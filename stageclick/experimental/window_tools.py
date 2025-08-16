__all__ = ["Window"]

from typing import Callable, Optional

import pygetwindow as gw

from .screenshot_tools.record_base import create_screenshot_func
from ..core.window_tools import Window as StableWindow


class Window(StableWindow):
    def __init__(self, title: str, window: gw.Window):
        """
        :param title: The title of the window.
        :param window: The pygetwindow Window object.
        """
        super().__init__(title, window)
        self._record_func: Optional[Callable[[], 'np.ndarray']] = None
        self._free_func = Optional[Callable[[], None]]

    def screenshot(self, attempt=0) -> Optional['np.ndarray']:
        if self.window.isMinimized:
            self.window.restore()
        if self._record_func is None:
            self._record_func, self._free_func = create_screenshot_func(self)
        ss = self._record_func()
        return ss

    def free_recording_window(self):
        if self._free_func:
            self._free_func()
            self._record_func = None
            self._free_func = None