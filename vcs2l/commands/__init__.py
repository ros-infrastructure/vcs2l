from .branch import BranchCommand
from .custom import CustomCommand
from .delete import DeleteCommand
from .diff import DiffCommand
from .export import ExportCommand
from .import_ import ImportCommand
from .log import LogCommand
from .pull import PullCommand
from .push import PushCommand
from .remotes import RemotesCommand
from .status import StatusCommand
from .validate import ValidateCommand

vcs2l_commands = []
vcs2l_commands.append(BranchCommand)
vcs2l_commands.append(CustomCommand)
vcs2l_commands.append(DeleteCommand)
vcs2l_commands.append(DiffCommand)
vcs2l_commands.append(ExportCommand)
vcs2l_commands.append(ImportCommand)
vcs2l_commands.append(LogCommand)
vcs2l_commands.append(PullCommand)
vcs2l_commands.append(PushCommand)
vcs2l_commands.append(RemotesCommand)
vcs2l_commands.append(StatusCommand)
vcs2l_commands.append(ValidateCommand)

_commands = [c.command for c in vcs2l_commands]
if len(_commands) != len(set(_commands)):
    raise RuntimeError(
        'Multiple commands share the same command name: ' + ', '.join(sorted(_commands))
    )
