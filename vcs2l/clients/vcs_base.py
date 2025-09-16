import os
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from vcs2l.executor import ansi


class VcsClientBase(object):
    type = None

    def __init__(self, path):
        self.path = path

    def __getattribute__(self, name):
        if name == 'import':
            try:
                return self.import_
            except AttributeError:
                pass
        return super(VcsClientBase, self).__getattribute__(name)

    def _not_applicable(self, command, message=None):
        return {
            'cmd': '%s.%s(%s)'
            % (self.__class__.type, 'push', command.__class__.command),
            'output': "Command '%s' not applicable for client '%s'%s"
            % (
                command.__class__.command,
                self.__class__.type,
                ': ' + message if message else '',
            ),
            'returncode': NotImplemented,
        }

    def _run_command(self, cmd, env=None, retry=0):
        for i in range(retry + 1):
            if i > 0:
                print(
                    ansi('yellowf')
                    + 'Retrying command (%d/%d): %s' % (i, retry, ' '.join(cmd))
                    + ansi('reset'),
                    file=sys.stderr,
                )
            result = run_command(cmd, os.path.abspath(self.path), env=env)
            if not result['returncode']:
                # return successful result
                break
            if i >= retry:
                # return the failure after retries
                break
            # increasing sleep before each retry
            time.sleep(i + 1)
        return result

    def _create_path(self):
        if not os.path.exists(self.path):
            try:
                os.makedirs(self.path)
            except os.error as e:
                return {
                    'cmd': 'os.makedirs(%s)' % self.path,
                    'cwd': self.path,
                    'output': "Could not create directory '%s': %s" % (self.path, e),
                    'returncode': 1,
                }
        return None

    def get_path(self):
        """Get the local path of the repository."""
        return self.path

    def export_repository(self, version, basepath):
        """Export the repository at the given version to the given basepath.

        Args:
            version: the version to export
            basepath: the path to export to
        Returns:
            A dict with keys 'cmd', 'cwd', 'output', and 'returncode'.
        """
        raise NotImplementedError(
            'Base class export_repository method must be overridden for client type %s '
            % self.__class__.type
        )

    def checkout(self, url, version=None, verbose=False, shallow=False, timeout=None):
        """Checkout the repository from the given URL.

        Args:
            url: the URL to checkout from
            version: the version to checkout (branch, tag, or revision)
            verbose: whether to run the command in verbose mode
            shallow: whether to perform a shallow checkout (if supported)
            timeout: timeout for network operations (if supported)
        Returns:
            True on success, False otherwise.
        """
        raise NotImplementedError(
            'Base class checkout method must be overridden for client type %s '
            % self._vcs_type_name
        )


def run_command(cmd, cwd, env=None):
    if not os.path.exists(cwd):
        cwd = None
    result = {'cmd': ' '.join(cmd), 'cwd': cwd}
    try:
        proc = subprocess.Popen(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env
        )
        output, _ = proc.communicate()
        result['output'] = output.rstrip().decode('utf8')
        result['returncode'] = proc.returncode
    except subprocess.CalledProcessError as e:
        result['output'] = e.output.decode('utf8')
        result['returncode'] = e.returncode
    return result


def load_url(url, retry=2, retry_period=1, timeout=10):
    try:
        fh = urlopen(url, timeout=timeout)
    except HTTPError as e:
        if e.code == 503 and retry:
            time.sleep(retry_period)
            return load_url(
                url, retry=retry - 1, retry_period=retry_period, timeout=timeout
            )
        e.msg += ' (%s)' % url
        raise
    except URLError as e:
        if isinstance(e.reason, socket.timeout) and retry:
            time.sleep(retry_period)
            return load_url(
                url, retry=retry - 1, retry_period=retry_period, timeout=timeout
            )
        raise URLError(str(e) + ' (%s)' % url)
    return fh.read()


def test_url(url, retry=2, retry_period=1, timeout=10):
    request = Request(url)
    request.get_method = lambda: 'HEAD'

    try:
        response = urlopen(request)
    except HTTPError as e:
        if e.code == 503 and retry:
            time.sleep(retry_period)
            return test_url(
                url, retry=retry - 1, retry_period=retry_period, timeout=timeout
            )
        e.msg += ' (%s)' % url
        raise
    except URLError as e:
        if isinstance(e.reason, socket.timeout) and retry:
            time.sleep(retry_period)
            return test_url(
                url, retry=retry - 1, retry_period=retry_period, timeout=timeout
            )
        raise URLError(str(e) + ' (%s)' % url)
    return response
