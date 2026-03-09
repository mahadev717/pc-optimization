# type: ignore
"""Headless optimizer — applies mouse tweaks and exits. No user input needed."""
import ctypes
import ctypes.wintypes
import winreg

user32 = ctypes.WinDLL('user32', use_last_error=True)
user32.SystemParametersInfoW.argtypes = [
    ctypes.wintypes.UINT, ctypes.wintypes.UINT,
    ctypes.c_void_p, ctypes.wintypes.UINT
]
user32.SystemParametersInfoW.restype = ctypes.wintypes.BOOL

REG_PATH = r"Control Panel\Mouse"

# 1. Write registry
with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
    winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
    winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
    winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
    winreg.SetValueEx(key, "MouseSensitivity", 0, winreg.REG_SZ, "10")
    winreg.SetValueEx(key, "MouseTrails", 0, winreg.REG_SZ, "0")

# 2. Apply instantly via SPI_SETMOUSE
params = (ctypes.c_int * 3)(0, 0, 0)
user32.SystemParametersInfoW(0x0004, 0, ctypes.cast(params, ctypes.c_void_p), 0x01 | 0x02)
