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


def get_vcs_client(vcs_type, uri):
    """
    Get a VCS client instance for the specified type and URI.

    Args:
        vcs_type: The type of VCS (e.g., 'git', 'svn', 'hg', etc.)
        uri: The repository URI/path

    Returns:
        An instance of the appropriate VCS client

    Raises:
        ValueError: If no client supports the specified type
    """
    for client_class in vcs2l_clients:
        if client_class.type == vcs_type:
            return client_class(uri)

    raise ValueError(f'No VCS client found for type: {vcs_type}')
