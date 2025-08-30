"""Integration tests for HgClient checkout functionality"""

import os
import subprocess
import tempfile
import unittest
from shutil import which

from vcs2l.clients.hg import HgClient
from vcs2l.util import rmtree

hg = which('hg')


@unittest.skipIf(not hg, '`hg` was not found')
class TestCheckout(unittest.TestCase):
    """Test cases for HgClient checkout method."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.repo_url = 'https://www.mercurial-scm.org/repo/hello'
        self.repo_path = os.path.join(self.test_dir, 'test_repo')

    def tearDown(self):
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)

    def test_checkout_with_version(self):
        """Test checkout with a specific version/revision."""
        client = HgClient(self.repo_path)
        result = client.checkout(self.repo_url, version='1')

        self.assertTrue(result, 'Checkout with version should return True on success')
        self.assertTrue(
            os.path.exists(self.repo_path), 'Repository directory should be created'
        )
        self.assertTrue(
            HgClient.is_repository(self.repo_path),
            'Should create valid Mercurial repository',
        )

    def test_checkout_invalid_url(self):
        """Test checkout with an invalid URL."""
        client = HgClient(self.repo_path)
        result = client.checkout('https://invalid-url-for-testing.com/repo')

        self.assertFalse(result, 'Checkout with invalid URL should return False')

    def test_checkout_existing_directory(self):
        """Test checkout fails when directory already exists with content."""
        # Create the target directory and put a file in it
        os.makedirs(self.repo_path, exist_ok=True)
        test_file = os.path.join(self.repo_path, 'existing_file.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('This file already exists')

        client = HgClient(self.repo_path)
        result = client.checkout(self.repo_url)

        self.assertFalse(
            result, 'Checkout should return False when directory exists with content'
        )


@unittest.skipIf(not hg, '`hg` was not found')
class TestExportRepository(unittest.TestCase):
    """Integration tests for HgClient _export_repository functionality."""

    def setUp(self):
        """Set up test fixtures for each test"""
        self.test_dir = tempfile.mkdtemp(prefix='hg_test_')
        self.repo_path = os.path.join(self.test_dir, 'hello')
        self.export_base_path = os.path.join(self.test_dir, 'exported_repo')
        self.repo_url = 'https://www.mercurial-scm.org/repo/hello'

        self.hg_client = HgClient(self.repo_path)

        self._ensure_repo_cloned()

    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)

    def _ensure_repo_cloned(self):
        """Ensure the test repository is cloned locally"""
        if not os.path.exists(self.repo_path):
            try:
                subprocess.run(
                    ['hg', 'clone', '--rev', 'tip', self.repo_url, self.repo_path],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except subprocess.CalledProcessError as e:
                self.fail(f'Failed to clone repository: {e.stderr}')

    def test_export_repository_specific_revision(self):
        """Test exporting a specific revision"""
        result = self.hg_client._export_repository('1', self.export_base_path)
        self.assertTrue(result, "Export should succeed for revision '1'")

        # Verify files were created correctly
        tar_gz_path = self.export_base_path + '.tar.gz'
        self.assertTrue(os.path.exists(tar_gz_path))

    def test_export_repository_invalid_revision(self):
        """Test exporting with an invalid revision"""
        invalid_revision = 'nonexistent123456789'

        result = self.hg_client._export_repository(
            invalid_revision, self.export_base_path
        )
        self.assertFalse(result, 'Export should fail for invalid revision')

        tar_gz_path = self.export_base_path + '.tar.gz'
        tar_path = self.export_base_path + '.tar'
        self.assertFalse(os.path.exists(tar_gz_path))
        self.assertFalse(os.path.exists(tar_path))


if __name__ == '__main__':
    unittest.main()
