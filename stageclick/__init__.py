# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from importlib.metadata import version, PackageNotFoundError
from .window_tools import Window, WindowClosed, Button, WindowNotFound, TemplateNotFound
from .image_processing import match_template, ScreenshotArea, screenshot_area, match_template_all, \
    create_load_template, find_color_in_image, split_screenshot_into_rows, get_main_monitor_bounding_box
from .input_controllers import mouse, keyboard, MouseButton, MouseController, KeyboardController, KeyboardListener, \
    Key, alt_n, alt_y, alt_tab, ctrl_a, ctrl_up, ctrl_c, ctrl_s, ctrl_down, ctrl_right, run_listener, PauseHandler
from .step_runner import *

try:
    __version__ = version("stage-click")
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ["Window", "WindowClosed", "Button", "match_template", "ScreenshotArea", "screenshot_area",
           "match_template_all", "create_load_template", "split_screenshot_into_rows", "find_color_in_image",
           "get_main_monitor_bounding_box", "__version__", "MouseController", "KeyboardController",
           "MouseButton", "KeyboardListener", "Key", "alt_n", "alt_y", "alt_tab", "ctrl_a", "ctrl_up",
           "ctrl_c", "ctrl_s", "ctrl_down", "ctrl_right", "run_listener", "PauseHandler", "WindowNotFound",
           "TemplateNotFound", *step_runner.__all__]
