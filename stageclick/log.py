# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
from rich.logging import RichHandler

_LOG_LEVEL = logging.INFO


def set_log_level(level: int):
    global _LOG_LEVEL
    _LOG_LEVEL = level
    logging.getLogger().setLevel(level)


def get_logger(name: str = "stageclick") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(markup=True, show_time=False, show_level=True)
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(_LOG_LEVEL)
    return logger


log = get_logger(__name__)


def log_colored(message: str, color: str = "white", level: str = "info"):
    color_tags = f"[{color}]{message}[/{color}]"
    getattr(log, level)(color_tags)
