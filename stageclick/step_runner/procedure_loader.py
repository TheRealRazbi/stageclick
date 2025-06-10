# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

__all__ = ["_run_procedure", "run_procedure", "prettify_procedure_names", "get_procedures"]

import signal
import subprocess
from pathlib import Path

import sys
from termcolor import cprint


def _run_procedure(procedure, base_path):
    subprocess.run([sys.executable, f"{base_path}{procedure}.py"])


def run_procedure(procedure, base_path, name, supress_signals_during_procedure=True):
    original_signal = signal.getsignal(signal.SIGINT)
    try:
        if supress_signals_during_procedure:
            signal.signal(signal.SIGINT, lambda _, __: None)  # temporarily disable the interrupt signal
        cprint(f"Running procedure '{name}'...", "yellow")
        _run_procedure(procedure, base_path)
        cprint(f"Procedure '{name}' completed", "green")

    except KeyboardInterrupt:
        cprint("Procedure interrupted", "yellow")
    finally:
        if supress_signals_during_procedure:
            signal.signal(signal.SIGINT, original_signal)
        _procedure_running = False


def prettify_procedure_names(procedures):
    prettified_to_real = {name.replace("_", "-"): name for name in procedures}
    prettified_names = list(prettified_to_real.keys())
    return prettified_names, prettified_to_real


def get_procedures(search_path, blacklisted=('__init__',)):
    procedures = [p.stem for p in Path(search_path).glob("*.py") if p.stem not in blacklisted]
    return procedures
