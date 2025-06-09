def test_smoketest():
    import stageclick

    from stageclick import Window, WindowNotFound

    assert hasattr(stageclick, "Window")
    assert callable(Window)

    from stageclick.step_runner.runner import StepRunner

    assert hasattr(stageclick, "step_runner")
    assert callable(StepRunner)
