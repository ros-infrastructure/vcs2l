import argparse
import os
from shutil import which
import sys
import urllib.request as request

from vcs2l import __version__ as vcs2l_version
from vcs2l.clients import vcs2l_clients
from vcs2l.clients.vcs_base import run_command
from vcs2l.executor import ansi
from vcs2l.executor import execute_jobs
from vcs2l.executor import output_repositories
from vcs2l.executor import output_results
from vcs2l.streams import set_streams
import yaml

from .command import add_common_arguments
from .command import Command


class ImportCommand(Command):

    command = 'import'
    help = 'Import the list of repositories'

    def __init__(
        self, args, url, version=None, recursive=False, shallow=False
    ):
        super(ImportCommand, self).__init__(args)
        self.url = url
        self.version = version
        self.force = args.force
        self.retry = args.retry
        self.skip_existing = args.skip_existing
        self.recursive = recursive
        self.shallow = shallow


def get_parser():
    parser = argparse.ArgumentParser(
        description='Import the list of repositories', prog='vcs import')
    group = parser.add_argument_group('"import" command parameters')
    group.add_argument(
        '--input', type=file_or_url_type, default='-',
        help='Where to read YAML from', metavar='FILE_OR_URL')
    group.add_argument(
        '--force', action='store_true', default=False,
        help="Delete existing directories if they don't contain the "
             'repository being imported')
    group.add_argument(
        '--shallow', action='store_true', default=False,
        help='Create a shallow clone without a history')
    group.add_argument(
        '--recursive', action='store_true', default=False,
        help='Recurse into submodules')
    group.add_argument(
        '--retry', type=int, metavar='N', default=2,
        help='Retry commands requiring network access N times on failure')
    group.add_argument(
        '--skip-existing', action='store_true', default=False,
        help="Don't overwrite existing directories or change custom checkouts "
             'in repos using the same URL (but fetch repos with same URL)')

    return parser


def file_or_url_type(value):
    if os.path.exists(value) or '://' not in value:
        return argparse.FileType('r')(value)
    # use another user agent to avoid getting a 403 (forbidden) error,
    # since some websites blacklist or block unrecognized user agents
    return request.Request(
        value, headers={'User-Agent': 'vcs2l/' + vcs2l_version})


def get_repositories(yaml_file):
    try:
        root = yaml.safe_load(yaml_file)
    except yaml.YAMLError as e:
        raise RuntimeError('Input data is not valid yaml format: %s' % e)

    try:
        repositories = root['repositories']
        return get_repos_in_vcs2l_format(repositories)
    except KeyError as e:
        raise RuntimeError('Input data is not valid format: %s' % e)
    except TypeError as e:
        # try rosinstall file format
        try:
            return get_repos_in_rosinstall_format(root)
        except Exception:
            raise RuntimeError('Input data is not valid format: %s' % e)


def get_repos_in_vcs2l_format(repositories):
    repos = {}
    if repositories is None:
        print(
            ansi('yellowf') + 'List of repositories is empty' + ansi('reset'),
            file=sys.stderr)
        return repos
    for path in repositories:
        repo = {}
        attributes = repositories[path]
        try:
            repo['type'] = attributes['type']
            repo['url'] = attributes['url']
            if 'version' in attributes:
                repo['version'] = attributes['version']
        except KeyError as e:
            print(
                ansi('yellowf') + (
                    "Repository '%s' does not provide the necessary "
                    'information: %s' % (path, e)) + ansi('reset'),
                file=sys.stderr)
            continue
        repos[path] = repo
    return repos


def get_repos_in_rosinstall_format(root):
    repos = {}
    for i, item in enumerate(root):
        if len(item.keys()) != 1:
            raise RuntimeError('Input data is not valid format')
        repo = {'type': list(item.keys())[0]}
        attributes = list(item.values())[0]
        try:
            path = attributes['local-name']
        except KeyError as e:
            print(
                ansi('yellowf') + (
                    'Repository #%d does not provide the necessary '
                    'information: %s' % (i, e)) + ansi('reset'),
                file=sys.stderr)
            continue
        try:
            repo['url'] = attributes['uri']
            if 'version' in attributes:
                repo['version'] = attributes['version']
        except KeyError as e:
            print(
                ansi('yellowf') + (
                    "Repository '%s' does not provide the necessary "
                    'information: %s' % (path, e)) + ansi('reset'),
                file=sys.stderr)
            continue
        repos[path] = repo
    return repos


def generate_jobs(repos, args):
    jobs = []
    for path, repo in repos.items():
        path = os.path.join(args.path, path)
        clients = [c for c in vcs2l_clients if c.type == repo['type']]
        if not clients:
            from vcs2l.clients.none import NoneClient
            job = {
                'client': NoneClient(path),
                'command': None,
                'cwd': path,
                'output':
                    "Repository type '%s' is not supported" % repo['type'],
                'returncode': NotImplemented
            }
            jobs.append(job)
            continue

        client = clients[0](path)
        command = ImportCommand(
            args, repo['url'],
            str(repo['version']) if 'version' in repo else None,
            recursive=args.recursive, shallow=args.shallow)
        job = {'client': client, 'command': command}
        jobs.append(job)
    return jobs


def add_dependencies(jobs):
    paths = [job['client'].path for job in jobs]
    for job in jobs:
        job['depends'] = set()
        path = job['client'].path
        while True:
            parent_path = os.path.dirname(path)
            if parent_path == path:
                break
            path = parent_path
            if path in paths:
                job['depends'].add(path)


def main(args=None, stdout=None, stderr=None):
    set_streams(stdout=stdout, stderr=stderr)

    parser = get_parser()
    add_common_arguments(
        parser, skip_hide_empty=True, skip_nested=True, path_nargs='?',
        path_help='Base path to clone repositories to')
    args = parser.parse_args(args)
    try:
        input_ = args.input
        if isinstance(input_, request.Request):
            input_ = request.urlopen(input_)
        repos = get_repositories(input_)
    except (RuntimeError, request.URLError) as e:
        print(ansi('redf') + str(e) + ansi('reset'), file=sys.stderr)
        return 1
    jobs = generate_jobs(repos, args)
    add_dependencies(jobs)

    if args.repos:
        output_repositories([job['client'] for job in jobs])

    workers = args.workers
    # for ssh URLs check if the host is known to prevent ssh asking for
    # confirmation when using more than one worker
    if workers > 1:
        ssh_keygen = None
        checked_hosts = set()
        for job in list(jobs):
            if job['command'] is None:
                continue
            url = job['command'].url
            # only check the host from a ssh URL
            if not url.startswith('git@') or ':' not in url:
                continue
            host = url[4:].split(':', 1)[0]

            # only check each host name once
            if host in checked_hosts:
                continue
            checked_hosts.add(host)

            # get ssh-keygen path once
            if ssh_keygen is None:
                ssh_keygen = which('ssh-keygen') or False
            if not ssh_keygen:
                continue

            result = run_command([ssh_keygen, '-F', host], '')
            if result['returncode']:
                print(
                    'At least one hostname (%s) is unknown, switching to a '
                    'single worker to allow interactively answering the ssh '
                    'question to confirm the fingerprint' % host)
                workers = 1
                break

    results = execute_jobs(
        jobs, show_progress=True, number_of_workers=workers,
        debug_jobs=args.debug)
    output_results(results)

    any_error = any(r['returncode'] for r in results)
    return 1 if any_error else 0


if __name__ == '__main__':
    sys.exit(main())
