"""Utilities for vcs2l tests."""

import os
import subprocess


def assert_base_repos_imported(workdir: str):
    """Assert that the base repos from staged.repos exist in workdir."""
    assert os.path.isdir(os.path.join(workdir, 'immutable', 'hash_tar'))
    assert os.path.isdir(os.path.join(workdir, 'immutable', 'hash_zip'))
    assert os.path.isdir(os.path.join(workdir, 'without_version'))


def assert_git_at_commit(repo_dir: str, expected_hash: str):
    """Assert that a git repo's HEAD is at the expected commit hash."""
    actual = (
        subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repo_dir,
            stderr=subprocess.STDOUT,
        )
        .decode()
        .strip()
    )
    assert actual == expected_hash, f'Expected {expected_hash}, got {actual}'


def assert_git_at_tag(repo_dir: str, expected_tag: str):
    """Assert that a git repo's HEAD is at the expected tag."""
    actual = (
        subprocess.check_output(
            ['git', 'describe', '--tags', '--exact-match'],
            cwd=repo_dir,
            stderr=subprocess.STDOUT,
        )
        .decode()
        .strip()
    )
    assert actual == expected_tag, f'Expected tag {expected_tag}, got {actual}'
