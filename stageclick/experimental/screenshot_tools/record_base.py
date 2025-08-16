__all__ = ['create_screenshot_func', 'create_window', 'register_thumbnail',
           'record_continuously', 'RegisterThumbnailFailed', 'FailedToScreenshot',
           'create_window', 'print_window_capture', 'make_window_transparent']

import ctypes
import math
from typing import Callable

import cv2
import numpy as np
from pygetwindow import Win32Window, Window as gwWindow

import stageclick.experimental.screenshot_tools.screen_capture as screen_capture
from stageclick.core import Window
from stageclick.experimental.screenshot_tools.record import print_window_capture, make_window_transparent


class RegisterThumbnailFailed(Exception):
    ...


class FailedToScreenshot(Exception):
    pass


def create_window(window: Win32Window | gwWindow, exceptions: list[tuple[int, tuple[float, float]]] = None) -> int:
    """
    Exception: [(hwnd: coef), ...]
    """
    exceptions = exceptions or []
    coef = 1, 1
    for other_hwnd, coef in exceptions:
        if window._hWnd == other_hwnd:
            coef = coef
    host = screen_capture.create_window(math.ceil(window.width * coef[0]), math.ceil(window.height * coef[1]))

    return host


def register_thumbnail(target: int, host: int, window: Win32Window | gwWindow | Window, raise_exc=True) -> bool:
    success = screen_capture.register_thumbnail(target, host, window.width, window.height)
    if not success and raise_exc:
        raise RegisterThumbnailFailed("Failed to register thumbnail")
    return success


def create_screenshot_func(window: Window, custom_size_coef: list[tuple[int, tuple[float, float]]] = None):
    target_hwnd = window._window._hWnd
    target_win32_window = Win32Window(target_hwnd)
    host = create_window(target_win32_window, custom_size_coef)
    register_thumbnail(target_hwnd, host, target_win32_window)
    make_window_transparent(host, alpha=0)

    def screenshot_func(crop_top_bar=False):
        # print(f"{host=}")
        img = print_window_capture(host)
        # print(f"1st {img=}")

        if img is None:
            raise FailedToScreenshot("Failed to capture window.")

        if crop_top_bar:
            # print(f"before crop {img=}")
            img = img[40:, :]
            # print(f"after crop {img=}")

        # print(f"2nd {img=}")

        return img

    def free_up() -> None:
        user32 = ctypes.windll.user32
        if host and user32.IsWindow(host):
            user32.DestroyWindow(host)

    return screenshot_func, free_up


def record_continuously(screenshot_func: Callable[[bool], np.ndarray],
                        title="Captured Thumbnail", crop_top_bar=False) -> None:
    while True:
        frame = screenshot_func(crop_top_bar)
        cv2.imshow(title, frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def in_place_test(title: str):
    window = Window.find(title)  # Replace with actual window title
    screenshot, _ = create_screenshot_func(window)
    record_continuously(screenshot)


if __name__ == '__main__':
    import signal

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    in_place_test('Spotify')
