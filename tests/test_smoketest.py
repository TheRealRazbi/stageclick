# Author: TheRealRazbi (https://github.com/TheRealRazbi)
# License: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

def test_smoketest():
    import stageclick

    from stageclick.core import Window, WindowNotFound

    assert hasattr(stageclick.core, "Window")
    assert callable(Window)

    from stageclick.step_runner.runner import StepRunner

    assert hasattr(stageclick, "step_runner")
    assert callable(StepRunner)
