"""Fixtures and utilities for testing vcs2l."""

import os
import shutil
import subprocess
import tarfile
import unittest
import zipfile
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory

import yaml


def to_file_url(path):
    return Path(path).as_uri()


class StagedReposFile(unittest.TestCase):
    """Fixture for testing git, tar, and zip clients."""

    _git = which('git')
    _git_env = {
        **os.environ,
        'GIT_AUTHOR_NAME': 'vcs2l',
        'GIT_AUTHOR_DATE': '2005-01-01T00:00:00-06:00',
        'GIT_AUTHOR_EMAIL': 'vcs2l@example.com',
        'GIT_COMMITTER_NAME': 'vcs2l',
        'GIT_COMMITTER_DATE': '2005-01-01T00:00:00-06:00',
        'GIT_COMMITTER_EMAIL': 'vcs2l@example.com',
        'GIT_CONFIG_GLOBAL': os.path.join(os.path.dirname(__file__), '.gitconfig'),
        'LANG': 'en_US.UTF-8',
    }
    _commit_date = '2005-01-01T00:00:00'

    temp_dir = None
    repos_file_path = None

    @classmethod
    def setUpClass(cls):
        if not cls._git:
            raise unittest.SkipTest('`git` was not found')

        cls.temp_dir = TemporaryDirectory(suffix='.vcstmp')

        # Create the staged git repository
        gitrepo_path = os.path.join(cls.temp_dir.name, 'gitrepo')
        os.mkdir(gitrepo_path)
        shutil.copy(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'LICENSE'),
            gitrepo_path,
        )
        for command in (
            ('init', '--quiet', '.'),
            ('commit', '--quiet', '--allow-empty', '-m', '0.1.26'),
            ('tag', '0.1.26'),
            ('checkout', '--quiet', '-b', 'license'),
            ('add', 'LICENSE'),
            ('commit', '--quiet', '-m', 'Add LICENSE'),
            ('checkout', '--quiet', 'main'),
            ('merge', '--no-ff', '--quiet', 'license', '-m', "Merge branch 'license'"),
            ('branch', '--quiet', '-D', 'license'),
            ('commit', '--quiet', '--allow-empty', '-m', 'update changelog'),
            ('commit', '--quiet', '--allow-empty', '-m', '0.1.27'),
            ('tag', '0.1.27'),
            ('commit', '--quiet', '--allow-empty', '-m', "codin' codin' codin'"),
        ):
            subprocess.check_call(
                [
                    cls._git,
                    *command,
                ],
                cwd=gitrepo_path,
                env=cls._git_env,
            )

        # Create the archive stage
        archive_path = os.path.join(cls.temp_dir.name, 'archive_dir')
        os.mkdir(archive_path)
        with open(os.path.join(archive_path, 'file_name.txt'), 'wb') as f:
            f.write(b'Lorem Ipsum\n')

        # Create a tar file
        tarball_path = os.path.join(cls.temp_dir.name, 'archive.tar.gz')
        with tarfile.TarFile.open(tarball_path, 'w:gz') as f:
            f.add(archive_path, 'archive_dir')

        # Create a zip file
        zip_path = os.path.join(cls.temp_dir.name, 'archive.zip')
        with zipfile.ZipFile(zip_path, mode='w') as f:
            f.write(
                os.path.join(archive_path, 'file_name.txt'),
                os.path.join('archive_dir', 'file_name.txt'),
            )

        # Populate the staged.repos file
        repos = {
            'immutable/hash': {
                'type': 'git',
                'url': to_file_url(gitrepo_path),
                'version': '5b3504594f7354121cf024dc734bf79e270cffd3',
            },
            'immutable/hash_tar': {
                'type': 'tar',
                'url': to_file_url(tarball_path),
                'version': 'archive_dir',
            },
            'immutable/hash_zip': {
                'type': 'zip',
                'url': to_file_url(zip_path),
                'version': 'archive_dir',
            },
            'immutable/tag': {
                'type': 'git',
                'url': to_file_url(gitrepo_path),
                'version': 'tags/0.1.27',
            },
            'vcs2l': {
                'type': 'git',
                'url': to_file_url(gitrepo_path),
                'version': 'heads/main',
            },
            'without_version': {
                'type': 'git',
                'url': to_file_url(gitrepo_path),
            },
        }

        cls.repos_file_path = os.path.join(cls.temp_dir.name, 'staged.repos')
        with open(cls.repos_file_path, 'wb') as f:
            yaml.safe_dump({'repositories': repos}, f, encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.repos_file_path = None
        if cls.temp_dir:
            cls.temp_dir.cleanup()
        cls.temp_dir = None


class StagedReposFile2(unittest.TestCase):
    """Fixture for testing subversion and mercurial clients."""

    _svn = which('svn')
    _svnadmin = which('svnadmin')
    _hg = which('hg')
    _hg_env = {
        **os.environ,
        'HGUSER': 'vcs2l',
        'EMAIL': 'vcs2l@example.com',
    }
    _commit_date = '2005-01-01T00:00:00-06:00'

    temp_dir = None
    repos_file_path = None

    @classmethod
    def setUpClass(cls):
        if not cls._svn:
            raise unittest.SkipTest('`svn` was not found')
        if not cls._svnadmin:
            raise unittest.SkipTest('`svnadmin` was not found')
        if not cls._hg:
            raise unittest.SkipTest('`hg` was not found')
        try:
            # check if the svn executable is usable (on macOS)
            # and not only exists to state that the program is not installed
            subprocess.check_call([cls._svn, '--version'], stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            raise unittest.SkipTest('`svn` was not found') from e

        cls.temp_dir = TemporaryDirectory(suffix='.vcstmp')

        # Create the staged subversion repository
        svnrepo_path = os.path.join(cls.temp_dir.name, 'svnrepo')
        os.mkdir(svnrepo_path)
        subprocess.check_call(
            [
                'svnadmin',
                'create',
                '.',
            ],
            cwd=svnrepo_path,
        )

        svnclone_path = os.path.join(cls.temp_dir.name, 'svnclone')
        os.mkdir(svnclone_path)
        shutil.copy(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'LICENSE'),
            svnclone_path,
        )
        for command in (
            ('checkout', to_file_url(svnrepo_path), '.', '--quiet'),
            ('add', 'LICENSE', '--quiet'),
            ('commit', 'LICENSE', '-m', 'Initial commit', '--quiet'),
        ):
            subprocess.check_call(
                [
                    cls._svn,
                    *command,
                ],
                cwd=svnclone_path,
            )

        # Create the staged mercurial repository
        hgrepo_path = os.path.join(cls.temp_dir.name, 'hgrepo')
        os.mkdir(hgrepo_path)
        for command in (
            ('init', '.'),
            ('branch', '--quiet', 'stable'),
            ('commit', '-m', 'Initial commit', '-d', cls._commit_date),
            ('tag', '-d', cls._commit_date, '5.8'),
        ):
            subprocess.check_call(
                [
                    cls._hg,
                    *command,
                ],
                cwd=hgrepo_path,
                env=cls._hg_env,
            )

        # Populate the staged.repos file
        repos = {
            'hg/branch': {
                'type': 'hg',
                'url': to_file_url(hgrepo_path),
                'version': 'stable',
            },
            'hg/hash': {
                'type': 'hg',
                'url': to_file_url(hgrepo_path),
                'version': '9bd654917508',
            },
            'hg/tag': {
                'type': 'hg',
                'url': to_file_url(hgrepo_path),
                'version': '5.8',
            },
            'svn/rev': {
                'type': 'svn',
                'url': to_file_url(svnrepo_path),
                'version': '1',
            },
        }

        cls.repos_file_path = os.path.join(cls.temp_dir.name, 'staged.repos')
        with open(cls.repos_file_path, 'wb') as f:
            yaml.safe_dump({'repositories': repos}, f, encoding='utf-8')

    @classmethod
    def tearDownClass(cls):
        cls.repos_file_path = None
        if cls.temp_dir:
            cls.temp_dir.cleanup()
        cls.temp_dir = None
