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
pip install stage-click
```

## Usage
```py
import stageclick
print(stageclick.__version__)  # will be updated after more implementation is done
```


## Notes
It was not tested for linux