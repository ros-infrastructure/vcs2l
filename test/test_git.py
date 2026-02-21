"""Tests for Git Client."""

import os
import tarfile
import unittest
from tempfile import TemporaryDirectory

from vcs2l.clients.git import GitClient

from . import StagedReposFile, to_file_url


class TestGitCheckout(StagedReposFile):
    """Test GitClient.checkout using the staged git repository."""

    def test_default_branch(self):
        """Checkout without a version gets the default branch."""
        with TemporaryDirectory(suffix='.git_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = GitClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'gitrepo'))

            result = client.checkout(url)
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(os.path.join(dest, '.git')))

    def test_specific_branch(self):
        """Checkout the main branch by name."""
        with TemporaryDirectory(suffix='.git_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = GitClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'gitrepo'))

            result = client.checkout(url, version='main')
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(os.path.join(dest, '.git')))

    def test_specific_hash(self):
        """Checkout a specific commit hash."""
        with TemporaryDirectory(suffix='.git_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = GitClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'gitrepo'))

            result = client.checkout(url, version='0.1.26')
            self.assertTrue(result)

    def test_nonempty_dir(self):
        """Checkout into a non-empty directory should return False."""
        with TemporaryDirectory(suffix='.git_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            os.makedirs(dest)
            # Place a file so the directory is non-empty
            with open(os.path.join(dest, 'blocker.txt'), 'w', encoding='utf-8') as f:
                f.write('occupied')

            client = GitClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'gitrepo'))

            result = client.checkout(url)
            self.assertFalse(result)

    def test_invalid_version(self):
        """Checkout with a non-existent version should return False."""
        with TemporaryDirectory(suffix='.git_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = GitClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'gitrepo'))

            result = client.checkout(url, version='nonexistent-branch-xyz')
            self.assertFalse(result)


class TestGitExportRepository(StagedReposFile):
    """Test GitClient.export_repository using the staged git repository."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Clone the staged repo so we have a working git directory
        cls._clone_dir = TemporaryDirectory(suffix='.git_export')
        cls._clone_path = os.path.join(cls._clone_dir.name, 'repo')
        client = GitClient(cls._clone_path)
        url = to_file_url(os.path.join(cls.temp_dir.name, 'gitrepo'))
        assert client.checkout(url, version='0.1.27'), 'Failed to clone staged repo'

    @classmethod
    def tearDownClass(cls):
        cls._clone_dir.cleanup()
        super().tearDownClass()

    def test_creates_tarball(self):
        """export_repository should create a .tar.gz archive."""
        with TemporaryDirectory(suffix='.git_export_out') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = GitClient(self._clone_path)

            result = client.export_repository('HEAD', basepath)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(basepath + '.tar.gz'))

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(len(names) > 0)

    def test_at_tag(self):
        """export_repository at a specific tag should succeed."""
        with TemporaryDirectory(suffix='.git_export_out') as tmp:
            basepath = os.path.join(tmp, 'export_tag')
            client = GitClient(self._clone_path)

            result = client.export_repository('0.1.27', basepath)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(basepath + '.tar.gz'))

    def test_invalid_version(self):
        """export_repository with a bad ref should return False."""
        with TemporaryDirectory(suffix='.git_export_out') as tmp:
            basepath = os.path.join(tmp, 'export_bad')
            client = GitClient(self._clone_path)

            result = client.export_repository('nonexistent-ref-xyz', basepath)
            self.assertFalse(result)

    def test_contains_license(self):
        """Exported archive at a tag after LICENSE merge should contain LICENSE."""
        with TemporaryDirectory(suffix='.git_export_out') as tmp:
            basepath = os.path.join(tmp, 'export_license')
            client = GitClient(self._clone_path)

            result = client.export_repository('0.1.27', basepath)
            self.assertTrue(result)

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(
                    any('LICENSE' in n for n in names),
                    f'LICENSE not found in archive: {names}',
                )


if __name__ == '__main__':
    unittest.main()
