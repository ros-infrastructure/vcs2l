import copy
import os
from shutil import which

from vcs2l.clients.vcs_base import VcsClientBase
from vcs2l.util import rmtree


class BzrClient(VcsClientBase):
    type = 'bzr'
    _executable = None

    @staticmethod
    def is_repository(path):
        return os.path.isdir(os.path.join(path, '.bzr'))

    def __init__(self, path):
        super(BzrClient, self).__init__(path)

    def branch(self, command):
        if command.all:
            return self._not_applicable(
                command, message='at least with the option to list all branches'
            )

        self._check_executable()
        return self._get_parent_branch()

    def custom(self, command):
        self._check_executable()
        cmd = [BzrClient._executable] + command.args
        return self._run_command(cmd)

    def diff(self, _command):
        self._check_executable()
        cmd = [BzrClient._executable, 'diff']
        return self._run_command(cmd)

    def import_(self, command):
        if not command.url:
            return {
                'cmd': '',
                'cwd': self.path,
                'output': "Repository data lacks the 'url' value",
                'returncode': 1,
            }

        self._check_executable()
        if BzrClient.is_repository(self.path):
            # verify that existing repository is the same
            result_parent_branch = self._get_parent_branch()
            if result_parent_branch['returncode']:
                return result_parent_branch
            parent_branch = result_parent_branch['output']
            if parent_branch != command.url:
                if not command.force:
                    return {
                        'cmd': '',
                        'cwd': self.path,
                        'output': 'Path already exists and contains a different '
                        'repository',
                        'returncode': 1,
                    }
                try:
                    rmtree(self.path)
                except OSError:
                    os.remove(self.path)

        not_exist = self._create_path()
        if not_exist:
            return not_exist

        if BzrClient.is_repository(self.path):
            # pull updates for existing repo
            cmd_pull = [BzrClient._executable, 'pull']
            return self._run_command(cmd_pull, retry=command.retry)

        else:
            cmd_branch = [BzrClient._executable, 'branch']
            if command.version:
                cmd_branch += ['-r', command.version]
            cmd_branch += [command.url, '.']
            result_branch = self._run_command(cmd_branch, retry=command.retry)
            if result_branch['returncode']:
                result_branch['output'] = "Could not branch repository '%s': %s" % (
                    command.url,
                    result_branch['output'],
                )
                return result_branch
            return result_branch

    def log(self, command):
        self._check_executable()
        if command.limit_tag or command.limit_untagged:
            tag = None
            if command.limit_tag:
                tag = command.limit_tag
            else:
                # determine nearest tag
                cmd_tag = [BzrClient._executable, 'tags', '--sort=time']
                result_tag = self._run_command(cmd_tag)
                if result_tag['returncode']:
                    return result_tag
                for line in result_tag['output'].splitlines():
                    parts = line.split(' ', 2)
                    if parts[1] != '?':
                        tag = parts[0]
                if not tag:
                    result_tag['output'] = 'Could not determine latest tag'
                    result_tag['returncode'] = 1
                    return result_tag
            # determine revision number of tag
            cmd_tag_rev = [BzrClient._executable, 'revno', '--rev', 'tag:' + tag]
            result_tag_rev = self._run_command(cmd_tag_rev)
            if result_tag_rev['returncode']:
                if command.limit_tag:
                    result_tag_rev['output'] = "Repository lacks the tag '%s'" % tag
                return result_tag_rev
            try:
                tag_rev = int(result_tag_rev['output'])
                tag_next_rev = tag_rev + 1
            except ValueError:
                tag_rev = result_tag_rev['output']
                tag_next_rev = tag_rev
            # determine revision number of HEAD
            cmd_head_rev = [BzrClient._executable, 'revno']
            result_head_rev = self._run_command(cmd_head_rev)
            if result_head_rev['returncode']:
                return result_head_rev
            try:
                head_rev = int(result_head_rev['output'])
            except ValueError:
                head_rev = result_head_rev['output']
            # output log since nearest tag
            cmd_log = [
                BzrClient._executable,
                'log',
                '--rev',
                'revno:%s..' % str(tag_next_rev),
            ]
            if tag_rev == head_rev:
                return {
                    'cmd': ' '.join(cmd_log),
                    'cwd': self.path,
                    'output': '',
                    'returncode': 0,
                }
            if command.limit != 0:
                cmd_log += ['--limit', '%d' % command.limit]
            result_log = self._run_command(cmd_log)
            return result_log
        cmd = [BzrClient._executable, 'log']
        if command.limit != 0:
            cmd += ['--limit', '%d' % command.limit]
        return self._run_command(cmd)

    def pull(self, _command):
        self._check_executable()
        cmd = [BzrClient._executable, 'pull']
        return self._run_command(cmd)

    def push(self, _command):
        self._check_executable()
        cmd = [BzrClient._executable, 'push']
        return self._run_command(cmd)

    def remotes(self, _command):
        self._check_executable()
        return self._get_parent_branch()

    def status(self, _command):
        self._check_executable()
        cmd = [BzrClient._executable, 'status']
        return self._run_command(cmd)

    def _get_parent_branch(self):
        cmd = [BzrClient._executable, 'info']
        # parsing the text output requires enforcing language
        env = copy.copy(os.environ)
        env['LANG'] = 'en_US.UTF-8'
        result = self._run_command(cmd, env)
        if result['returncode']:
            return result
        branch = None
        prefix = '  parent branch: '
        for line in result['output'].splitlines():
            if line.startswith(prefix):
                branch = line[len(prefix) :]
                break
        if not branch:
            result['output'] = ('Could not determine parent branch',)
            result['returncode'] = 1
            return result
        result['output'] = branch
        return result

    def _export_repository(self, version, basepath):
        """Export the bzr repository at a given version to a tar.gz file."""
        self._check_executable()

        # Construct the bzr export command
        cmd = [BzrClient._executable, 'export', '--format=tgz', basepath + '.tar.gz']

        if version:
            cmd.append('--revision')
            cmd.append(version)

        result = self._run_command(cmd)

        return result['returncode'] == 0

    def checkout(self, url, version=None, verbose=False, shallow=False, timeout=None):
        """Creates a local Bazaar branch from a remote repository."""
        if url is None or url.strip() == '':
            raise ValueError('Invalid empty url: "%s"' % url)

        # Check if directory exists and is not empty
        if os.path.exists(self.path) and os.listdir(self.path):
            raise RuntimeError('Target path exists and is not empty: %s' % self.path)

        # Create parent directory if it doesn't exist, but not the target directory itself
        # This is because 'bzr branch' will create the target directory.
        parent_dir = os.path.dirname(self.path)
        if parent_dir and not os.path.exists(parent_dir):
            result = self._create_path()
            if result and result.get('returncode'):
                return False

        self._check_executable()

        # Build the branch command
        cmd = ['bzr', 'branch']

        if verbose:
            cmd.append('--verbose')

        if version:
            cmd.extend(['--revision', str(version)])

        # let bzr create the target directory
        cmd.extend([url, self.path])

        # Run the command with proper timeout handling
        try:
            result = self._run_command(cmd)
        except Exception as e:
            print('Branch command failed with exception: %s' % str(e))
            return False

        if result['returncode'] != 0:
            error_msg = result.get('output', 'Unknown error')
            print('Branch failed: %s' % error_msg)
            return False

        return True

    def _check_executable(self):
        assert BzrClient._executable is not None, "Could not find 'bzr' executable"


if not BzrClient._executable:
    BzrClient._executable = which('bzr')
