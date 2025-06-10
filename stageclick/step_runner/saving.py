# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["save_data_somewhere", "make_permanent", "load_latest_runner_data", "load_data_util", "create_load_command"]

import datetime
import json
from json import JSONDecodeError
from pathlib import Path
from typing import Optional, Any

from termcolor import cprint


def save_data_somewhere(data: any, base_path: Path, runner_name: str = "", silent_normal=False,
                        silent_errors=False) -> Optional[str]:
    """Returns the timestamp if the data was saved, otherwise None"""
    try:
        json.dumps(data)
    except JSONDecodeError:
        if not silent_errors:
            cprint("Data is not JSON serializable", "red")
        return

    base_path.mkdir(parents=True, exist_ok=True)
    save_path = base_path / "temp.json"
    existing = {}
    if save_path.exists():
        with open(save_path, "r") as f:
            existing = json.load(f)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if runner_name:
        if runner_name not in existing:
            existing[runner_name] = {}
        existing[runner_name][timestamp] = data
    else:
        existing[timestamp] = data
    with open(save_path, "w") as f:
        json.dump(existing, f, indent=2)
    if not silent_normal:
        cprint(f"Saved data '{json.dumps(data)}'", "green")
    return timestamp


def make_permanent(timestamp: str, base_path: Path, silent=False) -> None:
    save_path = base_path / "temp.json"
    if not save_path.exists():
        if not silent:
            cprint("No temporary data to save", "yellow")
        return

    with open(save_path, "r") as f:
        existing = json.load(f)

    if timestamp not in existing:
        if not silent:
            cprint(f"Timestamp '{timestamp}' not found", "red")
        return

    permanent_path = base_path / f"{timestamp}.json"
    with open(permanent_path, "w") as f:
        json.dump(existing[timestamp], f, indent=2)

    if not silent:
        cprint(f"Saved data permanently '{existing[timestamp]}'", "green")


def load_latest_runner_data(runner_name: str, base_path: Path) -> Optional[Any]:
    """
    Loads the latest data for a specific runner_name from temp.json.
    Returns None if runner_name not found or file doesn't exist.
    """
    save_path = base_path / "temp.json"

    if not save_path.exists():
        return None

    with open(save_path, "r") as f:
        existing = json.load(f)

    if runner_name not in existing:
        return None

    runner_data = existing[runner_name]
    if not runner_data:
        return None

    latest_timestamp = max(runner_data.keys())
    return runner_data[latest_timestamp]


def load_data_util(runner, base_path: Path) -> None:
    data = load_latest_runner_data(runner.name, base_path)
    if not data:
        cprint("No data found", "red")
        return
    cprint(f"Loaded {data}", "green")
    runner.state = data


def create_load_command(runner, base_path: Path):
    from stageclick.step_runner.commands import Command
    return Command("load", lambda: load_data_util(runner, base_path), short_error=False)
