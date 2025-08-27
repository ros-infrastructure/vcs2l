"""Integration tests for BzrClient class."""

import os
import tarfile
import tempfile
import unittest

from vcs2l.clients.bzr import BzrClient
from vcs2l.util import rmtree


class TestCheckout(unittest.TestCase):
    """Simple integration tests for BzrClient checkout functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.repo_link = 'https://github.com/octocat/Hello-World.git'
        self.repo_path = os.path.join(self.test_dir, 'test_repo')

    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)

    def test_checkout_repository(self):
        """Test checkout with a valid repository URL."""
        client = BzrClient(self.repo_path)
        result = client.checkout(self.repo_link)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.repo_path))

    def test_checkout_invalid_url(self):
        """Test checkout with invalid URL raises ValueError."""
        client = BzrClient(self.repo_path)

        with self.assertRaises(ValueError):
            client.checkout(None)

        with self.assertRaises(ValueError):
            client.checkout('')

    def test_checkout_existing_directory_fails(self):
        """Test checkout fails when directory already exists with content."""
        # Create the target directory and put a file in it
        os.makedirs(self.repo_path, exist_ok=True)
        test_file = os.path.join(self.repo_path, 'existing_file.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('This file already exists')

        client = BzrClient(self.repo_path)

        with self.assertRaises(RuntimeError) as context:
            client.checkout(self.repo_link)

        # Verify the error message mentions the path
        self.assertIn(self.repo_path, str(context.exception))
        self.assertIn('Target path exists and is not empty', str(context.exception))


class TestExportRepository(unittest.TestCase):
    """Integration tests for BzrClient _export_repository functionality."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.repo_path = os.path.join(self.test_dir, 'test_repo')
        self.export_path = os.path.join(self.test_dir, 'export_test')
        self.client = BzrClient(self.repo_path)
        # Use a git repository instead of launchpad for future-proofing
        self.repo_url = 'https://github.com/octocat/Hello-World.git'

    def tearDown(self):
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)

    def test_export_repository(self):
        """Test export repository."""
        self.client.checkout(self.repo_url)

        # Change to the repository directory for export
        original_cwd = os.getcwd()
        try:
            os.chdir(self.repo_path)

            # Test export with a specific revision
            result = self.client._export_repository(None, self.export_path)
            self.assertTrue(result, 'Export should return True on success')

            archive_path = self.export_path + '.tar.gz'
            self.assertTrue(
                os.path.exists(archive_path), 'Archive file should be created'
            )

            # Verify the archive is a valid tar.gz file
            with tarfile.open(archive_path, 'r:gz') as tar:
                members = tar.getnames()
                self.assertGreater(len(members), 0, 'Archive should contain files')

        finally:
            os.chdir(original_cwd)

    def test_export_repository_git_version_unsupported(self):
        """Test export repository with unsupported version for git repo."""
        self.client.checkout(self.repo_url)

        # Change to the repository directory for export
        original_cwd = os.getcwd()
        try:
            os.chdir(self.repo_path)

            # Test export with invalid version
            result = self.client._export_repository('999999999', self.export_path)
            self.assertFalse(result, 'Version is not supported for git repositories.')

            archive_path = self.export_path + '.tar.gz'
            self.assertFalse(
                os.path.exists(archive_path), 'Archive should not be created on failure'
            )
        finally:
            os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
