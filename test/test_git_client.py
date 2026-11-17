"""Tests for GitClient repository detection."""

import os
import subprocess
import unittest
from tempfile import TemporaryDirectory

from vcs2l.clients.git import GitClient
from vcs2l.crawler import find_repositories


def _git(*args, cwd):
    subprocess.check_call(
        ['git', *args],
        cwd=cwd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={
            **os.environ,
            'GIT_AUTHOR_NAME': 'vcs2l',
            'GIT_AUTHOR_EMAIL': 'vcs2l@example.com',
            'GIT_COMMITTER_NAME': 'vcs2l',
            'GIT_COMMITTER_EMAIL': 'vcs2l@example.com',
        },
    )


class TestGitIsRepository(unittest.TestCase):
    def setUp(self):
        self._temp = TemporaryDirectory()
        self.root = self._temp.name
        self.repo = os.path.join(self.root, 'repo')
        os.mkdir(self.repo)
        _git('init', '-q', cwd=self.repo)
        _git('commit', '-q', '--allow-empty', '-m', 'init', cwd=self.repo)

    def tearDown(self):
        self._temp.cleanup()

    def test_git_directory(self):
        self.assertTrue(GitClient.is_repository(self.repo))

    def test_git_file_of_linked_worktree(self):
        worktree = os.path.join(self.root, 'worktree')
        _git('worktree', 'add', '-q', worktree, cwd=self.repo)
        self.assertTrue(os.path.isfile(os.path.join(worktree, '.git')))
        self.assertTrue(GitClient.is_repository(worktree))

    def test_git_file_of_separate_git_dir(self):
        checkout = os.path.join(self.root, 'checkout')
        git_dir = os.path.join(self.root, 'checkout.git')
        _git(
            'clone',
            '-q',
            '--separate-git-dir',
            git_dir,
            self.repo,
            checkout,
            cwd=self.root,
        )
        self.assertTrue(os.path.isfile(os.path.join(checkout, '.git')))
        self.assertTrue(GitClient.is_repository(checkout))

    def test_not_a_repository(self):
        plain = os.path.join(self.root, 'plain')
        os.mkdir(plain)
        self.assertFalse(GitClient.is_repository(plain))

    def test_crawler_finds_linked_worktree(self):
        worktree = os.path.join(self.root, 'worktree')
        _git('worktree', 'add', '-q', worktree, cwd=self.repo)
        found = [client.path for client in find_repositories([self.root])]
        self.assertIn(worktree, found)


if __name__ == '__main__':
    unittest.main()
