import sys
import warnings

import vcs2l
from vcs2l import *  # noqa: F403

warnings.warn(
    "The 'vcstool' package is deprecated. Please update your code to use "
    "'vcs2l' instead. This shim will be removed in a future release of vcs2l.",
    DeprecationWarning,
    stacklevel=2,
)


sys.modules[__name__].__dict__.update(vcs2l.__dict__)
