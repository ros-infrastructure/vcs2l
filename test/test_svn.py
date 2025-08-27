"""Integration tests for SvnClient class."""

import os
import subprocess
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


if __name__ == '__main__':
    unittest.main()
