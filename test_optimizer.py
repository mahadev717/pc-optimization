# type: ignore
"""
Direct test — run this as Administrator to verify mouse tweaks actually apply.
Usage: Right-click Command Prompt > Run as Administrator > python test_optimizer.py
"""
import ctypes
import ctypes.wintypes
import winreg
import sys
import time

# Setup Windows API
user32 = ctypes.WinDLL('user32', use_last_error=True)
user32.SystemParametersInfoW.argtypes = [
    ctypes.wintypes.UINT, ctypes.wintypes.UINT,
    ctypes.c_void_p, ctypes.wintypes.UINT
]
user32.SystemParametersInfoW.restype = ctypes.wintypes.BOOL

SPI_SETMOUSE = 0x0004
SPI_GETMOUSE = 0x0003
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02

REG_PATH = r"Control Panel\Mouse"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def read_registry():
    """Read all mouse registry values."""
    values = {}
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ) as key:
        for name in ["MouseSpeed", "MouseThreshold1", "MouseThreshold2", "MouseSensitivity", "MouseTrails"]:
            try:
                val, reg_type = winreg.QueryValueEx(key, name)
                values[name] = val
            except FileNotFoundError:
                values[name] = "N/A"
    return values


def read_live_spi():
    """Read live SPI_GETMOUSE values (what Windows is actually using right now)."""
    params = (ctypes.c_int * 3)(0, 0, 0)
    result = user32.SystemParametersInfoW(SPI_GETMOUSE, 0, ctypes.cast(params, ctypes.c_void_p), 0)
    return {
        "LIVE_thresh1": params[0],
        "LIVE_thresh2": params[1],
        "LIVE_speed": params[2],
        "api_success": bool(result)
    }


def write_registry(speed, thresh1, thresh2, sensitivity):
    """Write mouse values to registry."""
    print(f"  Writing registry: Speed={speed}, Thresh1={thresh1}, Thresh2={thresh2}, Sensitivity={sensitivity}")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, str(speed))
        winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, str(thresh1))
        winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, str(thresh2))
        winreg.SetValueEx(key, "MouseSensitivity", 0, winreg.REG_SZ, str(sensitivity))
        winreg.SetValueEx(key, "MouseTrails", 0, winreg.REG_SZ, "0")
    print("  Registry write: OK")


def apply_spi(speed, thresh1, thresh2):
    """Call SystemParametersInfo to apply changes instantly."""
    print(f"  Calling SPI_SETMOUSE with [{thresh1}, {thresh2}, {speed}]...")
    params = (ctypes.c_int * 3)(thresh1, thresh2, speed)
    result = user32.SystemParametersInfoW(
        SPI_SETMOUSE, 0, ctypes.cast(params, ctypes.c_void_p),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    if result:
        print("  SPI_SETMOUSE: OK (applied instantly)")
    else:
        err = ctypes.get_last_error()
        print(f"  SPI_SETMOUSE: FAILED (error code: {err})")
    return result


def main():
    print("=" * 50)
    print("  MOUSE OPTIMIZER - DIRECT TEST")
    print("=" * 50)
    print()

    # Check admin
    if is_admin():
        print("[OK] Running as Administrator")
    else:
        print("[WARNING] NOT running as Administrator!")
        print("  Registry writes may still work (HKCU doesn't need admin)")
        print("  But some system calls might fail.")
    print()

    # Step 1: Read current state
    print("--- STEP 1: CURRENT STATE ---")
    reg_before = read_registry()
    live_before = read_live_spi()
    print(f"  Registry: {reg_before}")
    print(f"  Live SPI: {live_before}")
    print()

    # Step 2: Apply optimized values
    print("--- STEP 2: APPLYING OPTIMIZATIONS ---")
    try:
        write_registry(speed=0, thresh1=0, thresh2=0, sensitivity=10)
    except Exception as e:
        print(f"  [FAILED] Registry write error: {e}")
        return

    time.sleep(0.5)

    apply_spi(speed=0, thresh1=0, thresh2=0)
    print()

    # Step 3: Verify
    print("--- STEP 3: VERIFICATION ---")
    time.sleep(0.5)
    reg_after = read_registry()
    live_after = read_live_spi()
    print(f"  Registry: {reg_after}")
    print(f"  Live SPI: {live_after}")
    print()

    # Step 4: Compare
    print("--- RESULTS ---")
    reg_changed = reg_before != reg_after
    live_changed = live_before != live_after

    if reg_changed:
        print("  [OK] Registry values CHANGED successfully")
    else:
        print("  [FAIL] Registry values DID NOT change")

    if live_changed:
        print("  [OK] Live SPI values CHANGED (instant apply worked)")
    else:
        print("  [FAIL] Live SPI values DID NOT change")

    if live_after["LIVE_speed"] == 0 and live_after["LIVE_thresh1"] == 0:
        print("  [OK] Mouse acceleration is NOW DISABLED")
    else:
        print("  [FAIL] Mouse acceleration is STILL ENABLED")

    print()
    print("Go to: Settings > Bluetooth & devices > Mouse > Additional mouse settings")
    print("Check if 'Enhance pointer precision' is UNCHECKED.")
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
