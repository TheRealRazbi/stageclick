# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from importlib.metadata import version, PackageNotFoundError
from . import step_runner
from . import core

import warnings
warnings.warn(
    "stage-click has been renamed to stageclick. Please reinstall from 'stageclick' instead of 'stage-click'",
    DeprecationWarning,
    stacklevel=2
)

try:
    __version__ = version("stage-click")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["core", "step_runner", "__version__"]
