# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["StepRunner"]


import subprocess
from pathlib import Path
from typing import Any, Callable, Optional
from termcolor import cprint, colored

from stageclick.step_runner.commands import Command, execute_command, print_command_help, get_command, \
    CommandStatus
from stageclick.step_runner.saving import save_data_somewhere


class StepRunner:
    def __init__(self, name: str = "", base_path: Optional[Path] = None):
        self.name = name
        self.base_path: Optional[Path] = base_path
        self.state: dict[str, Any] = {}

    def step(self,
             title: str,
             input_func: Optional[Callable[[str], Any]] = None,
             wait_for: Optional[str] = None,
             commands: Optional[list[Command]] = None,
             save_key: Optional[str] = None,
             skip_allowed: bool = True,
             condition: Optional[Callable[[dict], bool]] = None) -> Any:

        if condition and not condition(self.state):
            return None

        print_title = self._create_print_title(title)
        print_title()
        if commands:
            print_command_help(commands)

        result = None
        attempt = 0
        while True:
            attempt += 1
            if attempt == 10:
                print_title()
                if commands:
                    print_command_help(commands)
                attempt = 0
            res = input(colored(">> ", "blue")).strip()
            if res.lower() == "skip":
                if skip_allowed:
                    cprint("Skipped step", "yellow")
                    return
                else:
                    cprint("Skipping not allowed", "red")
                    print_title()
                    continue
            if res.lower() == "help":
                print_command_help(commands or [])
                continue
            if res.lower() == "help-hidden":
                hidden = ["skip", "state", "save", "exit", "cls"]
                cprint("Hidden commands: " + ", ".join(hidden), "magenta")
                continue
            if res.lower() == "cls":
                subprocess.run('cls', shell=True)
                print_title()
                print_command_help(commands or [])
                continue
            if res.lower() == "state":
                cprint(self.state, "yellow")
                continue
            if res.lower() == "save":
                if self.base_path is None:
                    cprint("No base path set, cannot save", "red")
                else:
                    save_data_somewhere(self.state, self.base_path, self.name)
                continue
            if commands:
                command_status = execute_command(res, commands)
                if command_status == CommandStatus.STOP_STEP:
                    return

                if command_status != CommandStatus.FAILED:
                    command_name, *args = res
                    command = get_command(command_name, commands)
                    if command is not None:  # fallback
                        if command.show_help_after:
                            print_title()
                            print_command_help(commands)
                    # print_title()
                    # print_command_help(commands or [])
                    continue
            if wait_for and res == wait_for:
                break
            if res.lower() == "exit":
                cprint("Exiting...", "red")
                quit()
            if input_func:
                try:
                    result = input_func(res)
                    if result is None:
                        continue
                    break
                except Exception as e:
                    cprint(str(e), "red")
                    continue
            result = res

        if save_key:
            self.state[save_key] = result
        return result

    @staticmethod
    def _create_print_title(title):
        return lambda: cprint(title.strip(), "cyan")
