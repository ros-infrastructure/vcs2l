import sys

import vcs2l
from vcs2l import *  # noqa: F403

sys.modules[__name__].__dict__.update(vcs2l.__dict__)
