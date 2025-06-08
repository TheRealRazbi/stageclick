# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("stage-click")
except PackageNotFoundError:
    __version__ = "unknown"
