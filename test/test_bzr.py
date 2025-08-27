"""Integration tests for BzrClient class."""

import os
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


if __name__ == '__main__':
    unittest.main()
