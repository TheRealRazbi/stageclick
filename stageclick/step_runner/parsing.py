# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = [
    "parse_ints",
    "legacy_grab_ints",
    "grab_ints",
    "grab_int",
    "int_or_none",
    "treat_base16_as_base10",
]

from typing import Callable, Collection

from termcolor import cprint

from stageclick.step_runner.core import parse_list, grab_input_once, has_n_elements, can_be_list_of_ints, \
    legacy_grab_input


def parse_ints(text, *args, **kwargs) -> list[int]:
    return parse_list(text, int, *args, **kwargs)


def legacy_grab_ints(how_many: int, *args, **kwargs) -> list[int]:
    return legacy_grab_input(lambda t: has_n_elements(t, how_many) and can_be_list_of_ints(t.split(", ")),
                             lambda t: parse_list(t, int), *args, **kwargs)


def grab_ints(how_many: int, valid_values: Collection[int] = None, suppress_warning=False) -> Callable[
    [str], list[int]]:
    if how_many == 1 and not suppress_warning:
        cprint("Please use grab_int instead of grab_ints(1) as grab_ints(1) returns a list", "red")
    return grab_input_once(
        lambda t: has_n_elements(t, how_many) and can_be_list_of_ints(t.split(", ")) and
                  (valid_values is None or all(int(v) in valid_values for v in t.split(", "))),
        lambda t: parse_list(t, int)
    )


def grab_int(valid_values: Collection[int] = None, base16=False,
             extra_process: Callable[[int], int] = lambda n: n) -> Callable[[str], int]:
    base = 16 if base16 else 10

    def is_digit(t: str) -> bool:
        if not t:
            return False
        if base == 10:
            return t.isdigit()
        elif base == 16:
            return all(c.isdigit() or c.lower() in "abcdef" for c in t)

    return grab_input_once(
        lambda t: is_digit(t) and (valid_values is None or int(t, base) in valid_values),
        lambda n: extra_process(int(n, base))
    )


def int_or_none(text: str) -> int:
    return int(text) if text is not None else None


def treat_base16_as_base10(vp) -> str:
    return hex(vp)[2:]
