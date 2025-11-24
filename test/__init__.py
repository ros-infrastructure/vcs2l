"""Fixtures and utilities for testing vcs2l."""

import os
import re
import shutil
import subprocess
import tarfile
import unittest
import zipfile
from pathlib import Path
from shutil import which
from tempfile import TemporaryDirectory

import yaml

REPO_LINK = 'https://github.com/ros-infrastructure/vcs2l.git'


def to_file_url(path):
    return Path(path).as_uri()


def extract_commit(url):
    """Extract commit hash from version for zip/tar clients."""
    m = re.search(r'vcs2l-([a-fA-F0-9]{40})', url)
    return m.group(1) if m else None


def setup_git_repository(temp_dir):
    """Create a git repository for testing."""
    repo_root = os.path.dirname(os.path.dirname(__file__))
    gitrepo_path = os.path.join(temp_dir.name, 'gitrepo')

    commits_count = int(
        subprocess.check_output(
            ['git', 'rev-list', '--count', 'HEAD'], cwd=repo_root
        ).strip()
    )

    if commits_count == 1:
        repo_root = REPO_LINK  # codecov sparsely clones the repo

    subprocess.check_call(['git', 'clone', repo_root, gitrepo_path])
    try:
        subprocess.check_call(['git', 'checkout', 'main'], cwd=gitrepo_path)
    except subprocess.CalledProcessError:
        # Create branch named 'main' as CI checks out with no branch
        subprocess.check_call(['git', 'checkout', '-b', 'main'], cwd=gitrepo_path)

    return gitrepo_path


def setup_tar_archive(temp_dir, target_commit):
    """Create a tar archive for testing by checking out the target commit."""
    gitrepo_path = os.path.join(temp_dir.name, 'gitrepo')
    tar_path = os.path.join(temp_dir.name, 'tar')

    subprocess.check_call(['git', 'clone', gitrepo_path, tar_path])
    subprocess.check_call(['git', 'checkout', target_commit], cwd=tar_path)
    shutil.rmtree(os.path.join(tar_path, '.git'))  # .git not present in tar archive

    archive_dir = os.path.join(temp_dir.name, 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    tarball_path = os.path.join(archive_dir, f'{target_commit}.tar.gz')

    with tarfile.TarFile.open(tarball_path, 'w:gz') as tar:
        tar.add(tar_path, arcname=f'vcs2l-{target_commit}')

    return tarball_path


def setup_zip_archive(temp_dir, target_commit):
    """Create a zip archive for testing by checking out the target commit."""
    gitrepo_path = os.path.join(temp_dir.name, 'gitrepo')
    zip_path = os.path.join(temp_dir.name, 'zip')

    subprocess.check_call(['git', 'clone', gitrepo_path, zip_path])
    subprocess.check_call(['git', 'checkout', target_commit], cwd=zip_path)
    shutil.rmtree(os.path.join(zip_path, '.git'))  # .git not present in zip archive

    archive_dir = os.path.join(temp_dir.name, 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    zipfile_path = os.path.join(archive_dir, f'{target_commit}.zip')

    with zipfile.ZipFile(zipfile_path, 'w') as zipf:
        for root, dirs, files in os.walk(zip_path):
            # Add directory entries
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                arcname = (
                    os.path.join(
                        f'vcs2l-{target_commit}', os.path.relpath(dir_path, zip_path)
                    )
                    + '/'
                )
                zipf.write(dir_path, arcname)

            # Add files
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join(
                    f'vcs2l-{target_commit}', os.path.relpath(file_path, zip_path)
                )
                zipf.write(file_path, arcname)

    return zipfile_path


class StagedReposFile(unittest.TestCase):
    """Fixture for testing git, tar, and zip clients."""

    _git = which('git')
    temp_dir = None
    repos_file_path = None

    @classmethod
    def setUpClass(cls, repos_file=None):
        if not cls._git:
            raise unittest.SkipTest('`git` was not found')

        cls.temp_dir = TemporaryDirectory(suffix='.vcstmp')

        if repos_file is None:
            raise ValueError('A repos file must be provided')

        with open(repos_file, 'r', encoding='utf-8') as f:
            repos_data = yaml.safe_load(f)

        repos = repos_data.get('repositories')

        # Create the temp git repository
        gitrepo_path = setup_git_repository(cls.temp_dir)

        # Use the existing file as a baseline
        repos = repos_data['repositories'].copy()

        for repo_name, repo_config in repos.items():
            if repo_config['type'] == 'git':
                repos[repo_name]['url'] = to_file_url(gitrepo_path)

            elif repo_config['type'] == 'tar':
                extracted_commit = extract_commit(repo_config['version'])
                repos[repo_name]['url'] = to_file_url(
                    setup_tar_archive(cls.temp_dir, extracted_commit)
                )

            elif repo_config['type'] == 'zip':
                extracted_commit = extract_commit(repo_config['version'])
                repos[repo_name]['url'] = to_file_url(
                    setup_zip_archive(cls.temp_dir, extracted_commit)
                )

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
