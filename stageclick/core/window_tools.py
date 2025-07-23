# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import ctypes
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import psutil
import pygetwindow as gw
import pyperclip
import win32process
from PIL import ImageGrab
from termcolor import colored

from stageclick.core.image_processing import ScreenshotArea, match_template, screenshot_area
from stageclick.core.input_controllers import mouse, keyboard, Key, MouseButton
from stageclick.log import log_colored, get_logger

__all__ = ["Window", "WindowClosed", "WindowNotFound", "TemplateNotFound", "TemplateFound", "Button",
           "safe_grab_clipboard"]

log = get_logger(__name__)


class WindowNotFound(Exception):
    pass


class TemplateNotFound(Exception):
    pass


class WindowClosed(WindowNotFound):
    """Raised when the window was found previously, but it can't be interacted with now"""


def safe_grab_clipboard():
    try:
        image = ImageGrab.grabclipboard()
        if image is None:
            raise ValueError("No image found in clipboard.")
        return image
    except Exception as e:
        log_colored(f"[Clipboard] Failed to grab image: {e}", "red", "debug")
        return None


@dataclass(kw_only=True)
class TemplateFound:
    where: Optional[tuple[int, int]]
    screenshot: Optional['np.ndarray']

    @property
    def found(self):
        return self.where is not None and len(self.where) != 0

    def __bool__(self):
        return self.found


class Window:
    def __init__(self, title: str, window: gw.Window):
        """
        :param title: The title of the window.
        :param window: The pygetwindow Window object.
        """
        self.title: str = title or window.title
        self._window: 'gw.Window' = window
        self._full_screen_resolution = ScreenshotArea.all_screens().as_width_height()

    @classmethod
    def find(cls, title: str, timeout=0):
        now = time.monotonic()
        if timeout == 0:
            window = gw.getWindowsWithTitle(title)
            if not window:
                raise WindowNotFound(f"Window with title '{title}' not found")
        else:
            while time.monotonic() - now < timeout:
                window = gw.getWindowsWithTitle(title)
                if window:
                    break
                time.sleep(0.05)
            else:
                raise WindowNotFound(f"Window with title '{title}' not found after {timeout} seconds")
        window = window[0]
        return cls(title, window)

    @classmethod
    def find_window_by_exe_path(cls, exe_path: str) -> 'Window':
        """Finds a window based on the executable path of the process."""
        for window in gw.getAllWindows():
            try:
                hwnd = window._hWnd
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                if process.exe() == exe_path:
                    return cls(window.title, window)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        raise WindowNotFound(f"No window found for executable path '{exe_path}'")

    @classmethod
    def start_and_find(cls, *, exe_path: str, title: str, wait_seconds: float = 4) -> 'Window':
        """
        Start a process, wait for a specified amount of time, and locate its window by executable path.

        :param exe_path: The path to the executable to start.
        :param title: The title to set for the window if found.
        :param wait_seconds: Time to wait before searching for the window (in seconds).
        :return: A Window object if found.
        :raises WindowNotFound: If no matching window is found.
        """
        subprocess.Popen(exe_path)
        time.sleep(wait_seconds)

        window = cls.find_window_by_exe_path(exe_path)

        # set title and return window instance
        hwnd = window._window._hWnd
        ctypes.windll.user32.SetWindowTextW(hwnd, title)  # Set the window title
        window.title = title

        return window

    @classmethod
    def start(cls, *, title: str, exe_path: str | Path, max_wait_seconds: float = 10):
        subprocess.Popen(exe_path)
        start_time = time.perf_counter()
        while time.perf_counter() < start_time + max_wait_seconds:
            try:
                return cls.find(title)
            except WindowNotFound:
                time.sleep(0.02)
        raise WindowNotFound(f"Time elapsed ({max_wait_seconds}) while waiting for window to open")

    @classmethod
    def find_or_start(cls, *, title: str, exe_path: str, max_wait_seconds: float = 10):
        try:
            return cls.find(title)
        except WindowNotFound:
            return cls.start(title=title, exe_path=exe_path, max_wait_seconds=max_wait_seconds)

    @classmethod
    def close_if_open(cls, title: str, sleep_if_closed: float = 0) -> bool:
        """
        Closes the window if it is open.
        :param title: The title of the window.
        :param sleep_if_closed: The time to sleep if the window is closed.
        :return: True if the window was found and closed, False otherwise.
        """
        try:
            window = cls.find(title)
            window.close()
            if sleep_if_closed:
                time.sleep(sleep_if_closed)
            return True
        except WindowNotFound:
            return False

    def close(self):
        self._window.close()

    def select(self):
        try:
            if self._window.isMinimized:
                self._window.restore()
            self._window.activate()
        except gw.PyGetWindowException:
            self._window.minimize()
            self._window.restore()
            time.sleep(0.2)
        try:
            self._window.activate()
        except gw.PyGetWindowException:
            raise WindowClosed(f"Window with title '{self.title}' is closed (or something else is happening)")

    def screenshot(self) -> Optional['np.ndarray']:
        if not self._window.isActive or not self._window.visible:
            self.select()

        previous_clipboard = pyperclip.paste()
        with keyboard.pressed(Key.alt_l):
            keyboard.press(Key.print_screen)
            keyboard.release(Key.print_screen)
        time.sleep(0.05)  # this time is necessary for the screenshot to be taken
        clipboard_image = safe_grab_clipboard()
        if clipboard_image is None:
            return None
        image = np.array(ImageGrab.grabclipboard())
        pyperclip.copy(previous_clipboard)
        # image = screenshot_area((self.left, self.top, self.width, self.height))
        """
        ^ this is the traditional way but left, top, width, height don't update and
        it would severely slow things down, not because it's slow, it's fast, but because
        it requires the program to wait unnecessarily to prevent bad errors.

        It might be worth coming back to if we find a way to reliably not waste time when waiting for stuff to show
        """

        if image.shape[:2][::-1] == self._full_screen_resolution:
            # discard screenshots accidentally made of the whole screen
            image = None

        return image

    def wait_for_template(self, template: 'np.ndarray', timeout: float = 5, threshold=0.8,
                          raise_exception=True, area=None) -> 'TemplateFound':
        """
        Waits for a template to appear in the window.
        :param template: The template to wait for.
        :param timeout: The maximum time to wait for the template to appear.
        :param threshold: The threshold to use when matching the template.
        :param raise_exception: Whether to raise an exception if the template is not found.
        :param area: If provided, the area relative to the entire screen to search for the template.
        """
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            try:
                screenshot = screenshot_area(area) if area is not None else None
                return self.find_template(template, screenshot=screenshot, threshold=threshold)
            except (TemplateNotFound, OSError, gw.PyGetWindowException):
                time.sleep(0.05)
        if raise_exception:
            raise TemplateNotFound(f"Template not found in window '{self.title}'")
        return TemplateFound(where=None, screenshot=None)

    def find_template(self, template, screenshot=None, threshold=0.8, raise_exception=True) -> 'TemplateFound':
        if screenshot is None:
            screenshot = self.screenshot()
        found, location = match_template(template, screenshot, threshold=threshold)
        if raise_exception and not found:
            raise TemplateNotFound(f"Template not found in window '{self.title}'")
        return TemplateFound(where=location, screenshot=screenshot)

    def set_title(self, title):
        hwnd = self._window._hWnd
        ctypes.windll.user32.SetWindowTextW(hwnd, title)
        self.title = title

    def is_running(self):
        return ctypes.windll.user32.IsWindow(self._window._hWnd) != 0

    def debug_screenshot(self, show_instead=False):
        # screenshot = self.screenshot()
        screenshot = None
        for _ in range(10):
            try:
                screenshot = self.screenshot()
                if show_instead:
                    cv2.imshow("Debug screenshot", screenshot)
                    cv2.waitKey(0)
                    break
                else:
                    cv2.imwrite("debug_screenshot.png", screenshot)
                    log_colored("Screenshot saved as 'debug_screenshot.png'", "green")
                    break

            except Exception as e:
                log_colored(f"Error displaying screenshot: {e} | {screenshot}", "green")

            else:
                break
        return screenshot

    def minimize(self):
        self._window.minimize()

    def __str__(self):
        return f"Window(title='{self.title}')"

    def __repr__(self):
        return f"Window(title='{self.title}, window={self._window}')"

    @property
    def left(self):
        return self._window.left

    @property
    def top(self):
        return self._window.top

    @property
    def right(self):
        return self._window.right

    @property
    def bottom(self):
        return self._window.bottom

    @property
    def width(self):
        return self._window.width

    @property
    def height(self):
        return self._window.height

    @property
    def visible(self):
        return self._window.visible

    @property
    def window(self):
        return self._window

    @property
    def hwnd(self):
        return self._window._hWnd


@dataclass
class Button:
    """
    A class that represents a button on the screen.

    Attributes:
        window (Window): The window where the button is located.
        template (np.ndarray): The template of the button.
        click_offset (Tuple[int, int]): The offset to apply when clicking the button.
        timeout (float): The maximum time to wait for the button to appear.
        threshold (float): The threshold to use when matching the template.
    """
    window: 'Window'
    template: 'np.ndarray'
    click_offset: tuple[int, int] = field(default_factory=lambda: (0, 0))
    timeout: float = 10.0
    threshold: float = 0.8
    custom_area: Optional[ScreenshotArea] | tuple[int, int, int, int] = None
    middle: bool = True
    _template_width_height: tuple[int, int] = None

    def click(self, testing_position=False, fine_if_not_found=False, timeout=None, times=1) -> bool:
        """
        Clicks the button if found in the window.
        :param testing_position: If True, the mouse will move to the position of the button without clicking.
        :param fine_if_not_found: If True, the method will not raise an exception if the button is not found.
        :param timeout: The maximum time to wait for the button to appear.
        :param times: The number of times to click the button.
        :return: True if the button was found and clicked, False otherwise.
        """
        timeout = timeout or self.timeout
        try:
            found = self.window.wait_for_template(self.template, timeout, threshold=self.threshold,
                                                  area=self.custom_area)
        except TemplateNotFound:
            if not fine_if_not_found:
                raise
            return False
        else:
            _m = self.middle
            x = self.window.left + found.where[0] + self.click_offset[0] + _m * self.template_w_half
            y = self.window.top + found.where[1] + self.click_offset[1] + _m * self.template_h_half
            if testing_position:
                self._test_position(x, y)
            else:
                for _ in range(times):
                    self._click(x, y)
            return True

    def wait_until_visible(self, timeout=None):
        timeout = timeout or self.timeout
        return self.window.wait_for_template(self.template, timeout, threshold=self.threshold, area=self.custom_area)

    @staticmethod
    def _click(x, y):
        mouse.position = x, y
        colored_x, colored_y = colored(x, "magenta"), colored(y, "magenta")
        log.info(f"{colored('Clicking at (', 'blue')}{colored_x}{colored(', ', 'blue')}"
                 f"{colored_y}{colored(')', 'blue')}")
        mouse.click(button=MouseButton.left)

    @staticmethod
    def _test_position(x, y):
        mouse.position = x, y
        log_colored(f"Moved mouse to {x}, {y}", "blue", "info")

    @property
    def template_width_height(self):
        if self._template_width_height is not None:
            return self._template_width_height
        width, height = self.template.shape[:2][::-1]
        self._template_width_height = width, height
        return self._template_width_height

    @property
    def template_w(self):
        return self.template_width_height[0]

    @property
    def template_h(self):
        return self.template_width_height[1]

    @property
    def template_w_half(self):
        return self.template_w * 0.5

    @property
    def template_h_half(self):
        return self.template_h * 0.5
