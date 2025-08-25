"""Command to delete directories of repositories listed in a YAML file."""

import argparse
import os
import sys
import urllib.request as request
from urllib.error import URLError

from vcs2l.commands.import_ import file_or_url_type, get_repositories
from vcs2l.executor import ansi
from vcs2l.streams import set_streams
from vcs2l.util import rmtree

from .command import Command, existing_dir


class DeleteCommand(Command):
    """Delete directories of repositories listed in a YAML file."""

    command = 'delete'
    help = 'Remove the directories indicated by the list of given repositories.'


def get_parser():
    """CLI parser for the 'delete' command."""
    _cls = DeleteCommand

    parser = argparse.ArgumentParser(
        description=_cls.help, prog='vcs {}'.format(_cls.command)
    )
    group = parser.add_argument_group('Command parameters')
    group.add_argument(
        '--input',
        type=file_or_url_type,
        default='-',
        help='Where to read YAML from',
        metavar='FILE_OR_URL',
    )
    group.add_argument(
        'path',
        nargs='?',
        type=existing_dir,
        default=os.curdir,
        help='Base path to look for repositories',
    )
    group.add_argument(
        '-f',
        '--force',
        action='store_true',
        default=False,
        help='Do the deletion instead of a dry-run',
    )
    return parser


def get_repository_paths(input_source, base_path):
    """Get repository paths from input source."""
    try:
        if isinstance(input_source, request.Request):
            input_source = request.urlopen(input_source)
        repos = get_repositories(input_source)
        return [os.path.join(base_path, rel_path) for rel_path in repos]
    except (RuntimeError, URLError) as e:
        raise RuntimeError(f'Failed to read repositories: {e}') from e


def validate_paths(paths):
    """Validate that paths exist and are directories."""
    valid_paths = []
    missing_paths = []

    for path in paths:
        if os.path.exists(path) and os.path.isdir(path):
            valid_paths.append(path)
        else:
            missing_paths.append(path)

    return valid_paths, missing_paths


def main(args=None, stdout=None, stderr=None):
    """Entry point for the 'delete' command."""

    set_streams(stdout=stdout, stderr=stderr)
    parser = get_parser()
    args = parser.parse_args(args)

    try:
        paths = get_repository_paths(args.input, args.path)
    except RuntimeError as e:
        print(ansi('redf') + f'Error: {e}' + ansi('reset'), file=sys.stderr)
        return 1

    if not paths:
        print(
            ansi('yellowf') + 'No repositories found to delete' + ansi('reset'),
            file=sys.stderr,
        )
        return 0

    # Validate paths existence
    valid_paths, missing_paths = validate_paths(paths)

    if not valid_paths:
        print(
            ansi('redf') + 'No valid directories to delete.' + ansi('reset'),
            file=sys.stderr,
        )
        return 1
    else:
        if missing_paths:
            print(
                ansi('yellowf')
                + 'Warning: The following directories do not exist:'
                + ansi('reset'),
                file=sys.stderr,
            )
            for path in missing_paths:
                print(f'  {path}', file=sys.stderr)

        print(
            ansi('cyanf')
            + 'The following directories will be deleted:'
            + ansi('reset'),
            file=sys.stderr,
        )
        for path in valid_paths:
            print(f'  {path}', file=sys.stderr)

    if not args.force:
        print(
            ansi('yellowf')
            + 'Dry-run mode: No directories were deleted. Use -f/--force to delete them.'
            + ansi('reset'),
            file=sys.stderr,
        )
        return 0

    # Actual deletion
    for path in valid_paths:
        try:
            rmtree(path)
        except OSError as e:
            print(
                ansi('redf') + f'Failed to delete {path}: {e}' + ansi('reset'),
                file=sys.stderr,
            )


if __name__ == '__main__':
    sys.exit(main())
