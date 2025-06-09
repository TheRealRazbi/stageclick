# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["Command", "CommandStatus", "execute_command", "print_command_help", "get_command"]

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Optional
import inspect
import traceback
from termcolor import cprint


@dataclass
class Command:
    name: str
    func: Callable
    args: str = ""
    short_error: bool = True
    show_help_after: bool = False
    stop_step_if_returns_true: bool = False


class CommandStatus(Enum):
    FAILED = 0
    SUCCESS = 1
    STOP_STEP = 2


def execute_command(user_input: str, commands: list[Command]) -> CommandStatus:
    parts = user_input.strip().split()
    if not parts:
        return CommandStatus.FAILED

    command_name, *args = parts
    command = next((cmd for cmd in commands if cmd.name == command_name), None)
    if not command:
        return CommandStatus.FAILED

    func = command.func
    res = None
    try:
        sig = inspect.signature(func)
        if any(p.kind == p.VAR_POSITIONAL for p in sig.parameters.values()):
            res = func(*args)
        else:
            res = func(*args[:len(sig.parameters)])
    except Exception as e:
        if command.short_error:
            cprint(str(e), "red")
        else:
            traceback.print_exc()

    if command.stop_step_if_returns_true and res is True:
        return CommandStatus.STOP_STEP

    return CommandStatus.SUCCESS


def print_command_help(commands: list[Command]):
    if not commands:
        return
    line = "Commands: " + ", ".join(
        f"{cmd.name} {cmd.args}".strip() for cmd in commands
    )
    cprint(line, "yellow")


def get_command(name: str, commands: list[Command]) -> Optional[Command]:
    return next((cmd for cmd in commands if cmd.name == name), None)
