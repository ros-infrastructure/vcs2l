"""Integration tests for HgClient checkout functionality"""

import os
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


if __name__ == '__main__':
    unittest.main()
