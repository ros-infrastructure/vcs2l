"""Integration tests for SvnClient class."""

import os
import subprocess
import tarfile
import tempfile
import unittest
from shutil import which

from vcs2l.clients.svn import SvnClient
from vcs2l.util import rmtree

svn = which('svn')


@unittest.skipIf(not svn, '`svn` was not found')
class TestCheckout(unittest.TestCase):
    """Test cases for SvnClient checkout method."""

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp(prefix='svn_test_')
        self.repo_url = 'https://svn.apache.org/repos/asf/abdera/abdera2/'
        self.client = SvnClient(self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)

    def test_checkout_version(self):
        """Test checkout repository with specific revision"""
        version = '1928014'  # Specific revision number

        result = self.client.checkout(self.repo_url, version=version)

        self.assertTrue(result, 'Checkout with specific version should succeed')

        # Verify that .svn directory exists
        svn_dir = os.path.join(self.test_dir, '.svn')
        self.assertTrue(
            os.path.exists(svn_dir), '.svn directory should exist after checkout'
        )

        # Verify the checked out revision (using svn info)
        try:
            result = subprocess.run(
                ['svn', 'info', '--show-item', 'revision'],
                check=True,
                cwd=self.test_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                actual_revision = result.stdout.strip()
                self.assertEqual(
                    actual_revision,
                    version,
                    f'Checked out revision should be {version}, got {actual_revision}',
                )
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            self.fail('Failed to run svn info to verify revision')

    def test_invalid_version(self):
        """Test that checkout fails with invalid revision number"""
        invalid_version = '999999999'

        result = self.client.checkout(self.repo_url, version=invalid_version)

        self.assertFalse(result, 'Checkout with invalid revision should fail')

    def test_existing_non_empty_dir_should_fail(self):
        """Test that checkout fails if target directory is not empty"""
        # Create a file in the test directory first
        test_file = os.path.join(self.test_dir, 'existing_file.txt')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write('This file already exists')

        with self.assertRaises(RuntimeError) as context:
            self.client.checkout(self.repo_url)

        self.assertIn('Target path exists and is not empty', str(context.exception))


@unittest.skipIf(not svn, '`svn` was not found')
class TestSvnExportRepository(unittest.TestCase):
    """Integration tests for SvnClient _export_repository functionality."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.repo_url = 'https://svn.apache.org/repos/asf/abdera/abdera2/'
        self.repo_path = os.path.join(self.test_dir, 'test_repo')
        self.export_path = os.path.join(self.test_dir, 'export_test')

    def tearDown(self):
        if os.path.exists(self.test_dir):
            rmtree(self.test_dir)

    def test_export_repository_with_version(self):
        """Test export repository with specific version."""
        client = SvnClient(self.repo_path)
        client.checkout(self.repo_url)

        # Change to the repository directory for export
        original_cwd = os.getcwd()
        try:
            os.chdir(self.repo_path)

            result = client._export_repository('1928014', self.export_path)
            self.assertTrue(result, 'Export should return True on success')

            # Verify tar.gz file was created
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

    def test_export_repository_invalid_version(self):
        """Test export repository with invalid version returns False."""
        client = SvnClient(self.repo_path)
        client.checkout(self.repo_url)

        original_cwd = os.getcwd()
        try:
            os.chdir(self.repo_path)

            result = client._export_repository('999999999', self.export_path)
            self.assertFalse(result, 'Export should return False for invalid version')

            archive_path = self.export_path + '.tar.gz'
            self.assertFalse(
                os.path.exists(archive_path), 'Archive should not be created on failure'
            )

        finally:
            os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()
