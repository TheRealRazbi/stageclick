from pathlib import Path
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "stageclick.experimental.screenshot_tools.screen_capture",
        [str(Path("stageclick/experimental/screenshot_tools/screen_capture.cpp"))],
        libraries=["user32", "gdi32", "dwmapi"],
        cxx_std=17,
    ),

]

setup(ext_modules=ext_modules, cmdclass={"build_ext": build_ext})
