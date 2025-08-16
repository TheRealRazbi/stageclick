import ctypes

import cv2
import numpy as np
import win32con
import win32gui
import win32ui


def capture_hwnd_bitblit(hwnd):
    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bottom - top

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    src_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    mem_dc = src_dc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(src_dc, width, height)
    mem_dc.SelectObject(bmp)

    # bit block transfer into memory device context
    mem_dc.BitBlt((0, 0), (width, height), src_dc, (0, 0), win32con.SRCCOPY)

    # bmp_info = bmp.GetInfo()
    bmp_str = bmp.GetBitmapBits(True)

    win32gui.DeleteObject(bmp.GetHandle())
    mem_dc.DeleteDC()
    src_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    img = np.frombuffer(bmp_str, dtype=np.uint8)
    img = img.reshape((height, width, 4))  # BGRA format
    img = img[..., :3]  # drop alpha channel

    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def make_window_transparent(hwnd, alpha=0):
    """makes a window layered and transparent (alpha: 0-255)"""
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           ex_style | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, alpha, win32con.LWA_ALPHA)


def make_window_clickthrough(hwnd):
    """Makes the window ignore mouse events (click-through)"""
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           ex_style | win32con.WS_EX_TRANSPARENT)


def move_window(hwnd, x, y, w, h):
    """moves and resizes a window"""
    win32gui.MoveWindow(hwnd, x, y, w, h, True)


def hide_window(hwnd):
    """hides the window (won't be capturable by BitBlt, but will be captured by PrintWindow)"""
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)


def show_window(hwnd):
    """Shows the window again"""
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)


def stealthify_window(hwnd):
    # remove borders and title bar
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME | win32con.WS_SYSMENU |
               win32con.WS_MINIMIZEBOX | win32con.WS_MAXIMIZEBOX)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    # remove from taskbar
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    ex_style |= win32con.WS_EX_TOOLWINDOW
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOPMOST,
        0, 0, 400, 300,
        win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
    )

    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                           ex_style | win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 1, win32con.LWA_ALPHA)


def print_window_capture(hwnd):
    left, top, right, bot = win32gui.GetClientRect(hwnd)
    width = right - left
    height = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    result = ctypes.windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0x00000002)

    # bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    img = np.frombuffer(bmpstr, dtype='uint8')
    img.shape = (height, width, 4)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    else:
        raise RuntimeError("PrintWindow failed")
