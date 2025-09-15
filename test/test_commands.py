import os
import subprocess
import sys
import unittest
from shutil import which

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from vcs2l.clients.git import GitClient  # noqa: E402
from vcs2l.util import rmtree  # noqa: E402

file_uri_scheme = 'file://' if sys.platform != 'win32' else 'file:///'

REPOS_FILE = os.path.join(os.path.dirname(__file__), 'list.repos')
REPOS_FILE_URL = file_uri_scheme + REPOS_FILE
REPOS2_FILE = os.path.join(os.path.dirname(__file__), 'list2.repos')
REPOS_EXTENDS_FILE = os.path.join(os.path.dirname(__file__), 'list_extension.repos')
REPOS_MULTIPLE_EXTENDS_FILE = os.path.join(
    os.path.dirname(__file__), 'list_multiple_extension.repos'
)
REPOS_EXTENDS_LOOP_FILE = os.path.join(
    os.path.dirname(__file__), 'loop_extension.repos'
)
BAD_REPOS_FILE = os.path.join(os.path.dirname(__file__), 'bad.repos')
TEST_WORKSPACE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'test_workspace'
)

svn = which('svn')
hg = which('hg')
if svn:
    # check if the svn executable is usable (on macOS)
    # and not only exists to state that the program is not installed
    try:
        subprocess.check_call([svn, '--version'])
    except subprocess.CalledProcessError:
        svn = False


class TestCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert not os.path.exists(TEST_WORKSPACE)
        os.makedirs(TEST_WORKSPACE)

        try:
            output = run_command('import', ['--input', REPOS_FILE, '.'])
            expected = get_expected_output('import')
            # newer git versions don't append three dots after the commit hash
            assert output == expected or output == expected.replace(b'... ', b' ')
        except Exception:
            cls.tearDownClass()
            raise

    @classmethod
    def tearDownClass(cls):
        rmtree(TEST_WORKSPACE)

    def test_branch(self):
        output = run_command('branch')
        expected = get_expected_output('branch')
        self.assertEqual(output, expected)

    def test_custom(self):
        output = run_command(
            'custom',
            args=['--git', '--args', 'describe', '--abbrev=0', '--tags'],
            subfolder='immutable',
        )
        expected = get_expected_output('custom_describe')
        self.assertEqual(output, expected)

    def test_diff(self):
        license_path = os.path.join(TEST_WORKSPACE, 'immutable', 'hash', 'LICENSE')
        file_length = None
        try:
            with open(license_path, 'ab') as h:
                file_length = h.tell()
                h.write(b'testing')

            output = run_command('diff', args=['--hide'])
            expected = get_expected_output('diff_hide')
        finally:
            if file_length is not None:
                with open(license_path, 'ab') as h:
                    h.truncate(file_length)

        self.assertEqual(output, expected)

    def test_export_exact_with_tags(self):
        output = run_command(
            'export', args=['--exact-with-tags'], subfolder='immutable'
        )
        expected = get_expected_output('export_exact_with_tags')
        self.assertEqual(output, expected)

    def test_export_exact(self):
        output = run_command('export', args=['--exact'], subfolder='immutable')
        expected = get_expected_output('export_exact')
        self.assertEqual(output, expected)

    def test_log(self):
        output = run_command('log', args=['--limit', '2'], subfolder='immutable')
        expected = get_expected_output('log_limit')
        self.assertEqual(output, expected)

    def test_log_merge_only(self):
        output = run_command('log', args=['--merge-only'], subfolder='immutable/tag')
        expected = get_expected_output('log_merges_only')
        self.assertEqual(output, expected)

    def test_pull(self):
        output = run_command('pull', args=['--workers', '1'])
        expected = get_expected_output('pull')
        # replace message from older git versions
        output = output.replace(
            b'anch. Please specify which\nbranch you want to merge with. See',
            b'anch.\nPlease specify which branch you want to merge with.\nSee',
        )
        self.assertEqual(output, expected)

    def test_pull_api(self):
        from io import StringIO

        from vcs2l.commands.pull import main

        stdout_stderr = StringIO()

        # change and restore cwd
        cwd_bck = os.getcwd()
        os.chdir(TEST_WORKSPACE)
        try:
            # change and restore USE_COLOR flag
            from vcs2l import executor

            use_color_bck = executor.USE_COLOR
            executor.USE_COLOR = False
            try:
                # change and restore os.environ
                env_bck = os.environ
                os.environ = dict(os.environ)
                os.environ.update(
                    LANG='en_US.UTF-8',
                    PYTHONPATH=(
                        os.path.dirname(os.path.dirname(__file__))
                        + os.pathsep
                        + os.environ.get('PYTHONPATH', '')
                    ),
                )
                try:
                    rc = main(
                        args=['--workers', '1'],
                        stdout=stdout_stderr,
                        stderr=stdout_stderr,
                    )
                finally:
                    os.environ = env_bck
            finally:
                executor.USE_COLOR = use_color_bck
        finally:
            os.chdir(cwd_bck)

        assert rc == 0
        # replace message from older git versions
        output = stdout_stderr.getvalue().replace(
            'anch. Please specify which\nbranch you want to merge with. See',
            'anch.\nPlease specify which branch you want to merge with.\nSee',
        )
        # the output was retrieved through a different way here
        output = adapt_command_output(output.encode()).decode()
        if sys.platform == 'win32':
            # it does not include carriage return characters on Windows
            output = output.replace('\n', '\r\n')
        expected = get_expected_output('pull').decode()
        assert output == expected

    def test_reimport(self):
        cwd_vcs2l = os.path.join(TEST_WORKSPACE, 'vcs2l')
        subprocess.check_output(
            ['git', 'remote', 'add', 'foo', 'http://foo.com/bar.git'],
            stderr=subprocess.STDOUT,
            cwd=cwd_vcs2l,
        )
        cwd_without_version = os.path.join(TEST_WORKSPACE, 'without_version')
        subprocess.check_output(
            ['git', 'checkout', '-b', 'foo'],
            stderr=subprocess.STDOUT,
            cwd=cwd_without_version,
        )
        output = run_command('import', ['--skip-existing', '--input', REPOS_FILE, '.'])
        expected = get_expected_output('reimport_skip')
        # newer git versions don't append three dots after the commit hash
        assert output == expected or output == expected.replace(b'... ', b' ')

        subprocess.check_output(
            ['git', 'remote', 'set-url', 'origin', 'http://foo.com/bar.git'],
            stderr=subprocess.STDOUT,
            cwd=cwd_without_version,
        )
        run_command('import', ['--skip-existing', '--input', REPOS_FILE, '.'])

        output = run_command('import', ['--force', '--input', REPOS_FILE, '.'])
        expected = get_expected_output('reimport_force')
        # on Windows, the "Already on 'main'" message is after the
        # "Your branch is up to date with ..." message, so remove it
        # from both output and expected strings
        if sys.platform == 'win32':
            output = output.replace(b"Already on 'main'\r\n", b'')
            expected = expected.replace(b"Already on 'main'\r\n", b'')
        # newer git versions don't append three dots after the commit hash
        assert output == expected or output == expected.replace(b'... ', b' ')

        subprocess.check_output(
            ['git', 'remote', 'remove', 'foo'], stderr=subprocess.STDOUT, cwd=cwd_vcs2l
        )

    def test_reimport_failed(self):
        cwd_tag = os.path.join(TEST_WORKSPACE, 'immutable', 'tag')
        subprocess.check_output(
            ['git', 'remote', 'add', 'foo', 'http://foo.com/bar.git'],
            stderr=subprocess.STDOUT,
            cwd=cwd_tag,
        )
        subprocess.check_output(
            ['git', 'remote', 'rm', 'origin'], stderr=subprocess.STDOUT, cwd=cwd_tag
        )
        try:
            run_command('import', ['--skip-existing', '--input', REPOS_FILE, '.'])
        finally:
            subprocess.check_output(
                ['git', 'remote', 'rm', 'foo'], stderr=subprocess.STDOUT, cwd=cwd_tag
            )
            subprocess.check_output(
                [
                    'git',
                    'remote',
                    'add',
                    'origin',
                    'https://github.com/ros-infrastructure/vcs2l.git',
                ],
                stderr=subprocess.STDOUT,
                cwd=cwd_tag,
            )

    def test_import_force_non_empty(self):
        workdir = os.path.join(TEST_WORKSPACE, 'force-non-empty')
        os.makedirs(os.path.join(workdir, 'vcs2l', 'not-a-git-repo'))
        try:
            output = run_command(
                'import',
                ['--force', '--input', REPOS_FILE, '.'],
                subfolder='force-non-empty',
            )
            expected = get_expected_output('import')
            # newer git versions don't append ... after the commit hash
            assert output == expected or output == expected.replace(b'... ', b' ')
        finally:
            rmtree(workdir)

    def test_import_shallow(self):
        workdir = os.path.join(TEST_WORKSPACE, 'import-shallow')
        os.makedirs(workdir)
        try:
            output = run_command(
                'import',
                ['--shallow', '--input', REPOS_FILE, '.'],
                subfolder='import-shallow',
            )
            # the actual output contains absolute paths
            output = output.replace(
                b'repository in ' + workdir.encode() + b'/', b'repository in ./'
            )
            expected = get_expected_output('import_shallow')
            # newer git versions don't append ... after the commit hash
            assert output == expected or output == expected.replace(b'... ', b' ')

            # check that repository history has only one commit
            output = subprocess.check_output(
                ['git', 'log', '--format=oneline'],
                stderr=subprocess.STDOUT,
                cwd=os.path.join(workdir, 'vcs2l'),
            )
            assert len(output.splitlines()) == 1
        finally:
            rmtree(workdir)

    def import_common(self, import_file, repos_file):
        """Common test function for import operations

        Args:
            import_file: Assertion expected output file name (without .txt)
            repos_file: path to the .repos file to use
        """
        workdir = os.path.join(TEST_WORKSPACE, import_file)
        os.makedirs(workdir)
        try:
            output = run_command(
                'import', ['--input', repos_file, '.'], subfolder=import_file
            )
            # the actual output contains absolute paths
            output = output.replace(
                b'repository in ' + workdir.encode() + b'/', b'repository in ./'
            )
            expected = get_expected_output(import_file)
            # newer git versions don't append ... after the commit hash
            assert output == expected or output == expected.replace(b'... ', b' ')
        finally:
            rmtree(workdir)

    def test_deletion(self):
        """Test the delete command."""
        workdir = os.path.join(TEST_WORKSPACE, 'deletion')
        os.makedirs(workdir)
        try:
            run_command(
                'import', ['--input', REPOS_FILE_URL, '.'], subfolder='deletion'
            )
            output = run_command(
                'delete',
                ['--force', '--input', REPOS_FILE_URL, '.'],
                subfolder='deletion',
            )
            expected = get_expected_output('delete')
            # we don't care what order these messages appear in
            output = b'\n'.join(sorted(output.split(b'\n')))
            expected = b'\n'.join(sorted(output.split(b'\n')))
            self.assertEqual(output, expected)

            # check that repositories were actually deleted
            self.assertFalse(os.path.exists(os.path.join(workdir, 'immutable/hash')))
            self.assertFalse(
                os.path.exists(os.path.join(workdir, 'immutable/hash_tar'))
            )
            self.assertFalse(
                os.path.exists(os.path.join(workdir, 'immutable/hash_zip'))
            )
            self.assertFalse(os.path.exists(os.path.join(workdir, 'immutable/tag')))
            self.assertFalse(os.path.exists(os.path.join(workdir, 'vcs2l')))
            self.assertFalse(os.path.exists(os.path.join(workdir, 'without_version')))
        finally:
            rmtree(workdir)

    def test_import_file_url(self):
        """Test import from file URL."""
        self.import_common('import', REPOS_FILE_URL)

    def test_import_extends(self):
        """Test import with extends functionality."""
        self.import_common('import_extends', REPOS_EXTENDS_FILE)

    def test_import_extends_loop(self):
        """Test import with extends functionality that creates a circular import."""
        with self.assertRaises(subprocess.CalledProcessError) as e:
            run_command('import', ['--input', REPOS_EXTENDS_LOOP_FILE, '.'])
        self.assertIn(b'Circular import detected:', e.exception.output)

    def test_import_multiple_extends(self):
        """Test import with multiple extends functionality."""
        self.import_common('import_multiple_extends', REPOS_MULTIPLE_EXTENDS_FILE)

    def test_validate(self):
        output = run_command('validate', ['--input', REPOS_FILE])
        expected = get_expected_output('validate')
        self.assertEqual(output, expected)

        output = run_command('validate', ['--hide-empty', '--input', REPOS_FILE])
        expected = get_expected_output('validate_hide')
        # we don't care what order these messages appear in
        output = b'\n'.join(sorted(output.split(b'\n')))
        expected = b'\n'.join(sorted(output.split(b'\n')))
        self.assertEqual(output, expected)

        output = run_command('validate', ['--input', BAD_REPOS_FILE])
        expected = get_expected_output('validate_bad')
        self.assertEqual(output, expected)

    @unittest.skipIf(not svn, '`svn` was not found')
    @unittest.skipIf(not hg, '`hg` was not found')
    def test_validate_svn_and_hg(self):
        output = run_command('validate', ['--input', REPOS2_FILE])
        expected = get_expected_output('validate2')
        self.assertEqual(output, expected)

    def test_remote(self):
        output = run_command('remotes', args=['--repos'])
        expected = get_expected_output('remotes_repos')
        self.assertEqual(output, expected)

    def test_status(self):
        output = run_command('status')
        # replace message from older git versions
        # https://github.com/git/git/blob/3ec7d702a89c647ddf42a59bc3539361367de9d5/Documentation/RelNotes/2.10.0.txt#L373-L374
        output = output.replace(b'working directory clean', b'working tree clean')
        # the following seems to have changed between git 2.10.0 and 2.14.1
        output = output.replace(b'.\nnothing to commit', b'.\n\nnothing to commit')
        expected = get_expected_output('status')
        self.assertEqual(output, expected)


def run_command(command, args=None, subfolder=None):
    repo_root = os.path.dirname(os.path.dirname(__file__))
    script = os.path.join(repo_root, 'scripts', 'vcs-' + command)
    env = dict(os.environ)
    env.update(
        GIT_CONFIG_GLOBAL=os.path.join(repo_root, 'test', '.gitconfig'),
        LANG='en_US.UTF-8',
        PYTHONPATH=repo_root + os.pathsep + env.get('PYTHONPATH', ''),
        PYTHONWARNINGS='ignore',
    )
    cwd = TEST_WORKSPACE
    if subfolder:
        cwd = os.path.join(cwd, subfolder)
    output = subprocess.check_output(
        [sys.executable, script] + (args or []),
        stderr=subprocess.STDOUT,
        cwd=cwd,
        env=env,
    )
    return adapt_command_output(output, cwd)


def adapt_command_output(output, cwd=None):
    assert isinstance(output, bytes)
    # replace message from older git versions
    output = output.replace(
        b'git checkout -b new_branch_name', b'git checkout -b <new-branch-name>'
    )
    output = output.replace(b'(detached from ', b'(HEAD detached at ')
    output = output.replace(
        b"ady on 'main'\n=",
        b"ady on 'main'\nYour branch is up-to-date with 'origin/main'.\n=",
    )
    output = output.replace(b'# HEAD detached at ', b'HEAD detached at ')
    output = output.replace(
        b'# On branch main',
        b"On branch main\nYour branch is up-to-date with 'origin/main'.\n",
    )
    # the following seems to have changed between git 2.17.1 and 2.25.1
    output = output.replace(b"Note: checking out '", b"Note: switching to '")
    output = output.replace(
        b'by performing another checkout.', b'by switching back to a branch.'
    )
    output = output.replace(
        b'using -b with the checkout command again.',
        b'using -c with the switch command.',
    )
    output = output.replace(
        b'git checkout -b <new-branch-name>',
        b'git switch -c <new-branch-name>\n\n'
        b'Or undo this operation with:\n\n'
        b'  git switch -\n\n'
        b'Turn off this advice by setting config variable '
        b'advice.detachedHead to false',
    )
    if sys.platform == 'win32':
        if cwd:
            # on Windows, git prints full path to repos
            # in some messages, so make it relative
            cwd_abs = os.path.abspath(cwd).replace('\\', '/')
            output = output.replace(cwd_abs.encode(), b'.')
        # replace path separators in specific paths;
        # this is less likely to cause wrong test results
        paths_to_replace = [
            (b'.\\immutable', b'./immutable'),
            (b'.\\vcs2l', b'./vcs2l'),
            (b'.\\without_version', b'./without_version'),
            (b'\\hash', b'/hash'),
            (b'\\tag', b'/tag'),
        ]
        for before, after in paths_to_replace:
            output = output.replace(before, after)
    return output


def get_expected_output(name):
    path = os.path.join(os.path.dirname(__file__), name + '.txt')
    with open(path, 'rb') as h:
        content = h.read()
    # change in git version 2.15.0
    # https://github.com/git/git/commit/7560f547e6
    if GitClient.get_git_version() < [2, 15, 0]:
        # use hyphenation for older git versions
        content = content.replace(b'up to date', b'up-to-date')
    return content


if __name__ == '__main__':
    unittest.main()
