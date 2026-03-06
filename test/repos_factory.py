"""Factory for generating .repos files used in tests."""

import os

import yaml


def _dump(data: dict, path: str):
    """Write a YAML repos file."""
    with open(path, 'wb') as f:
        yaml.safe_dump(data, f, encoding='utf-8')


def _git_repo(url: str, version: str) -> dict:
    return {'type': 'git', 'url': url, 'version': version}


def generate_extends_repos(temp_dir: str, git_url: str, tag_hashes: dict) -> dict:
    """Generate all extends .repos files for inheritance testing.

    The generated files use `staged.repos` present in `temp_dir` as
    the base file that extension repos inherit from via `extends:`.

    Args:
        temp_dir: Path to the temporary directory that already contains
            `staged.repos`.
        git_url: file:// URL to the local staged git repository.
        tag_hashes: Dict mapping tag names ('1.1.3', '1.1.4', '1.1.5')
            to their commit hashes.

    Returns:
        Dict with paths to all generated repos files:
            - staged_extension
            - staged_extension_2
            - staged_multiple_extension
            - loop_base
            - loop_extension
    """
    paths = {}

    # staged_extension.repos — extends staged.repos, overrides with tag 1.1.3
    paths['staged_extension'] = os.path.join(temp_dir, 'staged_extension.repos')
    _dump(
        {
            'extends': 'staged.repos',
            'repositories': {
                'immutable/hash': _git_repo(git_url, tag_hashes['1.1.3']),
                'immutable/tag': _git_repo(git_url, 'tags/1.1.3'),
                'vcs2l': _git_repo(git_url, '1.1.3'),
            },
        },
        paths['staged_extension'],
    )

    # staged_extension_2.repos — extends staged.repos, overrides with tag 1.1.4
    paths['staged_extension_2'] = os.path.join(temp_dir, 'staged_extension_2.repos')
    _dump(
        {
            'extends': 'staged.repos',
            'repositories': {
                'immutable/hash': _git_repo(git_url, tag_hashes['1.1.4']),
                'immutable/tag': _git_repo(git_url, 'tags/1.1.4'),
                'vcs2l': _git_repo(git_url, '1.1.4'),
            },
        },
        paths['staged_extension_2'],
    )

    # staged_multiple_extension.repos — extends both extensions
    paths['staged_multiple_extension'] = os.path.join(
        temp_dir, 'staged_multiple_extension.repos'
    )
    _dump(
        {
            'extends': [
                'staged_extension.repos',
                'staged_extension_2.repos',
            ],
            'repositories': {
                'immutable/tag': _git_repo(git_url, 'tags/1.1.5'),
                'vcs2l': _git_repo(git_url, 'heads/main'),
            },
        },
        paths['staged_multiple_extension'],
    )

    # loop_extension.repos / loop_base.repos — circular import pair
    paths['loop_extension'] = os.path.join(temp_dir, 'loop_extension.repos')
    _dump(
        {
            'extends': 'loop_base.repos',
            'repositories': {
                'vcs2l': _git_repo(git_url, '1.1.3'),
            },
        },
        paths['loop_extension'],
    )

    paths['loop_base'] = os.path.join(temp_dir, 'loop_base.repos')
    _dump(
        {
            'extends': 'loop_extension.repos',
            'repositories': {
                'vcs2l': _git_repo(git_url, 'heads/main'),
                'immutable/tag': _git_repo(git_url, 'tags/1.1.3'),
            },
        },
        paths['loop_base'],
    )

    return paths
