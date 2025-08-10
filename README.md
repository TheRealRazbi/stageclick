# StageClick

**StageClick** is a template-focused mouse/keyboard controller window automation library for Windows.  
It is a wrapper to libraries like `pynput`, `pygetwindow`, `pyperclip`, `opencv`, `mss`

Features:
- Time-based retry template matching
- Tweaked pynput controllers (e.g.: the ability for a global pause button)
- Improved window detection and control
- Generic timing/retry utils
- Screenshot tools

## Installation

```bash
pip install stageclick
```

## Usage
```py
import stageclick
print(stageclick.__version__)  # will be updated after more implementation is done
```


## Notes
It has no linux support as of right now, but I am open to contributors, it shouldn't be that hard to add linux support. It just that the library is aimed at harsh GUI conditions and creating "APIs" where apps don't provide that, while linux lets you use the terminal nearly exclusively.