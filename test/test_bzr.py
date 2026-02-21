"""Tests for BzrClient."""

import os
import tarfile
import unittest
from tempfile import TemporaryDirectory

from vcs2l.clients.bzr import BzrClient

from . import StagedReposFile2, to_file_url


class TestBzrCheckout(StagedReposFile2):
    """Test BzrClient.checkout using the staged bzr repository."""

    def test_default_branch(self):
        """Checkout without a version branches the entire repository."""
        with TemporaryDirectory(suffix='.bzr_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = BzrClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'bzrrepo'))

            result = client.checkout(url)
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(os.path.join(dest, '.bzr')))
            self.assertTrue(os.path.isfile(os.path.join(dest, 'LICENSE')))

    def test_specific_hash(self):
        """Checkout at revision 1."""
        with TemporaryDirectory(suffix='.bzr_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = BzrClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'bzrrepo'))

            result = client.checkout(url, version='1')
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(os.path.join(dest, '.bzr')))

    def test_nonempty_dir(self):
        """Checkout into a non-empty directory should raise RuntimeError."""
        with TemporaryDirectory(suffix='.bzr_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            os.makedirs(dest)
            with open(os.path.join(dest, 'blocker.txt'), 'w', encoding='utf-8') as f:
                f.write('occupied')

            client = BzrClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'bzrrepo'))

            with self.assertRaises(RuntimeError):
                client.checkout(url)


class TestBzrExportRepository(StagedReposFile2):
    """Test BzrClient.export_repository using the staged bzr repository."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._branch_dir = TemporaryDirectory(suffix='.bzr_export')
        cls._branch_path = os.path.join(cls._branch_dir.name, 'repo')
        client = BzrClient(cls._branch_path)
        url = to_file_url(os.path.join(cls.temp_dir.name, 'bzrrepo'))
        assert client.checkout(url), 'Failed to branch staged bzr repo'

    @classmethod
    def tearDownClass(cls):
        cls._branch_dir.cleanup()
        super().tearDownClass()

    def test_creates_tarball(self):
        """export_repository should create a .tar.gz archive."""
        with TemporaryDirectory(suffix='.bzr_export_out') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = BzrClient(self._branch_path)

            result = client.export_repository('1', basepath)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(basepath + '.tar.gz'))

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(len(names) > 0)

    def test_contains_license(self):
        """Exported archive should contain LICENSE."""
        with TemporaryDirectory(suffix='.bzr_export_out') as tmp:
            basepath = os.path.join(tmp, 'export_license')
            client = BzrClient(self._branch_path)

            result = client.export_repository('1', basepath)
            self.assertTrue(result)

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(
                    any('LICENSE' in n for n in names),
                    'LICENSE not found in archive: %s' % names,
                )

    def test_invalid_version(self):
        """export_repository with a bad revision should return False."""
        with TemporaryDirectory(suffix='.bzr_export_out') as tmp:
            basepath = os.path.join(tmp, 'export_bad')
            client = BzrClient(self._branch_path)

            result = client.export_repository('9999', basepath)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
