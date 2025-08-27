"""Unit tests for GitClient checkout functionality"""

import os
import tempfile
import unittest

from vcs2l.clients.git import GitClient
from vcs2l.util import rmtree


class TestCheckout(unittest.TestCase):
    """Test cases for GitClient checkout method"""

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.test_dir, 'test_repo')

    def tearDown(self):
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)

    def test_checkout_specific_branch(self):
        """Test checking out a specific branch"""
        client = GitClient(self.repo_path)

        url = 'https://github.com/octocat/Hello-World.git'
        success = client.checkout(url, version='test', shallow=True)

        self.assertTrue(success, 'Checkout should succeed')
        self.assertTrue(os.path.exists(self.repo_path), 'Repo directory should exist')
        self.assertTrue(
            os.path.isdir(os.path.join(self.repo_path, '.git')),
            'Should be a git repository',
        )

    def test_checkout_nonexistent_repo(self):
        """Test checking out a non-existent repository should fail"""
        client = GitClient(self.repo_path)

        url = 'https://github.com/this/repo/does/not/exist.git'
        success = client.checkout(url, verbose=True)

        self.assertFalse(success, 'Checkout should fail for non-existent repo')

    def test_checkout_to_existing_directory(self):
        """Test checking out to a non-empty directory should fail"""
        # Create a non-empty directory
        os.makedirs(self.repo_path)
        with open(
            os.path.join(self.repo_path, 'existing_file.txt'), 'w', encoding='utf-8'
        ) as f:
            f.write('This file already exists')

        client = GitClient(self.repo_path)
        url = 'https://github.com/octocat/Hello-World.git'
        success = client.checkout(url)

        self.assertFalse(success, 'Checkout should fail for non-empty directory')


if __name__ == '__main__':
    unittest.main()
