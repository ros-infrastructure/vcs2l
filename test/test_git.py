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

    def test_specific_tag(self):
        """Checkout a specific tag."""
        with TemporaryDirectory(suffix='.git_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = GitClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'gitrepo'))

            result = client.checkout(url, version='0.1.26')
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(os.path.join(dest, '.git')))

    def test_specific_hash(self):
        """Checkout a specific commit hash."""
        with TemporaryDirectory(suffix='.git_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = GitClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'gitrepo'))

            result = client.checkout(url, version=self._tag_hashes['1.1.3'])
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(os.path.join(dest, '.git')))

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

    def test_invalid_url(self):
        """Checkout from a non-existent local repository should return False."""
        with TemporaryDirectory(suffix='.git_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = GitClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'does-not-exist'))

            result = client.checkout(url)
            self.assertFalse(result)


class TestGitExportRepository(StagedReposFile):
    """Test GitClient.export_repository using the staged git repository."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Clone the staged repo so we have a working git directory
        cls._export_dir = TemporaryDirectory(suffix='.git_export')
        cls._export_path = os.path.join(cls._export_dir.name, 'repo')
        client = GitClient(cls._export_path)
        url = to_file_url(os.path.join(cls.temp_dir.name, 'gitrepo'))
        assert client.checkout(url, version='0.1.27'), 'Failed to clone staged repo'

    @classmethod
    def tearDownClass(cls):
        cls._export_dir.cleanup()
        super().tearDownClass()

    def test_creates_tarball(self):
        """export_repository should create a .tar.gz archive."""
        with TemporaryDirectory(suffix='.git_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = GitClient(self._export_path)

            result = client.export_repository('0.1.27', basepath)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(basepath + '.tar.gz'))

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(len(names) > 0)

    def test_contains_license(self):
        """Exported archive at a tag after LICENSE merge should contain LICENSE."""
        with TemporaryDirectory(suffix='.git_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = GitClient(self._export_path)

            result = client.export_repository('0.1.27', basepath)
            self.assertTrue(result)

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(
                    any('LICENSE' in n for n in names),
                    f'LICENSE not found in archive: {names}',
                )

    def test_invalid_version(self):
        """export_repository with a bad ref should return False."""
        with TemporaryDirectory(suffix='.git_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = GitClient(self._export_path)

            result = client.export_repository('nonexistent-branch-xyz', basepath)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
