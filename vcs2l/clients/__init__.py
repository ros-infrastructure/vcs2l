vcs2l_clients = []

try:
    from vcs2l.clients.bzr import BzrClient

    vcs2l_clients.append(BzrClient)
except ImportError:
    pass

try:
    from vcs2l.clients.git import GitClient

    vcs2l_clients.append(GitClient)
except ImportError:
    pass

try:
    from vcs2l.clients.hg import HgClient

    vcs2l_clients.append(HgClient)
except ImportError:
    pass

try:
    from vcs2l.clients.svn import SvnClient

    vcs2l_clients.append(SvnClient)
except ImportError:
    pass

try:
    from vcs2l.clients.tar import TarClient

    vcs2l_clients.append(TarClient)
except ImportError:
    pass

try:
    from vcs2l.clients.zip import ZipClient

    vcs2l_clients.append(ZipClient)
except ImportError:
    pass

_client_types = [c.type for c in vcs2l_clients]
if len(_client_types) != len(set(_client_types)):
    raise RuntimeError(
        'Multiple vcs clients share the same type: ' + ', '.join(sorted(_client_types))
    )
