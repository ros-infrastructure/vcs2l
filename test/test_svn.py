"""Tests for SvnClient."""

import os
import tarfile
import unittest
from tempfile import TemporaryDirectory

from vcs2l.clients.svn import SvnClient

from . import StagedReposFile2, to_file_url


class TestSvnCheckout(StagedReposFile2):
    """Test SvnClient.checkout using the staged svn repository."""

    def test_default_branch(self):
        """Checkout without a version gets the latest revision."""
        with TemporaryDirectory(suffix='.svn_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = SvnClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'svnrepo'))

            result = client.checkout(url)
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(os.path.join(dest, '.svn')))

    def test_specific_hash(self):
        """Checkout at revision 1."""
        with TemporaryDirectory(suffix='.svn_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = SvnClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'svnrepo'))

            result = client.checkout(url, version='1')
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(os.path.join(dest, '.svn')))
            # LICENSE was committed at rev 1
            self.assertTrue(os.path.isfile(os.path.join(dest, 'LICENSE')))

    def test_nonempty_dir(self):
        """Checkout into a non-empty directory should raise RuntimeError."""
        with TemporaryDirectory(suffix='.svn_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            os.makedirs(dest)
            with open(os.path.join(dest, 'blocker.txt'), 'w', encoding='utf-8') as f:
                f.write('occupied')

            client = SvnClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'svnrepo'))

            with self.assertRaises(RuntimeError):
                client.checkout(url)

    def test_invalid_version(self):
        """Checkout with a non-existent revision should return False."""
        with TemporaryDirectory(suffix='.svn_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = SvnClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'svnrepo'))

            result = client.checkout(url, version='9999')
            self.assertFalse(result)

    def test_invalid_url(self):
        """Checkout from a non-existent local repository should return False."""
        with TemporaryDirectory(suffix='.svn_checkout') as tmp:
            dest = os.path.join(tmp, 'repo')
            client = SvnClient(dest)
            url = to_file_url(os.path.join(self.temp_dir.name, 'does-not-exist'))

            result = client.checkout(url)
            self.assertFalse(result)


class TestSvnExportRepository(StagedReposFile2):
    """Test SvnClient.export_repository using the staged svn repository."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._export_dir = TemporaryDirectory(suffix='.svn_export')
        cls._export_path = os.path.join(cls._export_dir.name, 'repo')
        client = SvnClient(cls._export_path)
        url = to_file_url(os.path.join(cls.temp_dir.name, 'svnrepo'))
        assert client.checkout(url, version='1'), 'Failed to checkout staged svn repo'

    @classmethod
    def tearDownClass(cls):
        cls._export_dir.cleanup()
        super().tearDownClass()

    def test_creates_tarball(self):
        """export_repository should create a .tar.gz archive."""
        with TemporaryDirectory(suffix='.svn_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = SvnClient(self._export_path)

            result = client.export_repository('1', basepath)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(basepath + '.tar.gz'))

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(len(names) > 0)

    def test_contains_license(self):
        """Exported archive should contain LICENSE."""
        with TemporaryDirectory(suffix='.svn_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = SvnClient(self._export_path)

            result = client.export_repository('1', basepath)
            self.assertTrue(result)

            with tarfile.open(basepath + '.tar.gz', 'r:gz') as tar:
                names = tar.getnames()
                self.assertTrue(
                    any('LICENSE' in n for n in names),
                    f'LICENSE not found in archive: {names}',
                )

    def test_invalid_version(self):
        """export_repository with a bad revision should return False."""
        with TemporaryDirectory(suffix='.svn_export') as tmp:
            basepath = os.path.join(tmp, 'export')
            client = SvnClient(self._export_path)

            result = client.export_repository('9999', basepath)
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
