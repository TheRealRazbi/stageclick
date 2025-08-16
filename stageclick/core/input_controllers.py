# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ['mouse', 'keyboard', 'MouseButton', 'Key', 'alt_tab', 'alt_n', 'ctrl_up', 'ctrl_c', 'ctrl_down', 'alt_y',
           'ctrl_a', 'ctrl_s', 'ctrl_right', 'run_listener', 'PauseHandler', 'MouseController', 'KeyboardController',
           'KeyboardListener']

import threading
import time

import pynput
from pynput.keyboard import Key, Controller as KeyboardController, Listener as KeyboardListener
from pynput.mouse import Controller as MouseController, Button as MouseButton

from stageclick.log import log_colored


class PauseHandler:
    def __init__(self, toggle_vk=109):  # Numpad - to toggle
        self.keep_running = threading.Event()
        self.keep_running.set()
        self.toggle_vk = toggle_vk
        self.last_switch_at = 0
        self.listener = pynput.keyboard.Listener(on_press=self._on_press)
        self.listener.start()

    def _on_press(self, key):
        if isinstance(key, pynput.keyboard.KeyCode):
            if key.vk == self.toggle_vk:
                if time.time() - self.last_switch_at < 1:
                    return

                if self.keep_running.is_set():
                    log_colored("Paused mouse & keyboard".center(70, '-'), "red", "info")
                    self.keep_running.clear()
                else:
                    log_colored("Resumed mouse & keyboard".center(70, '+'), "green", "info")
                    self.keep_running.set()
                self.last_switch_at = time.time()

    def wait_if_paused(self):
        self.keep_running.wait()


pause_handler = PauseHandler()


class CustomMouse(MouseController):
    def click(self, where=None, count=1, skip_click=False, *, button=MouseButton.left):
        pause_handler.wait_if_paused()
        if where is not None:
            if isinstance(where, int):
                raise ValueError("'where' parameter should be a tuple of x, y coordinates. Did you forget parentheses?")
            self.position = where
        if not skip_click:
            super().click(button, count)


class CustomKeyboard(KeyboardController):
    def tap(self, key):
        pause_handler.wait_if_paused()
        super().tap(key)

    def press(self, key):
        pause_handler.wait_if_paused()
        super().press(key)

    def release(self, key):
        pause_handler.wait_if_paused()
        super().release(key)


mouse = CustomMouse()
keyboard = CustomKeyboard()


# Convenience functions
def alt_tab():
    with keyboard.pressed(Key.alt):
        keyboard.tap(Key.tab)


def alt_n():
    with keyboard.pressed(Key.alt):
        keyboard.tap('n')


def alt_y():
    with keyboard.pressed(Key.alt):
        keyboard.tap('y')


def ctrl_up():
    with keyboard.pressed(Key.ctrl):
        keyboard.tap(Key.up)


def ctrl_down():
    with keyboard.pressed(Key.ctrl):
        keyboard.tap(Key.down)


def ctrl_c():
    with keyboard.pressed(Key.ctrl):
        keyboard.tap('c')


def ctrl_a():
    with keyboard.pressed(Key.ctrl):
        keyboard.tap('a')


def ctrl_s():
    with keyboard.pressed(Key.ctrl):
        keyboard.tap('s')


def ctrl_right():
    with keyboard.pressed(Key.ctrl):
        keyboard.tap(Key.right)


def run_listener(on_press, *args, **kwargs) -> None:
    """Run a blocking listener with the given on_press function"""
    listener = KeyboardListener(on_press=on_press, *args, **kwargs)
    listener.start()
    try:
        while listener.running:
            time.sleep(0.1)  # keep the main thread alive
    except KeyboardInterrupt:
        log_colored("Exiting...", "red", "info")
    finally:
        listener.stop()
        listener.join()
