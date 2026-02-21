"""Tests for HgClient checkout and export_repository functionality."""

import os
import tarfile
import unittest
from tempfile import TemporaryDirectory

from vcs2l.clients.hg import HgClient

from . import StagedReposFile2, to_file_url


class TestHgCheckout(StagedReposFile2):
    """Test HgClient.checkout using the staged hg repository."""

    def test_default_branch(self):
        """Checkout without a version clones the entire repository."""
        with TemporaryDirectory(suffix='.hg_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = HgClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'hgrepo'))

            result = client.checkout(url)
            self.assertTrue(result)
            self.assertTrue(HgClient.is_repository(dest))

    def test_specific_branch(self):
        """Checkout a specific named branch."""
        with TemporaryDirectory(suffix='.hg_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = HgClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'hgrepo'))

            result = client.checkout(url, version='stable')
            self.assertTrue(result)
            self.assertTrue(HgClient.is_repository(dest))

    def test_specific_tag(self):
        """Checkout a specific tag."""
        with TemporaryDirectory(suffix='.hg_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = HgClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'hgrepo'))

            result = client.checkout(url, version='5.8')
            self.assertTrue(result)
            self.assertTrue(HgClient.is_repository(dest))

    def test_specific_hash(self):
        """Checkout a specific changeset hash."""
        with TemporaryDirectory(suffix='.hg_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = HgClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'hgrepo'))

            result = client.checkout(url, version='27ff6a32cacf')
            self.assertTrue(result)
            self.assertTrue(HgClient.is_repository(dest))

    def test_nonempty_dir(self):
        """Checkout into a non-empty directory should raise RuntimeError."""
        with TemporaryDirectory(suffix='.hg_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            os.makedirs(dest)
            with open(os.path.join(dest, 'blocker.txt'), 'w', encoding='utf-8') as f:
                f.write('occupied')

            client = HgClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'hgrepo'))

            with self.assertRaises(RuntimeError):
                client.checkout(url)

    def test_invalid_version(self):
        """Checkout with a non-existent revision should return False."""
        with TemporaryDirectory(suffix='.hg_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = HgClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'hgrepo'))

            result = client.checkout(url, version='nonexistent-rev-xyz')
            self.assertFalse(result)

    def test_invalid_url(self):
        """Checkout from a non-existent local repository should return False."""
        with TemporaryDirectory(suffix='.hg_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = HgClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'does-not-exist'))

            result = client.checkout(url)
            self.assertFalse(result)


class TestHgExportRepository(StagedReposFile2):
    """Test HgClient.export_repository using the staged hg repository."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._export_dir = TemporaryDirectory(suffix='.hg_export')
        cls._export_path = os.path.join(cls._export_dir.name, 'repo')
        client = HgClient(cls._export_path)
        url = to_file_url(os.path.join(cls.temp_dir.name, 'hgrepo'))
        assert client.checkout(url), 'Failed to clone staged hg repo'

    @classmethod
    def tearDownClass(cls):
        cls._export_dir.cleanup()
        super().tearDownClass()

    def test_creates_tarball(self):
        """export_repository should create a .tar.gz archive."""
        with TemporaryDirectory(suffix='.hg_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = HgClient(self._export_path)

            result = client.export_repository('5.8', basepath)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(basepath + '.tar.gz'))

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(len(names) > 0)

    def test_contains_license(self):
        """Exported archive should contain LICENSE."""
        with TemporaryDirectory(suffix='.hg_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = HgClient(self._export_path)

            result = client.export_repository('5.8', basepath)
            self.assertTrue(result)

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(
                    any('LICENSE' in n for n in names),
                    f'LICENSE not found in archive: {names}',
                )

    def test_invalid_version(self):
        """export_repository with a bad revision should return False."""
        with TemporaryDirectory(suffix='.hg_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = HgClient(self._export_path)

            result = client.export_repository('nonexistent-rev-xyz', basepath)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
