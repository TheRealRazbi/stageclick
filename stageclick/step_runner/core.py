# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = [
    "_grab_input",
    "grab_input_once",
    "legacy_grab_input",
    "has_n_elements",
    "parse_list",
    "can_be_converted_type",
    "can_be_list_of_type",
    "can_be_list_of_ints",
    "is_done",
    "grab_y_n_bool",
    "PickFrom",
]

import inspect
from dataclasses import dataclass
from typing import Callable, Optional, Literal

from termcolor import colored, cprint


def _grab_input() -> str:
    return input(colored(">> ", "blue")).lower().strip()


def grab_input_once(break_func, process_result=lambda n: n):
    def inner(user_input: str):
        if break_func(user_input):
            return process_result(user_input)
        # raise ValueError("Invalid input format")

    return inner


def legacy_grab_input(break_func: Callable[[str], bool], process_result: Callable[[str], any] = lambda n: n,
                      commands: Optional[dict[str, Callable[[Optional[str]], any]]] = None) -> any:
    while True:
        res = _grab_input()
        if res == "skip":
            cprint("Skipped step", "yellow")
            return None
        if res == "help":
            commands_str = f"Commands: skip, help"
            if commands:
                commands_str = f"{commands_str}, {', '.join(commands.keys())}"
            cprint(commands_str, "yellow")
            continue
        if break_func(res):
            res = process_result(res)
            break
        if commands:
            command_name, *args = res.split(" ")
            if command_name in commands:
                func = commands[command_name]
                sig = inspect.signature(func)
                try:
                    func(*args[:len(sig.parameters)])
                except Exception as e:
                    cprint(e, "red")
                    continue
    return res


def has_n_elements(text: str, n: int, separator=", ") -> bool:
    return len(text.split(separator)) == n


def parse_list(text: str, type_: type, separator=", ") -> list[any]:
    return list(map(type_, text.split(separator)))


def can_be_converted_type(obj, type_) -> bool:
    try:
        type_(obj)
        return True
    except Exception:
        return False


def can_be_list_of_type(elements: list[str], type_):
    return all(map(lambda obj: can_be_converted_type(obj, type_), elements))


def can_be_list_of_ints(elements: list[str]):
    return can_be_list_of_type(elements, int)


def is_done(text: str) -> Callable[[str], Literal["done"]]:
    return grab_input_once(lambda n: n and n.lower() == "done", lambda n: "done")(text)


def grab_y_n_bool():
    return grab_input_once(lambda n: n in ('y', 'n'), lambda n: True if n == 'y' else False)


@dataclass
class PickFrom:
    collection: dict[str, any]  # name, value

    @property
    def options(self):
        return f"({', '.join(map(str, self.collection.keys()))})"

    def is_from(self, option: str):
        return option in self.collection

    def __getitem__(self, item):
        return self.collection[item]

    def grab_input(self, return_key=False):
        """Returns grab_input_once with preset options"""

        def _specific_is_from(option: str):
            if option not in self.collection and option.strip() != '':
                cprint(f"'{option}' doesn't exist", "red")
                return
            return True

        return grab_input_once(_specific_is_from,
                               lambda n, default=None: n if return_key else self.collection.get(n, default))
