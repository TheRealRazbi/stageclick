# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["ScreenshotArea", "screenshot_area", "match_template", "match_template_all",
           "create_load_template", "FailedToLoadTemplate", "get_main_monitor_bounding_box",
           "split_screenshot_into_rows", "find_color_in_image"]

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Union, Sequence

import cv2
import numpy as np
from PIL import Image
from mss import mss
from screeninfo import get_monitors

from stageclick.log import log_colored


@dataclass
class ScreenshotArea:
    left: int
    top: int
    width: int
    height: int

    def __iter__(self):
        yield self.left
        yield self.top
        yield self.width
        yield self.height

    def as_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height
        }

    def as_x_y(self):
        return self.left, self.top

    def as_width_height(self):
        return self.width, self.height

    @classmethod
    def from_sequence(cls, sequence: Sequence):
        return cls(*sequence)

    @classmethod
    def from_monitor(cls, monitor_index: int = 0):
        monitor = get_monitors()[monitor_index]
        return cls(monitor.x, monitor.y, monitor.width, monitor.height)

    @classmethod
    def all_screens(cls):
        monitors = get_monitors()
        left = min(monitor.x for monitor in monitors)
        top = min(monitor.y for monitor in monitors)
        right = max(monitor.x + monitor.width for monitor in monitors)
        bottom = max(monitor.y + monitor.height for monitor in monitors)
        return cls(left, top, right - left, bottom - top)


def screenshot_area(area: Union[Sequence, dict, ScreenshotArea] = None) -> np.ndarray:
    area = area or ScreenshotArea.all_screens().as_dict()
    if isinstance(area, Sequence):
        area = ScreenshotArea.from_sequence(area)
    if isinstance(area, ScreenshotArea):
        area = area.as_dict()

    if area['width'] <= 0 or area['height'] <= 0:
        raise ValueError("Width and Height must be positive numbers.")

    with mss() as sct:
        try:
            screenshot = sct.grab(area)
        except Exception as e:
            log_colored(f"Failed to grab screenshot: {e}", "red", "error")
            raise RuntimeError(f"Screenshot failed with area {area}") from e
        # Convert screenshot to PIL Image for easier manipulation
        # Make sure to use 'BGRX' as the decoder since mss provides BGRA (alpha channel included)
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.bgra, 'raw', 'BGRX')

    #  PIL image to numpy array
    img_np = np.array(img)

    # BGR to RGB
    img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

    return img_np


class FailedToLoadTemplate(Exception):
    pass


def match_template(template, source, threshold=0.8):
    if source is None:
        return False, None

    if template is None:
        raise ValueError("Template must be provided and cannot be None.")

    if not isinstance(template, np.ndarray) or not isinstance(source, np.ndarray):
        raise TypeError("Both template and source must be numpy arrays. Ensure images are loaded correctly.")

    try:
        if not source.any():  # whenever an empty screenshot is taken
            return False, None
    except np.core._exceptions.UFuncTypeError:  # handle a very weird and rare error
        return False, None

    try:
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    except cv2.error as e:
        raise ValueError(
            f"Error converting images to grayscale. Ensure they are in a compatible color format. Details: {e}")

    try:
        result = cv2.matchTemplate(source_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # find the maximum match value and its location
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            # match found
            return True, max_loc
        else:
            # match not found
            return False, None
    except cv2.error as e:
        raise ValueError(f"Error during template matching. Details: {e}")


def match_template_all(template, source, threshold=0.8):
    if template is None or source is None:
        raise ValueError("Both template and source images must be provided and cannot be None.")

    if not isinstance(template, np.ndarray) or not isinstance(source, np.ndarray):
        raise TypeError("Both template and source must be numpy arrays. Ensure images are loaded correctly.")

    if not source.any():  # whenever an empty screenshot is taken
        return []

    try:
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        source_gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    except cv2.error as e:
        raise ValueError(
            f"Error converting images to grayscale. Ensure they are in a compatible color format. Details: {e}")

    try:
        result = cv2.matchTemplate(source_gray, template_gray, cv2.TM_CCOEFF_NORMED)

        # threshold the result to find all high enough matches
        loc = np.where(result >= threshold)

        matches = []
        for pt in zip(*loc[::-1]):  # Switch x and y coordinates
            matches.append((pt, result[pt[1], pt[0]]))

        return matches
    except cv2.error as e:
        raise ValueError(f"Error during template matching. Details: {e}")


def create_load_template(folder_root: Union[Path, str], cache_size=10):
    if not isinstance(folder_root, Path):
        folder_root = Path(folder_root)

    @lru_cache(maxsize=cache_size)
    def load_template(name: str):
        if '.' not in name:
            name = f"{name}.png"  # prepend .png extension if not provided
        template_path = folder_root / name

        if not template_path.exists():
            path_without_extension, _, extension = name.rpartition('.')
            alternate_path = folder_root / f"{path_without_extension}.jpg"
            #  ^ attempt to find .jpg file if .png file is not found
            if alternate_path.exists():
                log_colored(f"Warning! Template with extension '.png' not found. Using '.jpg' instead. ({name}).",
                            "yellow", "warning")
                template_path = alternate_path
            else:
                raise FailedToLoadTemplate(f"Error loading template image from path: {template_path}")
        template = cv2.imread(str(template_path))
        if template is None:
            raise FailedToLoadTemplate(f"Error loading template image from path: {template_path}")
        return template

    return load_template


def get_main_monitor_bounding_box(without_taskbar=False, taskbar_height=47):
    bounding_box = \
        [(monitor.x, monitor.y, monitor.width, monitor.height) for monitor in get_monitors() if monitor.is_primary][0]
    if without_taskbar:
        bounding_box = list(bounding_box)
        bounding_box[3] -= taskbar_height
    return bounding_box


def split_screenshot_into_rows(row_height: int, expected_rows: int = None, keep_last_incomplete_row: bool = True,
                               area: Union[Sequence, dict] = None) -> list:
    """
    Takes a screenshot of the specified area, splits it into rows of a given height,
    and returns each row as an image. Stops after reaching expected_rows if specified.

    :param row_height: The height of each row.
    :param expected_rows: The maximum number of rows to return. If None, processes the entire image.
    :param keep_last_incomplete_row: Whether to include the last row if it's shorter than row_height.
    :param area: The area to capture, defaults to full screen if None.
    :return: List of numpy arrays, each representing a row of the screenshot.
    """
    screenshot = screenshot_area(area)

    screenshot_height = screenshot.shape[0]
    rows = []

    row_count = 0
    while row_count * row_height < screenshot_height:
        # check if we have reached the specified expected rows
        if expected_rows is not None and row_count >= expected_rows:
            break

        # calculate the start and end of the current row
        start_y = row_count * row_height
        end_y = start_y + row_height

        # If the row height exceeds the screenshot height, handle the last row
        if end_y > screenshot_height:
            if keep_last_incomplete_row:
                rows.append(screenshot[start_y:screenshot_height, :, :])
            break

        # append the current row to the list
        rows.append(screenshot[start_y:end_y, :, :])
        row_count += 1

    return rows


def find_color_in_image(image, target_color):
    indices = np.where(np.all(image == target_color, axis=-1))

    return indices
