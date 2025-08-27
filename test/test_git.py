"""Unit tests for GitClient checkout functionality"""

import os
import tarfile
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


class TestExportRepository(unittest.TestCase):
    """Test cases for GitClient export_repository method"""

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.test_dir, 'test_repo')
        self.export_dir = os.path.join(self.test_dir, 'exports')
        os.makedirs(self.export_dir, exist_ok=True)

        self.test_repo_url = 'https://github.com/octocat/Hello-World.git'
        self.client = GitClient(self.repo_path)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)

    def test_export_specific_branch(self):
        """Test exporting the repository at a specific branch"""
        success = self.client.checkout(self.test_repo_url, version='test')

        if not success:
            self.fail('Failed to clone test repository')

        basepath = os.path.join(self.export_dir, 'repo_export')
        filepath = self.client.export_repository('test', basepath)

        self.assertTrue(os.path.exists(filepath), 'Export file should exist')
        self.assertGreater(
            os.path.getsize(filepath), 0, 'Export file should not be empty'
        )
        # Verify it's a valid tar.gz file
        try:
            if filepath and isinstance(filepath, str):
                with tarfile.open(filepath, 'r:gz') as tar:
                    members = tar.getnames()
                    self.assertIn('README', members, 'Should contain README file')
            else:
                self.fail('Exported file path is invalid')
        except tarfile.ReadError:
            self.fail('Exported file should be a valid tar.gz archive')

    def test_export_with_local_changes_uses_temp_dir(self):
        """Test that export uses temp directory when there are local changes"""
        # First clone the repository
        success = self.client.checkout(self.test_repo_url)
        if not success:
            self.fail('Failed to clone test repository')

        # Create a local change
        test_file = os.path.join(self.repo_path, 'test_change.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('test change')

        basepath = os.path.join(self.export_dir, 'local_changes_test')
        filepath = self.client.export_repository(None, basepath)

        self.assertIsNotNone(filepath, 'Export should succeed even with local changes')
        self.assertTrue(os.path.exists(filepath), 'Export file should exist')
        self.assertGreater(
            os.path.getsize(filepath), 0, 'Export file should not be empty'
        )

        # Clean up
        os.remove(test_file)

    def test_export_invalid_branch(self):
        """Test exporting a non-existent branch should fail gracefully"""
        success = self.client.checkout(self.test_repo_url)

        if not success:
            self.fail('Failed to clone test repository')

        basepath = os.path.join(self.export_dir, 'nonexistent_export')
        result = self.client.export_repository('nonexistent-branch-12345', basepath)

        self.assertEqual(
            result, False, 'Export should return False for non-existent ref'
        )


if __name__ == '__main__':
    unittest.main()
