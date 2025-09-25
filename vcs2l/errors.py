"""Custom exceptions for the vcs2l package."""

import sys


class Vcs2lError(Exception):
    """Base exception for vcs2l-specific errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedPythonVersionError(Vcs2lError):
    """Raised when the Python version is too old for vcs2l."""

    def __init__(self, min_version: str = '3.6'):
        current_version = f'{sys.version_info.major}.{sys.version_info.minor}'
        message = (
            f'Unsupported Python version ({current_version}). '
            f'vcs2l requires Python {min_version} or higher.'
        )
        super().__init__(message)


class CircularImportError(Vcs2lError):
    """Raised when a circular import is detected."""

    def __init__(self, message: str = 'Circular import detected.'):
        super().__init__(message)
