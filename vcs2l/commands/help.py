import argparse
import sys

from vcs2l import __version__
from vcs2l.clients import vcs2l_clients
from vcs2l.commands import vcs2l_commands
from vcs2l.errors import UnsupportedPythonVersionError
from vcs2l.streams import set_streams

if sys.version_info >= (3, 8):
    from importlib.metadata import entry_points
elif sys.version_info >= (3, 7):
    from importlib_metadata import entry_points
elif sys.version_info >= (3, 5):
    from pkg_resources import load_entry_point
else:
    raise UnsupportedPythonVersionError()


def main(args=None, stdout=None, stderr=None):
    set_streams(stdout=stdout, stderr=stderr)

    # no help to extract command first (which might be followed by --help)
    parser = get_parser(add_help=False)
    ns, _ = parser.parse_known_args(args)

    # help for a specific command
    if ns.command:
        # relay help request foe specific command
        entrypoint = get_entrypoint(ns.command)
        if not entrypoint:
            return 1
        return entrypoint(['--help'])

    # regular parsing validating options and arguments
    parser = get_parser()
    ns = parser.parse_args(args)

    if ns.clients:
        print('The available VCS clients are:')
        for client in vcs2l_clients:
            print('  ' + client.type)
        return 0

    if ns.commands:
        print(' '.join([cmd.command for cmd in vcs2l_commands]))
        return 0

    if ns.commands_descriptions:
        print(
            '\n'.join(
                ['{}\t{}'.format(cmd.command, cmd.help) for cmd in vcs2l_commands]
            )
        )
        return 0

    # output detailed command list
    parser = get_parser_with_command_only()
    parser.print_help()
    return 0


def get_parser(add_help=True):
    parser = argparse.ArgumentParser(
        prog='vcs',
        description=_get_description(),
        epilog=_get_epilog(),
        add_help=add_help,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        'command',
        metavar='<command>',
        nargs='?',
        help='The available commands: '
        + ', '.join([cmd.command for cmd in vcs2l_commands]),
    )
    group.add_argument(
        '--clients',
        action='store_true',
        default=False,
        help='Show the available VCS clients',
    )
    group.add_argument(
        '--commands',
        action='store_true',
        default=False,
        help='Output the available commands for auto-completion',
    )
    group.add_argument(
        '--commands-descriptions',
        action='store_true',
        default=False,
        help='Output the available commands along with their descriptions',
    )

    group.add_argument(
        '--version',
        action='version',
        version='%(prog)s ' + __version__,
        help='Show the vcs2l version',
    )
    return parser


def get_entrypoint(command):
    # accept command with same prefix if unique
    commands = [cmd.command for cmd in vcs2l_commands]
    commands = [cmd for cmd in commands if cmd.startswith(command)]
    if len(commands) != 1:
        print(
            "vcs: '%s' is not a vcs command. See 'vcs help'." % command, file=sys.stderr
        )
        if commands:
            print(
                '\nDid you mean one of these?\n' + '\n   '.join(commands),
                file=sys.stderr,
            )
        return None

    ep_name = 'vcs-' + commands[0]

    if sys.version_info >= (3, 10):
        eps = entry_points()
        entry_point = next(iter(eps.select(group='console_scripts', name=ep_name)))
        if entry_point:
            return entry_point.load()

    elif sys.version_info >= (3, 7):
        eps = entry_points()
        for ep in eps.get('console_scripts', []):
            if ep.name == ep_name:
                return ep.load()

    elif sys.version_info >= (3, 5):
        return load_entry_point('vcs2l', 'console_scripts', ep_name)

    else:
        raise UnsupportedPythonVersionError()

    return None


def get_parser_with_command_only():
    parser = argparse.ArgumentParser(
        prog='vcs',
        usage='%(prog)s <command>',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='%s\n\n%s'
        % (_get_description(), '\n'.join(_get_command_help(vcs2l_commands))),
        epilog=_get_epilog(),
        add_help=False,
    )
    parser.add_argument('command', help=argparse.SUPPRESS)
    return parser


def _get_description():
    return (
        'Most commands take directory arguments, '
        'recursively searching for repositories\n'
        'in these directories.  '
        'If no arguments are supplied to a command, it recurses\n'
        'on the current directory (inclusive) by default.'
    )


def _get_epilog():
    return "See '%(prog)s <command> --help' for more information on a specific command."


def _get_command_help(commands):
    lines = ['The available commands are:']
    max_len = max(len(cmd.command) for cmd in commands)
    for cmd in vcs2l_commands:
        lines.append(
            '   %s%s   %s' % (cmd.command, ' ' * (max_len - len(cmd.command)), cmd.help)
        )
    return lines


if __name__ == '__main__':
    sys.exit(main())
