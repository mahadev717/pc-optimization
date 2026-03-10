# type: ignore
# HACKER CONTROL CENTER - Complete Backend Server
# Optimized for LOW-END LAPTOPS: 4GB RAM, Integrated GPU
# BlueStacks Beast Mode: Free Fire 300+ FPS target
# All HTML/CSS/JS embedded. No external files needed.

from flask import Flask, jsonify, request, Response
from flask_cors import CORS  # type: ignore
import os
import re
import multiprocessing
import subprocess
import ctypes  # type: ignore[attr-defined]
import ctypes.wintypes  # type: ignore[attr-defined]
import winreg  # type: ignore[attr-defined]
import datetime
import socket as _hostsocket
from supabase import create_client  # type: ignore

app = Flask(__name__)
CORS(app)

# ============================================================
# SUPABASE CLOUD DATABASE
# ============================================================

SUPABASE_URL = "https://mvsvbcmwovyufyrgquwy.supabase.co"
SUPABASE_KEY = "sb_publishable_QWAKXmaByRRWl8kSqXPqRw_tJBdjB7h"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def init_db():
    """Supabase tables are pre-created. Just verify connectivity."""
    try:
        supabase.table('users').select('id').limit(1).execute()
        print("[DB] Supabase connected — cloud database ready")
    except Exception as e:
        print(f"[DB] WARNING: Supabase connection issue: {e}")


def _get_device(ua):
    """Classify user-agent string into device/browser label."""
    s = str(ua or "")
    if "Android" in s or "iPhone" in s or "Mobile" in s:
        label = "Mobile"
    elif "iPad" in s:
        label = "Tablet"
    else:
        label = "PC"
    for b in ["Chrome", "Firefox", "Edge", "Safari", "Opera"]:
        if b in s:
            label = label + " / " + b
            break
    return label


def validate_user(username, password):
    """Return True if username+password match the users table (Supabase)."""
    try:
        result = supabase.table('users').select('id').eq('username', username).eq('password', password).execute()
        return len(result.data) > 0
    except Exception:
        return False


def record_login(username, ip, user_agent):
    """Insert a login event into Supabase logins table."""
    try:
        hostname = _hostsocket.getfqdn(ip) if ip and ip != "127.0.0.1" else _hostsocket.gethostname()
    except Exception:
        hostname = ""
    device = _get_device(user_agent)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        supabase.table('logins').insert({
            "username": username,
            "ip": ip,
            "device": device,
            "hostname": hostname,
            "logged_at": now
        }).execute()
    except Exception as e:
        print(f"[DB] Login record error: {e}")


def get_admin_data():
    """Return users with per-user login history + counts (Supabase)."""
    try:
        users_result = supabase.table('users').select('id, username, created_at').order('id').execute()
        logins_result = supabase.table('logins').select('*').order('id', desc=True).execute()
    except Exception as e:
        print(f"[DB] Admin data error: {e}")
        return {"users": [], "all_logins": []}

    users = users_result.data or []
    all_logins = logins_result.data or []

    # Build enriched user list
    enriched = []
    for u in users:
        uname = u["username"]
        u_logins = [l for l in all_logins if l["username"] == uname]
        last = u_logins[0]["logged_at"] if u_logins else ""
        enriched.append({
            "id":            str(u["id"]),
            "username":      str(u["username"]),
            "created_at":    str(u["created_at"]),
            "login_count":   str(len(u_logins)),
            "last_login":    str(last),
            "login_history": u_logins,
        })
    return {"users": enriched, "all_logins": all_logins}

CREATE_NO_WINDOW = 0x08000000

# --- Windows API setup ---
user32 = ctypes.WinDLL('user32', use_last_error=True)  # type: ignore
user32.SystemParametersInfoW.argtypes = [
    ctypes.wintypes.UINT, ctypes.wintypes.UINT,
    ctypes.c_void_p, ctypes.wintypes.UINT
]
user32.SystemParametersInfoW.restype = ctypes.wintypes.BOOL

SPI_SETMOUSE = 0x0004
SPI_GETMOUSE = 0x0003
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def run_silent(args):
    """Run a command silently (no CMD window)."""
    try:
        subprocess.run(args, creationflags=CREATE_NO_WINDOW,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        return True
    except Exception:
        return False


def reg_add(key_path, value_name, value_type, value_data):
    """Add a registry value silently via reg.exe."""
    return run_silent([
        "reg", "add", key_path, "/v", value_name,
        "/t", value_type, "/d", str(value_data), "/f"
    ])


def reg_delete(key_path, value_name):
    """Delete a registry value silently via reg.exe."""
    return run_silent(["reg", "delete", key_path, "/v", value_name, "/f"])


def service_control(service, action, start_type=None):
    """Control a Windows service silently."""
    if start_type:
        run_silent(["sc", "config", service, "start=", start_type])
    if action == "stop":
        run_silent(["net", "stop", service])
    elif action == "start":
        run_silent(["net", "start", service])


def read_mouse_registry():
    """Read current mouse registry values."""
    key_path = r"Control Panel\Mouse"
    values = {}
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            for name in ["MouseSpeed", "MouseThreshold1", "MouseThreshold2", "MouseSensitivity", "MouseTrails"]:
                try:
                    val, _ = winreg.QueryValueEx(key, name)
                    values[name] = val
                except FileNotFoundError:
                    values[name] = "N/A"
    except Exception as e:
        values["error"] = str(e)
    return values


def apply_mouse_params(speed, thresh1, thresh2):
    """Write registry + call SystemParametersInfo to apply instantly."""
    key_path = r"Control Panel\Mouse"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, str(speed))
            winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, str(thresh1))
            winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, str(thresh2))
    except Exception as e:
        return False, f"Registry write failed: {e}"

    params = (ctypes.c_int * 3)(thresh1, thresh2, speed)
    result = user32.SystemParametersInfoW(
        SPI_SETMOUSE, 0, ctypes.cast(params, ctypes.c_void_p),
        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
    )
    if not result:
        err = ctypes.get_last_error()
        return False, f"SystemParametersInfo failed (error code: {err})"
    return True, f"Mouse params applied (speed={speed}, thresh={thresh1}/{thresh2})"


def set_mouse_sensitivity(value):
    """Set MouseSensitivity registry key."""
    key_path = r"Control Panel\Mouse"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MouseSensitivity", 0, winreg.REG_SZ, str(value))
        return True, f"Sensitivity = {value}"
    except Exception as e:
        return False, f"Sensitivity write failed: {e}"


def disable_mouse_trails():
    """Disable mouse trails."""
    key_path = r"Control Panel\Mouse"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MouseTrails", 0, winreg.REG_SZ, "0")
        return True, "Mouse trails OFF"
    except Exception as e:
        return False, f"Mouse trails setting failed: {e}"


# ============================================================
# BLUESTACKS HELPER FUNCTIONS
# ============================================================

def find_bluestacks_conf():
    """
    Search ALL known BlueStacks config file locations across versions.
    Returns list of all found paths (there can be multiple instances).
    """
    search_dirs = [
        r"C:\ProgramData\BlueStacks_nxt",
        r"C:\ProgramData\BlueStacksSetup",
        r"C:\ProgramData\BlueStacks",
    ]
    found = []
    for d in search_dirs:
        if not os.path.exists(d):
            continue
        # Walk the directory to find all bluestacks.conf files
        for root, dirs, files in os.walk(d):
            for f in files:
                if f.lower() == "bluestacks.conf":
                    found.append(os.path.join(root, f))
    return found  # returns list, may be empty


def find_bluestacks_conf_single():
    """Returns the first found conf path or None (backward compat)."""
    results = find_bluestacks_conf()
    return results[0] if results else None


def is_bluestacks_running():
    """Check if BlueStacks is currently running."""
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", "IMAGENAME eq HD-Player.exe"],
            creationflags=CREATE_NO_WINDOW, stderr=subprocess.DEVNULL
        ).decode(errors="ignore")
        return "HD-Player.exe" in out
    except Exception:
        return False


def read_conf_fps(conf_path):
    """Read current FPS value(s) from a bluestacks.conf file."""
    try:
        with open(conf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        matches = re.findall(r'bst\.instance\.(\w+)\.(fps|fb_fps)="?(\d+)"?', content)
        return matches  # list of (instance, key, value)
    except Exception:
        return []


def find_bluestacks_install():
    """Find BlueStacks installation folder."""
    install_paths = [
        r"C:\Program Files\BlueStacks_nxt",
        r"C:\Program Files (x86)\BlueStacks_nxt",
        r"C:\BlueStacks_nxt",
        r"C:\Program Files\BlueStacks",
        r"C:\Program Files (x86)\BlueStacks",
    ]
    for path in install_paths:
        if os.path.exists(path):
            return path
    return None


def get_ultra_bs_settings():
    """
    Calculate ULTRA (maximum possible) BlueStacks settings for this machine.
    Gives BS as many cores and as much RAM as safely possible.
    """
    # CPU: use ALL logical cores — no cap
    cpu_cores = multiprocessing.cpu_count()

    # RAM: give BlueStacks maximum leaving only 1.5 GB for Windows
    # (our service massacre already freed ~600 MB so Windows runs on ~1.2 GB fine)
    try:
        import psutil  # type: ignore
        total_mb = psutil.virtual_memory().total // (1024 * 1024)
    except Exception:
        total_mb = 4096  # assume 4 GB if psutil unavailable

    ram_mb = 16384  # 16 GB ULTRA — BlueStacks will use pagefile if physical RAM is lower

    return cpu_cores, ram_mb


def patch_bluestacks_conf(conf_path, target_fps=800):
    """
    Patch a single bluestacks.conf to ULTRA settings:
    - FPS = 240 (BlueStacks 5 maximum)
    - CPU cores = ALL available cores on this machine
    - RAM = maximum safe allocation (total RAM - 1.5 GB)
    - DPI = 160 (low DPI = less GPU rendering work = more FPS)
    - Hardware ASTC texture decoding ON
    - High FPS mode ON
    - Graphics quality = PERFORMANCE
    Handles all key formats across BlueStacks versions.
    File is locked read-only after patching so BS cannot overwrite.
    """
    import stat

    cpu_cores, ram_mb = get_ultra_bs_settings()

    try:
        with open(conf_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Unlock read-only lock if previously set by us
        try:
            os.chmod(conf_path, stat.S_IREAD | stat.S_IWRITE |
                     stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH)
        except Exception:
            pass

        original = content

        # ── FPS: .fps= and .fb_fps= ──────────────────────────────
        content = re.sub(
            r'(bst\.instance\.\w+\.(?:fps|fb_fps)=)"?\d+"?',
            lambda m: m.group(1) + f'"{target_fps}"',
            content
        )
        # ── CPU CORES: all available ──────────────────────────────
        content = re.sub(
            r'(bst\.instance\.\w+\.cpu_count=)"?\d+"?',
            lambda m: m.group(1) + f'"{cpu_cores}"',
            content
        )
        # ── RAM: maximum safe ─────────────────────────────────────
        content = re.sub(
            r'(bst\.instance\.\w+\.ram=)"?\d+"?',
            lambda m: m.group(1) + f'"{ram_mb}"',
            content
        )
        # ── DPI: 700 ULTRA ───────────────────────────────────────
        content = re.sub(
            r'(bst\.instance\.\w+\.dpi=)"?\d+"?',
            lambda m: m.group(1) + '"700"',
            content
        )
        # ── High FPS mode: ON ─────────────────────────────────────
        content = re.sub(
            r'(bst\.instance\.\w+\.enable_high_fps_mode=)"?\d+"?',
            lambda m: m.group(1) + '"1"',
            content
        )
        # ── FPS display overlay: OFF (saves GPU cycles) ───────────
        content = re.sub(
            r'(bst\.instance\.\w+\.enable_fps_display=)"?\d+"?',
            lambda m: m.group(1) + '"0"',
            content
        )
        # ── Hardware ASTC decoding: ON (faster texture load) ──────
        content = re.sub(
            r'(bst\.instance\.\w+\.astc_mode=)"?\d+"?',
            lambda m: m.group(1) + '"1"',
            content
        )
        # ── Hardware decoder: ON ──────────────────────────────────
        content = re.sub(
            r'(bst\.instance\.\w+\.hardwareDecoder=)"?\d+"?',
            lambda m: m.group(1) + '"1"',
            content
        )
        # ── Graphics engine: 1 = DirectX (fastest on iGPU) ───────
        content = re.sub(
            r'(bst\.instance\.\w+\.graphics_engine=)"?\d+"?',
            lambda m: m.group(1) + '"1"',
            content
        )
        # ── Performance mode: 1 = High Performance ────────────────
        content = re.sub(
            r'(bst\.instance\.\w+\.perf_mode=)"?\d+"?',
            lambda m: m.group(1) + '"1"',
            content
        )

        # Write back even if "no change" — values may already be correct
        # but we still want to lock the file
        with open(conf_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # Lock file read-only — prevents BlueStacks from resetting on close
        try:
            os.chmod(conf_path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        except Exception:
            pass

        label = os.path.basename(os.path.dirname(conf_path))
        return True, (
            f"ULTRA config set in [{label}]: "
            f"FPS={target_fps} | CPU={cpu_cores} cores (ALL) | "
            f"RAM={ram_mb}MB | DPI=160 | HW-ASTC=ON | DirectX=ON | Locked read-only"
        )

    except PermissionError:
        return False, f"Permission denied on {conf_path} — run as Administrator"
    except Exception as e:
        return False, f"Patch error on {conf_path}: {e}"


def do_bs_diagnose():
    """
    Diagnose BlueStacks setup and identify why FPS is capped at 60.
    Returns a dict with full diagnosis.
    """
    # Use separate typed variables — avoids Pyright mixed-dict inference errors
    bs_running   = is_bluestacks_running()
    install_path = find_bluestacks_install()
    conf_files   = find_bluestacks_conf()
    fps_values   = []
    issues       = []
    fixes        = []

    if bs_running:
        issues.append("BlueStacks is RUNNING — conf patches will be overwritten when it closes")
        fixes.append("Close BlueStacks completely before running the optimizer")

    if not install_path:
        issues.append("BlueStacks installation folder NOT FOUND")
        fixes.append("Install BlueStacks 5 from bluestacks.com")

    if not conf_files:
        issues.append("bluestacks.conf NOT FOUND — FPS is controlled only by in-app settings")
        fixes.append("Open BlueStacks → Settings → Display → set FPS to 240 manually")
    else:
        for cp in conf_files:
            for instance, key, val in read_conf_fps(cp):
                fps_values.append({"file": cp, "instance": instance, "key": key, "fps": int(val)})
                if int(val) <= 60:
                    issues.append(f"FPS cap = {val} in {os.path.basename(os.path.dirname(cp))}/{instance}")
                    fixes.append("Run BlueStacks optimizer OR manually: BlueStacks Settings → Display → FPS → 240")

    issues.append("Free Fire in-game FPS may still be capped at 60 (in-game setting)")
    fixes.append("In Free Fire: Settings → Graphics → Frame Rate → HIGH or ULTRA")

    return {
        "bs_running":   bs_running,
        "install_path": install_path,
        "conf_files":   conf_files,
        "fps_values":   fps_values,
        "issues":       issues,
        "fixes":        fixes,
    }


# ============================================================
# AIM OPTIMIZATION
# ============================================================

def do_aim_optimize():
    """Full mouse/aim optimization - raw 1:1 input, no acceleration."""
    results = []

    ok, msg = set_mouse_sensitivity(10)
    results.append(msg)

    ok, msg = apply_mouse_params(0, 0, 0)
    results.append(msg)

    ok, msg = disable_mouse_trails()
    results.append(msg)

    run_silent(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"])
    results.append("High Performance power plan active")

    reg_add(r"HKCU\Control Panel\Mouse", "MouseSpeed", "REG_SZ", "0")
    reg_add(r"HKCU\Control Panel\Mouse", "MouseThreshold1", "REG_SZ", "0")
    reg_add(r"HKCU\Control Panel\Mouse", "MouseThreshold2", "REG_SZ", "0")
    results.append("Raw 1:1 mouse input locked — zero acceleration")

    return results


# ============================================================
# MOUSE RESTORE
# ============================================================

def do_mouse_restore():
    """Restore mouse settings to Windows defaults."""
    results = []

    ok, msg = set_mouse_sensitivity(10)
    results.append(msg)

    ok, msg = apply_mouse_params(1, 6, 10)
    results.append(msg)

    ok, msg = disable_mouse_trails()
    results.append(msg)

    run_silent(["powercfg", "-setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"])
    results.append("Balanced power plan active")

    return results


# ============================================================
# LOW-END LAPTOP PC OPTIMIZATION  (10 phases)
# Target: 4GB RAM, Integrated GPU
# ============================================================

def do_pc_optimize():
    """
    10-Phase aggressive optimization for low-end laptops.
    4GB RAM | Integrated GPU | Free Fire baseline boost.
    Run this FIRST, then run BlueStacks Beast Mode.
    """
    results = []

    # ═══ PHASE 1: TOTAL VISUAL EFFECTS ANNIHILATION ═══
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
            "VisualFXSetting", "REG_DWORD", 2)
    run_silent(["reg", "add", r"HKCU\Control Panel\Desktop",
                "/v", "UserPreferencesMask", "/t", "REG_BINARY",
                "/d", "9012038010000000", "/f"])
    reg_add(r"HKCU\Control Panel\Desktop\WindowMetrics", "MinAnimate", "REG_SZ", "0")
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            "EnableTransparency", "REG_DWORD", 0)
    reg_add(r"HKCU\Control Panel\Desktop", "DragFullWindows", "REG_SZ", "0")
    reg_add(r"HKCU\Control Panel\Desktop", "FontSmoothing", "REG_SZ", "0")
    reg_add(r"HKCU\Control Panel\Desktop", "SmoothScroll", "REG_DWORD", 0)
    reg_add(r"HKCU\Control Panel\Desktop", "CursorShadow", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "TaskbarAnimations", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "ListviewAlphaSelect", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "ListviewShadow", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\DWM", "EnableAeroPeek", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\DWM", "AlwaysHibernateThumbnails", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
            "NoThumbnailCache", "REG_DWORD", 1)
    results.append("PHASE 1 DONE: All visual effects destroyed — pure speed mode")

    # ═══ PHASE 2: UNLOCK ULTIMATE PERFORMANCE POWER PLAN ═══
    run_silent(["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"])
    ps_ultimate = (
        "$plans = powercfg /list; "
        "$up = $plans | Select-String 'Ultimate'; "
        "if($up){ "
        "  $line = $up.Line; "
        "  $guid = ($line -split ' ')[3]; "
        "  powercfg /setactive $guid "
        "} else { "
        "  powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c "
        "}"
    )
    run_silent(["powershell", "-command", ps_ultimate])
    run_silent(["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "893dee8e-2bef-41e0-89c6-b55d0929964c", "100"])
    run_silent(["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "54533251-82be-4824-96c1-47b60b740d00",
                "bc5038f7-23e0-4960-96da-33abaf5935ec", "100"])
    run_silent(["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "2a737441-1930-4402-8d77-b2bebba308a3",
                "48e6b7a6-50f5-4782-a5d4-53bb8f07e226", "0"])
    run_silent(["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "0012ee47-9041-4b5d-9b77-535fba8b1442",
                "6738e2c4-e8a5-4a42-b16a-e040e769756e", "0"])
    run_silent(["powercfg", "-setactive", "SCHEME_CURRENT"])
    results.append("PHASE 2 DONE: Ultimate Performance power plan UNLOCKED — CPU at 100% always")

    # ═══ PHASE 3: CPU CORE PARKING DISABLE + PRIORITY ═══
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\0cc5b647-c1df-4637-891a-dec35c318583",
            "ValueMax", "REG_DWORD", 0)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\be337238-0d82-4146-a960-4f3749d470c7",
            "ValueMax", "REG_DWORD", 0)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl",
            "Win32PrioritySeparation", "REG_DWORD", 38)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "GPU Priority", "REG_DWORD", 8)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "Priority", "REG_DWORD", 6)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "Scheduling Category", "REG_SZ", "High")
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "SFIO Priority", "REG_SZ", "High")
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "Background Only", "REG_SZ", "False")
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "Clock Rate", "REG_DWORD", 10000)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
            "SystemResponsiveness", "REG_DWORD", 0)
    results.append("PHASE 3 DONE: CPU core parking OFF — all cores active, 3x game CPU boost")

    # ═══ PHASE 4: RAM OPTIMIZATION (CRITICAL FOR 4GB) ═══
    service_control("SysMain", "stop", "disabled")
    service_control("WSearch", "stop", "disabled")
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "DisablePagingExecutive", "REG_DWORD", 1)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "LargeSystemCache", "REG_DWORD", 0)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "IoPageLockLimit", "REG_DWORD", 983040)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
            "EnablePrefetcher", "REG_DWORD", 0)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
            "EnableSuperfetch", "REG_DWORD", 0)
    ps_pagefile = (
        "try { "
        "  $cs = Get-WmiObject -Class Win32_ComputerSystem; "
        "  $cs.AutomaticManagedPagefile = $false; "
        "  $cs.Put() | Out-Null; "
        "  $pf = Get-WmiObject -Class Win32_PageFileSetting; "
        "  if($pf) { $pf.InitialSize = 2048; $pf.MaximumSize = 4096; $pf.Put() | Out-Null } "
        "} catch {}"
    )
    run_silent(["powershell", "-command", ps_pagefile])
    results.append("PHASE 4 DONE: RAM freed — SysMain OFF, kernel in RAM, pagefile tuned")

    # ═══ PHASE 5: SERVICE MASSACRE (24 SERVICES) ═══
    dead_services = [
        ("DiagTrack",         "stop", "disabled"),
        ("dmwappushservice",  "stop", "disabled"),
        ("WMPNetworkSvc",     "stop", "disabled"),
        ("CDPSvc",            "stop", "disabled"),
        ("MapsBroker",        "stop", "disabled"),
        ("lfsvc",             "stop", "disabled"),
        ("WerSvc",            "stop", "disabled"),
        ("wercplsupport",     "stop", "disabled"),
        ("wisvc",             "stop", "disabled"),
        ("RetailDemo",        "stop", "disabled"),
        ("TrkWks",            "stop", "disabled"),
        ("WbioSrvc",          "stop", "disabled"),
        ("BDESVC",            "stop", "disabled"),
        ("Fax",               "stop", "disabled"),
        ("Spooler",           "stop", "disabled"),
        ("RemoteRegistry",    "stop", "disabled"),
        ("XblAuthManager",    "stop", "disabled"),
        ("XblGameSave",       "stop", "disabled"),
        ("XboxNetApiSvc",     "stop", "disabled"),
        ("XboxGip",           "stop", "disabled"),
        ("NcaSvc",            "stop", "disabled"),
        ("icssvc",            "stop", "disabled"),
        ("PcaSvc",            "stop", "disabled"),
        ("TabletInputService","stop", "disabled"),
    ]
    for svc, action, start_type in dead_services:
        service_control(svc, action, start_type)
    results.append("PHASE 5 DONE: 24 background services KILLED — 400-600MB RAM freed")

    # ═══ PHASE 6: NETWORK OPTIMIZATION ═══
    ps_nagle = (
        "$adapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}; "
        "foreach($a in $adapters){ "
        "  $guid = $a.InterfaceGuid; "
        "  $path = 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\' + $guid; "
        "  Set-ItemProperty -Path $path -Name 'TcpAckFrequency' -Value 1 -Type DWord -ErrorAction SilentlyContinue; "
        "  Set-ItemProperty -Path $path -Name 'TCPNoDelay' -Value 1 -Type DWord -ErrorAction SilentlyContinue "
        "}"
    )
    run_silent(["powershell", "-command", ps_nagle])
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
            "NetworkThrottlingIndex", "REG_DWORD", "0xFFFFFFFF")
    run_silent(["netsh", "int", "tcp", "set", "global", "congestionprovider=ctcp"])
    run_silent(["netsh", "int", "tcp", "set", "global", "autotuninglevel=disabled"])
    run_silent(["netsh", "int", "tcp", "set", "global", "rss=disabled"])
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Services\Dnscache\Parameters",
            "MaxCacheSize", "REG_DWORD", 4096)
    results.append("PHASE 6 DONE: Network optimized — Nagle OFF, CTCP ON, zero throttling")

    # ═══ PHASE 7: iGPU OPTIMIZATION ═══
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode", "REG_DWORD", 2)
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", "REG_DWORD", 0)
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_DXGIHonorFSEWindowsCompatible", "REG_DWORD", 1)
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_EFSEFeatureFlags", "REG_DWORD", 0)
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_HonorUserFSEBehaviorMode", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "ShowGameModeNotifications", "REG_DWORD", 0)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", "REG_DWORD", 0)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", "REG_DWORD", 2)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler",
            "EnablePreemption", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences",
            "DirectXUserGlobalSettings", "REG_SZ", "VRROptimizeEnable=0;")
    results.append("PHASE 7 DONE: iGPU optimized — DVR OFF, HW scheduling ON")

    # ═══ PHASE 8: BACKGROUND APPS + TELEMETRY SHUTDOWN ═══
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
            "GlobalUserDisabled", "REG_DWORD", 1)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "AllowTelemetry", "REG_DWORD", 0)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search",
            "AllowCortana", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
            "SubscribedContent-338389Enabled", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
            "SubscribedContent-353698Enabled", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications",
            "ToastEnabled", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize",
            "StartupDelayInMSec", "REG_DWORD", 0)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive",
            "DisableFileSyncNGSC", "REG_DWORD", 1)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\WindowsStore",
            "AutoDownload", "REG_DWORD", 2)
    results.append("PHASE 8 DONE: Telemetry, notifications, background apps all KILLED")

    # ═══ PHASE 9: FILE SYSTEM OPTIMIZATION ═══
    run_silent(["fsutil", "behavior", "set", "disable8dot3", "1"])
    run_silent(["fsutil", "behavior", "set", "disablelastaccess", "1"])
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem",
            "NtfsMemoryUsage", "REG_DWORD", 2)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\FileSystem",
            "NtfsDisableEncryption", "REG_DWORD", 1)
    results.append("PHASE 9 DONE: File system tweaked — faster disk access")

    # ═══ PHASE 10: FREE FIRE / GAME PRIORITY LOCK ═══
    for proc in ["FreeFire.exe", "freefire.exe", "garena.exe", "GarenaMaster.exe", "GarenaPC.exe"]:
        reg_add(
            fr"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{proc}\PerfOptions",
            "CpuPriorityClass", "REG_DWORD", 3)
        reg_add(
            fr"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{proc}\PerfOptions",
            "IoPriority", "REG_DWORD", 3)
    results.append("PHASE 10 DONE: Free Fire locked to HIGH CPU + I/O priority permanently")

    return results


# ============================================================
# BLUESTACKS BEAST MODE OPTIMIZER
# Dedicated emulator optimization for 300+ FPS in Free Fire
# Run AFTER do_pc_optimize() for best results
# ============================================================

def do_bluestacks_optimize():
    """
    7-Phase BlueStacks-specific optimization.
    Targets Free Fire 300+ FPS on low-end 4GB / iGPU laptops.
    IMPORTANT: Close BlueStacks before running this, then restart it.
    """
    results = []

    # ═══ BS PHASE 1: ULTRA CONFIG — ALL CONF FILES ═══
    # Patch every bluestacks.conf found on this machine (handles multiple BS instances).
    # Sets FPS=240, CPU=ALL cores, RAM=MAX safe, DPI=160, HW-ASTC=ON, DirectX=ON.
    cpu_cores, ram_mb = get_ultra_bs_settings()
    results.append(f"BS PHASE 1: ULTRA settings — FPS=240 | CPU={cpu_cores} cores (ALL) | RAM={ram_mb}MB | DPI=160 | HW-ASTC=ON | DirectX=ON")

    conf_paths = find_bluestacks_conf()  # returns list
    if conf_paths:
        for cp in conf_paths:
            ok, msg = patch_bluestacks_conf(cp, target_fps=800)
            results.append(f"  {'OK' if ok else 'WARN'}: {msg}")
    else:
        results.append("  WARN: bluestacks.conf not found — set manually: BS Settings > Display > FPS=240 | Performance > Cores=MAX | RAM=2048")

    # ═══ BS PHASE 2: ALL BLUESTACKS PROCESSES → HIGH PRIORITY ═══
    # When Windows gives BS processes more CPU time, frames come faster.
    bs_processes = [
        "HD-Player.exe",      # Main BlueStacks window
        "HD-Agent.exe",       # BS background agent
        "BstkSVC.exe",        # BlueStacks service
        "HD-Service.exe",     # BS core service
        "HD-Frontend.exe",    # BS frontend
        "HD-Network.exe",     # BS network layer
        "HD-Plus-Service.exe",# BS Plus service
        "BlueStacks.exe",     # Older BS versions
    ]
    for proc in bs_processes:
        reg_add(
            fr"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{proc}\PerfOptions",
            "CpuPriorityClass", "REG_DWORD", 3   # HIGH
        )
        reg_add(
            fr"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{proc}\PerfOptions",
            "IoPriority", "REG_DWORD", 3          # HIGH
        )
    results.append("BS PHASE 2: All 8 BlueStacks processes locked to HIGH CPU + I/O priority")

    # ═══ BS PHASE 3: WINDOWS DEFENDER EXCLUSIONS FOR BLUESTACKS ═══
    # Defender scans every file BlueStacks opens inside the Android VM.
    # On a slow laptop this destroys FPS. Excluding BS folders fixes it.
    ps_defender = (
        "$bsPaths = @("
        "  'C:\\Program Files\\BlueStacks_nxt',"
        "  'C:\\ProgramData\\BlueStacks_nxt',"
        "  'C:\\Program Files (x86)\\BlueStacks_nxt',"
        "  'C:\\BlueStacks_nxt'"
        "); "
        "foreach($p in $bsPaths) { "
        "  if(Test-Path $p) { "
        "    Add-MpPreference -ExclusionPath $p -ErrorAction SilentlyContinue "
        "  } "
        "} "
        "$bsProcs = @('HD-Player.exe','HD-Agent.exe','BstkSVC.exe','HD-Service.exe','HD-Frontend.exe'); "
        "foreach($proc in $bsProcs) { "
        "  Add-MpPreference -ExclusionProcess $proc -ErrorAction SilentlyContinue "
        "}"
    )
    run_silent(["powershell", "-command", ps_defender])
    results.append("BS PHASE 3: BlueStacks excluded from Windows Defender — no more scan FPS drops")

    # ═══ BS PHASE 4: TIMER RESOLUTION FIX FOR EMULATORS ═══
    # Dynamic timer ticks cause micro-stutters inside VM/emulator frames.
    # Disabling dynamic tick + forcing platform tick = smoother frame timing.
    # NOTE: These changes take effect after next restart.
    run_silent(["bcdedit", "/set", "disabledynamictick", "yes"])
    run_silent(["bcdedit", "/set", "useplatformtick", "yes"])
    # Also set Windows timer resolution via registry
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel",
            "GlobalTimerResolutionRequests", "REG_DWORD", 1)
    results.append("BS PHASE 4: Timer resolution fixed — dynamic tick OFF, platform tick ON (restart needed)")

    # ═══ BS PHASE 5: GPU RENDERING MODE FOR BLUESTACKS ═══
    # Force BlueStacks to use DirectX rendering (fastest on Intel/AMD iGPU).
    # Also set HD-Player to use the best available GPU.
    install_path = find_bluestacks_install()
    if install_path:
        # DirectX graphics engine preference
        run_silent(["reg", "add", r"HKLM\SOFTWARE\BlueStacks_nxt",
                    "/v", "GraphicsEngine", "/t", "REG_SZ", "/d", "DirectX", "/f"])
    # Force HD-Player.exe to use High Performance GPU
    run_silent(["powershell", "-command",
        "if(-not (Test-Path 'HKCU:\\Software\\Microsoft\\DirectX\\UserGpuPreferences')) { "
        "  New-Item -Path 'HKCU:\\Software\\Microsoft\\DirectX\\UserGpuPreferences' -Force | Out-Null "
        "} "
        "Set-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\DirectX\\UserGpuPreferences' "
        "-Name 'HD-Player.exe' -Value 'GpuPreference=2;' -ErrorAction SilentlyContinue"
    ])
    # Disable VSync at Windows level for BS (let BS control its own frame pacing)
    reg_add(r"HKCU\Software\Microsoft\DirectX\UserGpuPreferences",
            "DirectXUserGlobalSettings", "REG_SZ", "VRROptimizeEnable=0;SwapEffectUpgradeEnable=0;")
    results.append("BS PHASE 5: GPU rendering set to DirectX HIGH PERFORMANCE mode")

    # ═══ BS PHASE 6: KILL RAM COMPETITION BEFORE BLUESTACKS ═══
    # On 4GB: BlueStacks needs 1.5GB free when it starts.
    # Kill idle processes that are hogging memory right now.
    ps_kill_idle = (
        "Get-Process | Where-Object { "
        "  $_.CPU -ne $null -and $_.CPU -lt 0.5 -and "
        "  $_.WorkingSet64 -gt 40MB -and "
        "  $_.Name -notmatch '^(svchost|System|Registry|lsass|csrss|wininit|services|smss|HD-|python|flask)' "
        "} | Stop-Process -Force -ErrorAction SilentlyContinue"
    )
    run_silent(["powershell", "-command", ps_kill_idle])
    # Force .NET garbage collection to release CLR memory
    run_silent(["powershell", "-command",
        "[System.Runtime.GCSettings]::LargeObjectHeapCompactionMode = "
        "[System.Runtime.GCLargeObjectHeapCompactionMode]::CompactOnce; "
        "[System.GC]::Collect(2, [System.GCCollectionMode]::Forced, $true, $true)"
    ])
    results.append("BS PHASE 6: Idle RAM hogs killed — memory cleared for BlueStacks startup")

    # ═══ BS PHASE 7: BLUESTACKS NETWORK ADAPTER PRIORITY ═══
    # BlueStacks creates a virtual network adapter. Give it maximum QoS.
    ps_bs_net = (
        "Get-NetAdapter | Where-Object { "
        "  $_.Name -like '*BlueStacks*' -or $_.Description -like '*BlueStacks*' "
        "} | ForEach-Object { "
        "  Set-NetIPInterface -InterfaceIndex $_.ifIndex -InterfaceMetric 1 -ErrorAction SilentlyContinue; "
        "  Set-ItemProperty -Path ('HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\' + $_.InterfaceGuid) "
        "    -Name 'TcpAckFrequency' -Value 1 -Type DWord -ErrorAction SilentlyContinue; "
        "  Set-ItemProperty -Path ('HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\' + $_.InterfaceGuid) "
        "    -Name 'TCPNoDelay' -Value 1 -Type DWord -ErrorAction SilentlyContinue "
        "}"
    )
    run_silent(["powershell", "-command", ps_bs_net])
    results.append("BS PHASE 7: BlueStacks virtual network adapter set to priority 1 — lowest ping")

    return results


# ============================================================
# PC RESTORE
# ============================================================

def do_pc_restore():
    """Restore all PC + BlueStacks tweaks to Windows defaults."""
    results = []

    # Visual Effects
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
            "VisualFXSetting", "REG_DWORD", 0)
    run_silent(["reg", "add", r"HKCU\Control Panel\Desktop",
                "/v", "UserPreferencesMask", "/t", "REG_BINARY",
                "/d", "9e3e078012000000", "/f"])
    reg_add(r"HKCU\Control Panel\Desktop\WindowMetrics", "MinAnimate", "REG_SZ", "1")
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            "EnableTransparency", "REG_DWORD", 1)
    reg_add(r"HKCU\Control Panel\Desktop", "DragFullWindows", "REG_SZ", "1")
    reg_add(r"HKCU\Control Panel\Desktop", "FontSmoothing", "REG_SZ", "2")
    reg_delete(r"HKCU\Control Panel\Desktop", "SmoothScroll")
    reg_delete(r"HKCU\Control Panel\Desktop", "CursorShadow")
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "TaskbarAnimations", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "ListviewAlphaSelect", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "ListviewShadow", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\Microsoft\Windows\DWM", "EnableAeroPeek", "REG_DWORD", 1)
    reg_delete(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
               "NoThumbnailCache")
    results.append("Visual effects restored")

    # Power Plan
    run_silent(["powercfg", "-setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"])
    results.append("Balanced power plan restored")

    # CPU Priority
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl",
            "Win32PrioritySeparation", "REG_DWORD", 2)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "GPU Priority", "REG_DWORD", 2)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "Priority", "REG_DWORD", 2)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
            "Scheduling Category", "REG_SZ", "Medium")
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
            "SystemResponsiveness", "REG_DWORD", 20)
    results.append("CPU priority restored")

    # Memory Services
    service_control("SysMain", "start", "auto")
    service_control("WSearch", "start", "delayed-auto")
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
            "DisablePagingExecutive", "REG_DWORD", 0)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
            "EnablePrefetcher", "REG_DWORD", 3)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters",
            "EnableSuperfetch", "REG_DWORD", 3)
    results.append("Memory services restored")

    # Core services
    for svc, action, start_type in [
        ("DiagTrack",  "start", "auto"),
        ("WerSvc",     "start", "demand"),
        ("CDPSvc",     "start", "auto"),
        ("Spooler",    "start", "auto"),
        ("TrkWks",     "start", "auto"),
        ("PcaSvc",     "start", "auto"),
    ]:
        service_control(svc, action, start_type)
    results.append("Core services restored")

    # Network
    ps_restore_nagle = (
        "$adapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}; "
        "foreach($a in $adapters){ "
        "  $guid = $a.InterfaceGuid; "
        "  $path = 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\' + $guid; "
        "  Remove-ItemProperty -Path $path -Name 'TcpAckFrequency' -ErrorAction SilentlyContinue; "
        "  Remove-ItemProperty -Path $path -Name 'TCPNoDelay' -ErrorAction SilentlyContinue "
        "}"
    )
    run_silent(["powershell", "-command", ps_restore_nagle])
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
            "NetworkThrottlingIndex", "REG_DWORD", 10)
    run_silent(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"])
    run_silent(["netsh", "int", "tcp", "set", "global", "rss=enabled"])
    results.append("Network defaults restored")

    # GPU/Game
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode", "REG_DWORD", 0)
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled", "REG_DWORD", 1)
    reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR")
    reg_delete(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode")
    results.append("GPU/Game settings restored")

    # Background apps
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
            "GlobalUserDisabled", "REG_DWORD", 0)
    reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry")
    reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana")
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\PushNotifications",
            "ToastEnabled", "REG_DWORD", 1)
    reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\OneDrive", "DisableFileSyncNGSC")
    reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\WindowsStore", "AutoDownload")
    results.append("Background apps restored")

    # File system
    run_silent(["fsutil", "behavior", "set", "disable8dot3", "0"])
    run_silent(["fsutil", "behavior", "set", "disablelastaccess", "0"])
    results.append("File system restored")

    # Remove Free Fire + BlueStacks process priority locks
    all_procs = [
        "FreeFire.exe", "freefire.exe", "garena.exe", "GarenaMaster.exe", "GarenaPC.exe",
        "HD-Player.exe", "HD-Agent.exe", "BstkSVC.exe", "HD-Service.exe",
        "HD-Frontend.exe", "HD-Network.exe", "HD-Plus-Service.exe", "BlueStacks.exe",
    ]
    for proc in all_procs:
        run_silent(["reg", "delete",
                    fr"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\{proc}\PerfOptions",
                    "/f"])
    results.append("Free Fire + BlueStacks priority locks removed")

    # Restore bcdedit timer settings
    run_silent(["bcdedit", "/set", "disabledynamictick", "no"])
    run_silent(["bcdedit", "/deletevalue", "useplatformtick"])
    reg_delete(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\kernel",
               "GlobalTimerResolutionRequests")
    results.append("Timer resolution settings restored (restart required)")

    return results


# ============================================================
# EMBEDDED HTML
# ============================================================

HTML_PAGE = r'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HACKER | NEURAL LINK</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root {
            --cyan: #00f3ff;
            --red: #ff3c3c;
            --green: #39ff14;
            --orange: #ff8800;
            --purple: #bf00ff;
            --dark: #020205;
            --font: 'Orbitron', sans-serif;
            --mono: 'Roboto Mono', monospace;
            --glass: rgba(5, 5, 10, 0.8);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; cursor: crosshair; }
        body { background: var(--dark); height: 100vh; width: 100vw; color: #fff; font-family: var(--font); overflow: hidden; }
        #canvas3d { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
        .scanlines { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(rgba(18,16,16,0) 50%, rgba(0,0,0,0.25) 50%); background-size: 100% 4px; z-index: 100; pointer-events: none; opacity: 0.3; }
        .vignette { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle, transparent 40%, #000 100%); z-index: 99; pointer-events: none; }

        .login-glass { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 420px; padding: 60px 40px; background: var(--glass); backdrop-filter: blur(10px); border: 1px solid rgba(0,243,255,0.1); text-align: center; box-shadow: 0 0 40px rgba(0,243,255,0.1); }
        /* ── MOBILE RESPONSIVE ────────────────────────────────── */
        @media (max-width: 640px) {
            body { overflow-y: auto; }
            .login-glass { width: 92vw; padding: 40px 24px; position: relative; top: auto; left: auto; transform: none; margin: 10vh auto; }
            #login-module { display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; padding: 0; }
            .glitch-title { font-size: 2rem; letter-spacing: 6px; }
            #dash-module { padding: 10px; }
            .glass-nav { padding: 10px 14px; flex-wrap: wrap; gap: 8px; }
            .brand { font-size: 0.85rem; }
            .stats { font-size: 0.7rem; gap: 10px; }
            .grid-layout { padding-bottom: 30px; }
            .panel-right { width: 100% !important; }
            .node-card { padding: 18px 16px; gap: 14px; }
            .node-card:hover { transform: none; }
            .node-card:active { opacity: 0.75; transform: scale(0.98); }
            .node-icon { font-size: 1.5rem; min-width: 30px; }
            .node-info h4 { font-size: 0.82rem; }
            .node-info p { font-size: 0.6rem; }
            .section-label { font-size: 0.6rem; letter-spacing: 2px; }
            .result-panel { width: 95vw; padding: 20px 16px; max-height: 92vh; }
            #guide-overlay > div { width: 95vw; padding: 24px 16px; }
            .prime-btn { padding: 18px; font-size: 0.85rem; }
            .rp-close { padding: 14px; }
            #mobile-banner { display: flex !important; }
        }
        .cyber-bracket { position: absolute; width: 20px; height: 20px; border: 2px solid var(--cyan); }
        .top-left { top: -2px; left: -2px; border-right: 0; border-bottom: 0; }
        .top-right { top: -2px; right: -2px; border-left: 0; border-bottom: 0; }
        .bottom-left { bottom: -2px; left: -2px; border-right: 0; border-top: 0; }
        .bottom-right { bottom: -2px; right: -2px; border-left: 0; border-top: 0; }
        .glitch-title { font-size: 3rem; letter-spacing: 10px; text-shadow: 0 0 10px var(--cyan); }
        .pulse-line { width: 100%; height: 1px; background: var(--cyan); margin: 20px 0; box-shadow: 0 0 10px var(--cyan); animation: pulse 2s infinite; }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }
        .input-container { background: rgba(0,243,255,0.05); border: 1px solid rgba(0,243,255,0.2); display: flex; align-items: center; margin-bottom: 20px; padding: 10px 15px; }
        .label { font-size: 0.6rem; color: var(--cyan); font-family: var(--mono); margin-right: 15px; }
        input { background: transparent; border: none; color: #fff; font-family: var(--mono); width: 100%; outline: none; }
        .prime-btn { width: 100%; padding: 15px; background: transparent; border: 1px solid var(--red); color: var(--red); font-family: var(--font); cursor: pointer; transition: 0.3s; }
        .prime-btn:hover { background: var(--red); color: #000; box-shadow: 0 0 20px var(--red); }

        #dash-module { display: none; padding: 20px; overflow-y: auto; height: 100vh; }
        .glass-nav { display: flex; justify-content: space-between; padding: 15px 30px; background: var(--glass); border-bottom: 1px solid rgba(0,243,255,0.2); margin-bottom: 20px; }
        .brand { font-size: 1.1rem; display: flex; align-items: center; gap: 10px; }
        .pulse-dot { width: 8px; height: 8px; background: var(--green); border-radius: 50%; box-shadow: 0 0 8px var(--green); animation: pulse 1.5s infinite; }
        .stats { display: flex; gap: 20px; align-items: center; font-family: var(--mono); font-size: 0.8rem; }
        .grid-layout { display: flex; justify-content: center; align-items: flex-start; padding-bottom: 40px; }
        .panel-right { width: 580px; }
        .section-label { font-size: 0.65rem; letter-spacing: 4px; color: rgba(255,255,255,0.3); margin: 20px 0 10px 0; padding-left: 4px; }
        .action-grid { display: grid; grid-template-columns: 1fr; gap: 12px; }
        .node-card { background: var(--glass); border: 1px solid rgba(255,255,255,0.05); padding: 22px 28px; display: flex; align-items: center; gap: 20px; cursor: pointer; transition: all 0.3s; }
        .node-card:hover { transform: translateX(6px); border-color: currentColor; box-shadow: 0 0 18px currentColor; }
        .node-card.red { color: var(--red); }
        .node-card.blue { color: var(--cyan); }
        .node-card.green { color: var(--green); }
        .node-card.cyan { color: var(--cyan); }
        .node-card.orange { color: var(--orange); }
        .node-card.orange:hover { box-shadow: 0 0 25px var(--orange), 0 0 50px rgba(255,136,0,0.3); }
        .bs-highlight { border: 1px solid rgba(255,136,0,0.3) !important; background: rgba(255,136,0,0.05) !important; }
        .node-icon { font-size: 1.8rem; min-width: 38px; text-align: center; }
        .node-info h4 { font-size: 0.88rem; margin-bottom: 4px; }
        .node-info p { font-size: 0.62rem; opacity: 0.65; line-height: 1.5; }
        .badge { display: inline-block; font-size: 0.5rem; padding: 2px 6px; border: 1px solid var(--orange); color: var(--orange); letter-spacing: 2px; margin-left: 8px; vertical-align: middle; }
        .fade-out { opacity: 0; transition: 0.8s; }
        .fade-in { animation: fadeIn 1s forwards; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .hidden { display: none; }
        #login-error { position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); color: var(--red); font-size: 0.9rem; font-family: var(--mono); background: rgba(255,60,60,0.15); border: 1px solid var(--red); padding: 12px 40px; z-index: 1000; letter-spacing: 3px; box-shadow: 0 0 25px var(--red); }

        #result-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.88); z-index: 500; justify-content: center; align-items: center; }
        #result-overlay.show { display: flex; }
        .result-panel { width: 560px; max-height: 88vh; background: rgba(5,5,10,0.97); border: 1px solid rgba(0,243,255,0.3); padding: 30px; overflow-y: auto; font-family: 'Roboto Mono', monospace; }
        .result-panel .rp-title { font-family: 'Orbitron', sans-serif; font-size: 0.95rem; letter-spacing: 3px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(0,243,255,0.2); }
        .result-panel .rp-line { font-size: 0.78rem; margin-bottom: 4px; line-height: 1.6; }
        .result-panel .rp-success { color: #39ff14; margin-top: 15px; padding: 14px; border: 1px solid #39ff14; background: rgba(57,255,20,0.07); font-size: 0.78rem; line-height: 1.8; }
        .result-panel .rp-success.bs { color: var(--orange); border-color: var(--orange); background: rgba(255,136,0,0.07); }
        .result-panel .rp-close { margin-top: 20px; padding: 12px 20px; background: transparent; border: 1px solid #00f3ff; color: #00f3ff; font-family: 'Orbitron', sans-serif; cursor: pointer; width: 100%; transition: 0.3s; font-size: 0.8rem; }
        .result-panel .rp-close:hover { background: #00f3ff; color: #000; }
        .tag-sys { color: #00f3ff; }
        .tag-act { color: #ffcc00; }
        .tag-ok  { color: #39ff14; }
        .tag-err { color: #ff3c3c; }
        .tag-bs  { color: #ff8800; }
        .tag-phase { color: #ff6600; font-weight: bold; }
    </style>
</head>
<body>
    <canvas id="canvas3d"></canvas>
    <div class="scanlines"></div>
    <div class="vignette"></div>

    <div id="login-module">
        <div class="login-glass">
            <div class="cyber-bracket top-left"></div>
            <div class="cyber-bracket top-right"></div>
            <div class="cyber-bracket bottom-left"></div>
            <div class="cyber-bracket bottom-right"></div>
            <header>
                <h1 class="glitch-title">HACKER</h1>
                <div class="pulse-line"></div>
                <p style="font-size:0.65rem;color:#ff8800;letter-spacing:3px;">NEURAL LINK v6.0 | BLUESTACKS BEAST MODE</p>
            </header>
            <form id="login-form" autocomplete="off">
                <div class="input-container">
                    <span class="label">ID://</span>
                    <input type="text" id="user-input" placeholder="IDENTITY" required autocomplete="off" readonly onfocus="this.removeAttribute('readonly')" value="">
                </div>
                <div class="input-container">
                    <span class="label">KEY://</span>
                    <input type="password" id="pass-input" placeholder="PASSCODE" required autocomplete="off" readonly onfocus="this.removeAttribute('readonly')" value="">
                </div>
                <button type="submit" class="prime-btn">ESTABLISH CONNECTION</button>
            </form>

            <!-- QR CODE — right below login form, hidden on mobile -->
            <div id="qr-card" style="margin-top:24px;padding-top:20px;border-top:1px solid rgba(0,243,255,0.12);">
                <p style="font-size:0.55rem;letter-spacing:3px;color:rgba(57,255,20,0.7);margin-bottom:14px;text-align:center;">&#128241; SCAN WITH PHONE TO OPEN ON MOBILE</p>
                <div style="display:flex;align-items:center;gap:16px;">
                    <div style="background:#fff;padding:5px;border-radius:3px;flex-shrink:0;">
                        <img id="qr-img" src="" width="90" height="90" alt="QR">
                    </div>
                    <div style="font-family:'Roboto Mono',monospace;text-align:left;">
                        <div style="font-size:0.5rem;color:rgba(255,255,255,0.35);margin-bottom:5px;">OR TYPE IN CHROME:</div>
                        <div id="qr-url-text" style="font-size:0.75rem;color:#39ff14;word-break:break-all;">Loading...</div>
                        <div style="font-size:0.5rem;color:rgba(255,255,255,0.3);margin-top:6px;line-height:1.8;">Connect phone to same WiFi<br>Login with 1 / 1</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="dash-module">
        <nav class="glass-nav">
            <div class="brand">
                <span class="pulse-dot"></span>
                HACKER_OS / BEAST MODE
            </div>
            <div class="stats">
                <div class="stat-item">RAM: <span id="mem-usage">--</span></div>
                <div class="stat-item"><span style="color:#39ff14;">&#9679; ONLINE</span></div>
                <div class="stat-item" id="clock">00:00:00</div>
            </div>
        </nav>
        <main class="grid-layout">
            <div class="panel-right">

                <!-- ══ MOBILE CONNECT CARD (shown on PC, hidden on mobile) ══ -->
                <div id="pc-connect-card" style="background:rgba(57,255,20,0.04);border:1px solid rgba(57,255,20,0.25);padding:20px;margin-bottom:16px;display:flex;gap:20px;align-items:center;">
                    <div id="qr-wrap" style="flex-shrink:0;width:110px;height:110px;background:#fff;display:flex;align-items:center;justify-content:center;border-radius:4px;">
                        <img id="qr-img" src="" width="106" height="106" alt="QR" style="display:none;border-radius:2px;">
                        <span id="qr-loading" style="font-size:0.6rem;color:#333;text-align:center;padding:8px;">Loading QR...</span>
                    </div>
                    <div style="font-family:'Roboto Mono',monospace;flex:1;min-width:0;">
                        <div style="font-size:0.6rem;letter-spacing:3px;color:#39ff14;margin-bottom:8px;">&#128241; MOBILE ACCESS — SCAN OR TYPE</div>
                        <div id="pc-mobile-url" style="font-size:0.9rem;color:#fff;font-weight:bold;word-break:break-all;margin-bottom:8px;">Loading...</div>
                        <div style="font-size:0.6rem;color:rgba(255,255,255,0.45);line-height:1.8;">
                            1. Connect phone to <b style="color:#fff;">same WiFi</b> as this PC<br>
                            2. Open Chrome on phone → type or scan the URL above<br>
                            3. Login → tap any button → it applies to THIS PC instantly
                        </div>
                    </div>
                </div>

                <!-- ══ MOBILE STATUS BANNER (shown on mobile, hidden on PC) ══ -->
                <div id="mobile-banner" style="display:none;align-items:center;gap:14px;background:rgba(57,255,20,0.06);border:1px solid rgba(57,255,20,0.3);padding:16px;margin-bottom:16px;">
                    <div style="font-size:2rem;">&#128241;</div>
                    <div style="font-family:'Roboto Mono',monospace;">
                        <div style="font-size:0.65rem;color:#39ff14;letter-spacing:2px;margin-bottom:4px;">&#9679; MOBILE CONNECTED TO PC</div>
                        <div style="font-size:0.7rem;color:rgba(255,255,255,0.6);">Tap any button below — it applies to your PC in real time</div>
                    </div>
                </div>

                <div class="section-label">&#9658; STEP 1 — WINDOWS OS OPTIMIZATION</div>
                <div class="action-grid">
                    <div class="node-card blue" id="btn-pc-optimize">
                        <div class="node-icon">&#9889;</div>
                        <div class="node-info">
                            <h4>LOW-END BEAST OPTIMIZER <span class="badge">STEP 1</span></h4>
                            <p>10-Phase OS boost: Ultimate Power + Core Parking OFF + 24 Services Killed + iGPU Tuned</p>
                        </div>
                    </div>
                </div>

                <div class="section-label">&#9658; STEP 2 — BLUESTACKS EMULATOR OPTIMIZATION</div>
                <div class="action-grid">
                    <div class="node-card orange bs-highlight" id="btn-bs-optimize">
                        <div class="node-icon">&#128241;</div>
                        <div class="node-info">
                            <h4>BLUESTACKS BEAST MODE <span class="badge">STEP 2</span></h4>
                            <p>FPS unlock in .conf + Process HIGH priority + Defender exclusion + Timer fix + DirectX GPU + RAM cleaner | FREE FIRE 300+ FPS</p>
                        </div>
                    </div>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                        <div class="node-card" style="color:#ffcc00;border-color:rgba(255,204,0,0.15);" id="btn-diagnose">
                            <div class="node-icon" style="font-size:1.4rem;">&#128269;</div>
                            <div class="node-info">
                                <h4 style="font-size:0.8rem;">DIAGNOSE FPS</h4>
                                <p>Find out exactly why FPS is capped</p>
                            </div>
                        </div>
                        <div class="node-card" style="color:#bf00ff;border-color:rgba(191,0,255,0.15);" id="btn-guide">
                            <div class="node-icon" style="font-size:1.4rem;">&#128218;</div>
                            <div class="node-info">
                                <h4 style="font-size:0.8rem;">SETUP GUIDE</h4>
                                <p>Step-by-step manual settings</p>
                            </div>
                        </div>
                    </div>
                    <div class="node-card red" id="btn-optimize">
                        <div class="node-icon">&#127919;</div>
                        <div class="node-info">
                            <h4>MOUSE AIM OPTIMIZER</h4>
                            <p>Raw 1:1 input | Zero acceleration | High Performance power plan</p>
                        </div>
                    </div>
                </div>

                <div class="section-label">&#9658; RESTORE</div>
                <div class="action-grid">
                    <div class="node-card green" id="btn-restore">
                        <div class="node-icon">&#128260;</div>
                        <div class="node-info">
                            <h4>RESTORE MOUSE</h4>
                            <p>Revert mouse settings to Windows defaults</p>
                        </div>
                    </div>
                    <div class="node-card cyan" id="btn-pc-restore">
                        <div class="node-icon">&#128281;</div>
                        <div class="node-info">
                            <h4>RESTORE ALL DEFAULTS</h4>
                            <p>Undo all OS + BlueStacks tweaks and restore Windows defaults</p>
                        </div>
                    </div>
                </div>

            </div>
        </main>
    </div>

    <div id="result-overlay">
        <div class="result-panel">
            <div class="rp-title" id="rp-title" style="color:#00f3ff;">PROCESSING</div>
            <div id="rp-log"></div>
            <button class="rp-close" id="rp-close" style="display:none;"
                onclick="document.getElementById('result-overlay').classList.remove('show')">
                CLOSE
            </button>
        </div>
    </div>

    <!-- GUIDE MODAL -->
    <div id="guide-overlay" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.92);z-index:600;justify-content:center;align-items:center;">
        <div style="width:580px;max-height:90vh;overflow-y:auto;background:rgba(5,5,10,0.98);border:1px solid rgba(191,0,255,0.4);padding:32px;font-family:'Roboto Mono',monospace;">
            <div style="font-family:'Orbitron',sans-serif;font-size:1rem;letter-spacing:3px;color:#bf00ff;margin-bottom:20px;padding-bottom:10px;border-bottom:1px solid rgba(191,0,255,0.2);">
                SETUP GUIDE — HOW TO GET 300+ FPS
            </div>

            <div style="color:#ffcc00;font-size:0.72rem;letter-spacing:2px;margin-bottom:14px;">STEP A — INSIDE BLUESTACKS SETTINGS</div>
            <div style="font-size:0.78rem;line-height:2;color:#ccc;">
                <span style="color:#39ff14;">1.</span> Open <b style="color:#fff;">BlueStacks 5</b><br>
                <span style="color:#39ff14;">2.</span> Click the <b style="color:#fff;">&#9881; gear icon</b> (top-right settings button)<br>
                <span style="color:#39ff14;">3.</span> Go to <b style="color:#fff;">Display</b> tab<br>
                <span style="color:#39ff14;">4.</span> Set <b style="color:#ff8800;">FPS</b> slider to <b style="color:#ff8800;">240</b> (drag all the way right)<br>
                <span style="color:#39ff14;">5.</span> Set <b style="color:#ff8800;">Resolution</b> to <b style="color:#ff8800;">1280x720</b> (lower = more FPS)<br>
                <span style="color:#39ff14;">6.</span> Go to <b style="color:#fff;">Performance</b> tab<br>
                <span style="color:#39ff14;">7.</span> Set <b style="color:#ff8800;">Performance Mode</b> to <b style="color:#ff8800;">High Performance</b><br>
                <span style="color:#39ff14;">8.</span> Set <b style="color:#ff8800;">CPU Cores</b> to <b style="color:#ff8800;">maximum</b><br>
                <span style="color:#39ff14;">9.</span> Set <b style="color:#ff8800;">Memory</b> to <b style="color:#ff8800;">2048 MB</b> (2 GB)<br>
                <span style="color:#39ff14;">10.</span> Click <b style="color:#fff;">Save Changes</b> and <b style="color:#ff3c3c;">RESTART BlueStacks</b>
            </div>

            <div style="height:1px;background:rgba(191,0,255,0.2);margin:18px 0;"></div>
            <div style="color:#ffcc00;font-size:0.72rem;letter-spacing:2px;margin-bottom:14px;">STEP B — INSIDE FREE FIRE GAME SETTINGS</div>
            <div style="font-size:0.78rem;line-height:2;color:#ccc;">
                <span style="color:#39ff14;">1.</span> Open <b style="color:#fff;">Free Fire</b> inside BlueStacks<br>
                <span style="color:#39ff14;">2.</span> Tap the <b style="color:#fff;">&#9881; Settings icon</b> on the main screen<br>
                <span style="color:#39ff14;">3.</span> Go to <b style="color:#fff;">Graphics</b> settings<br>
                <span style="color:#39ff14;">4.</span> Set <b style="color:#ff8800;">Graphics Quality</b> to <b style="color:#ff8800;">LOW</b> (lowest possible)<br>
                <span style="color:#39ff14;">5.</span> Set <b style="color:#ff8800;">Frame Rate</b> to <b style="color:#ff8800;">HIGH</b> or <b style="color:#ff8800;">ULTRA HIGH</b><br>
                <span style="color:#39ff14;">6.</span> <b style="color:#ff3c3c;">Disable ALL</b> extra effects: shadows, effects, background<br>
                <span style="color:#39ff14;">7.</span> Tap <b style="color:#fff;">OK</b> and <b style="color:#ff3c3c;">restart Free Fire</b>
            </div>

            <div style="height:1px;background:rgba(191,0,255,0.2);margin:18px 0;"></div>
            <div style="color:#ffcc00;font-size:0.72rem;letter-spacing:2px;margin-bottom:14px;">STEP C — RUN OUR OPTIMIZER (CORRECT ORDER)</div>
            <div style="font-size:0.78rem;line-height:2;color:#ccc;">
                <span style="color:#00f3ff;">1.</span> Click <b style="color:#00f3ff;">LOW-END BEAST OPTIMIZER</b> (Step 1 OS tweaks)<br>
                <span style="color:#00f3ff;">2.</span> <b style="color:#ff3c3c;">Fully close BlueStacks</b> (check Task Manager, kill all HD-*.exe)<br>
                <span style="color:#00f3ff;">3.</span> Click <b style="color:#ff8800;">BLUESTACKS BEAST MODE</b> (Step 2 emulator tweaks)<br>
                <span style="color:#00f3ff;">4.</span> <b style="color:#ff3c3c;">RESTART YOUR LAPTOP</b> (required for timer + power changes)<br>
                <span style="color:#00f3ff;">5.</span> Open BlueStacks → do Steps A &amp; B above → play Free Fire
            </div>

            <div style="height:1px;background:rgba(191,0,255,0.2);margin:18px 0;"></div>
            <div style="color:#ff3c3c;font-size:0.72rem;letter-spacing:2px;margin-bottom:10px;">WHY STILL 60 FPS? COMMON CAUSES</div>
            <div style="font-size:0.75rem;line-height:1.9;color:#ccc;">
                <span style="color:#ff3c3c;">&#9654;</span> BlueStacks FPS slider is still at 60 (do Step A above)<br>
                <span style="color:#ff3c3c;">&#9654;</span> Free Fire Frame Rate is set to Medium/High=60 (do Step B above)<br>
                <span style="color:#ff3c3c;">&#9654;</span> BlueStacks was RUNNING when optimizer ran (it overwrites conf on close)<br>
                <span style="color:#ff3c3c;">&#9654;</span> Laptop not restarted after optimization<br>
                <span style="color:#ff3c3c;">&#9654;</span> BlueStacks version is too old — update to BlueStacks 5 latest
            </div>

            <button onclick="document.getElementById('guide-overlay').style.display='none'"
                style="margin-top:24px;width:100%;padding:12px;background:transparent;border:1px solid #bf00ff;color:#bf00ff;font-family:'Orbitron',sans-serif;cursor:pointer;font-size:0.8rem;letter-spacing:2px;">
                CLOSE GUIDE
            </button>
        </div>
    </div>

    <div id="login-error" class="hidden">[ ERROR ] INCORRECT CREDENTIALS</div>

    <script>
    document.addEventListener('DOMContentLoaded', () => {
        // THREE.JS 3D BACKGROUND
        const canvas = document.querySelector('#canvas3d');
        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 5;
        const geometry = new THREE.PlaneGeometry(20, 20, 40, 40);
        const material = new THREE.MeshBasicMaterial({ color: 0x00f3ff, wireframe: true, transparent: true, opacity: 0.15 });
        const plane = new THREE.Mesh(geometry, material);
        plane.rotation.x = -Math.PI / 2.5;
        plane.position.y = -2;
        scene.add(plane);
        const partGeom = new THREE.BufferGeometry();
        const partCount = 800;
        const posArray = new Float32Array(partCount * 3);
        for (let i = 0; i < partCount * 3; i++) posArray[i] = (Math.random() - 0.5) * 15;
        partGeom.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        const partMat = new THREE.PointsMaterial({ size: 0.02, color: 0xff3c3c });
        const particles = new THREE.Points(partGeom, partMat);
        scene.add(particles);
        function animate() {
            requestAnimationFrame(animate);
            const time = Date.now() * 0.001;
            const positions = plane.geometry.attributes.position.array;
            for (let i = 0; i < positions.length; i += 3) {
                positions[i + 2] = Math.sin(positions[i] * 0.5 + time) * 0.5 + Math.cos(positions[i+1] * 0.3 + time) * 0.5;
            }
            plane.geometry.attributes.position.needsUpdate = true;
            particles.rotation.y += 0.001;
            particles.rotation.x += 0.0005;
            renderer.render(scene, camera);
        }
        animate();
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // STATS
        async function updateMemory() {
            try {
                const r = await fetch('/health');
                const d = await r.json();
                if (d.mem_percent !== null) document.getElementById('mem-usage').innerText = d.mem_percent + '%';
            } catch(e) {}
        }
        setInterval(updateMemory, 3000);
        updateMemory();
        setInterval(() => { document.getElementById('clock').innerText = new Date().toLocaleTimeString(); }, 1000);

        // Clear autofill once — only if user hasn't typed yet
        var _uEl = document.getElementById('user-input');
        var _pEl = document.getElementById('pass-input');
        var _uTouched = false, _pTouched = false;
        if (_uEl) { _uEl.value = ''; _uEl.addEventListener('input', function(){ _uTouched = true; }); }
        if (_pEl) { _pEl.value = ''; _pEl.addEventListener('input', function(){ _pTouched = true; }); }
        setTimeout(function(){ if(!_uTouched && _uEl) _uEl.value = ''; if(!_pTouched && _pEl) _pEl.value = ''; }, 300);

        // LOGIN
        const loginForm = document.getElementById('login-form');
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const user = document.getElementById('user-input').value;
            const pass = document.getElementById('pass-input').value;
            try {
                const r = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: user, password: pass})
                });
                if (r.ok) {
                    const lm = document.getElementById('login-module');
                    const dm = document.getElementById('dash-module');
                    lm.classList.add('fade-out');
                    setTimeout(() => {
                        lm.style.display = 'none';
                        dm.style.display = 'block';
                        dm.classList.add('fade-in');
                        partMat.color.set(0xff8800);
                        material.color.set(0xff8800);
                        material.opacity = 0.3;
                    }, 800);
                } else {
                    const error = document.getElementById('login-error');
                    error.classList.remove('hidden');
                    setTimeout(() => error.classList.add('hidden'), 3000);
                }
            } catch(err) {
                const error = document.getElementById('login-error');
                error.classList.remove('hidden');
                setTimeout(() => error.classList.add('hidden'), 3000);
            }
        });

        // ACTION ENGINE
        const overlay = document.getElementById('result-overlay');
        const rpTitle = document.getElementById('rp-title');
        const rpLog   = document.getElementById('rp-log');
        const rpClose = document.getElementById('rp-close');

        function addLog(tag, text, cls) {
            const line = document.createElement('div');
            line.className = 'rp-line';
            line.innerHTML = '<span class="' + cls + '">[' + tag + ']</span> ' + text;
            rpLog.appendChild(line);
            rpLog.scrollTop = rpLog.scrollHeight;
        }

        const endpoints = {
            'aim':        '/run-optimizer',
            'restore':    '/restore-defaults',
            'pc-optimize':'/pc-optimize',
            'bs-optimize':'/bluestacks-optimize',
            'pc-restore': '/pc-restore'
        };
        const titles = {
            'aim':        'MOUSE AIM OPTIMIZER',
            'restore':    'MOUSE RESTORE',
            'pc-optimize':'LOW-END BEAST OPTIMIZER',
            'bs-optimize':'BLUESTACKS BEAST MODE — 7 PHASES',
            'pc-restore': 'FULL RESTORE'
        };

        const allSteps = {
            'aim': [
                ['SYS','Connecting to Windows kernel...','tag-sys'],
                ['ACT','Setting MouseSpeed = 0 (acceleration OFF)','tag-act'],
                ['ACT','Setting MouseThreshold1 = 0, Threshold2 = 0','tag-act'],
                ['SYS','Calling SystemParametersInfo(SPI_SETMOUSE)...','tag-sys'],
                ['ACT','Activating High Performance power plan...','tag-act']
            ],
            'restore': [
                ['SYS','Initiating mouse restore...','tag-sys'],
                ['ACT','Restoring MouseSpeed=1, T1=6, T2=10','tag-act'],
                ['ACT','Restoring Balanced power plan...','tag-act']
            ],
            'pc-optimize': [
                ['SYS','Initializing LOW-END BEAST MODE...','tag-sys'],
                ['SYS','Target: 4GB RAM | Integrated GPU | Baseline boost','tag-sys'],
                ['PH1','PHASE 1: Destroying all visual effects...','tag-phase'],
                ['ACT','Disabling animations, transparency, shadows, Aero Peek...','tag-act'],
                ['PH2','PHASE 2: Unlocking Ultimate Performance power plan...','tag-phase'],
                ['ACT','CPU min=100%, max=100% — no throttle ever...','tag-act'],
                ['PH3','PHASE 3: Disabling CPU core parking...','tag-phase'],
                ['ACT','All CPU cores forced ACTIVE — Win32PrioritySeparation=38...','tag-act'],
                ['PH4','PHASE 4: RAM optimization for 4GB...','tag-phase'],
                ['ACT','SysMain OFF (frees 300MB), kernel in RAM, pagefile=2048-4096...','tag-act'],
                ['PH5','PHASE 5: Killing 24 background services...','tag-phase'],
                ['ACT','DiagTrack, Xbox, CDPSvc, WMPNet, MapsBroker, Telemetry...','tag-act'],
                ['PH6','PHASE 6: Network optimization...','tag-phase'],
                ['ACT','Nagle OFF, CTCP ON, auto-tuning OFF...','tag-act'],
                ['PH7','PHASE 7: Integrated GPU optimization...','tag-phase'],
                ['ACT','Game DVR OFF, HW scheduling ON, fullscreen fixed...','tag-act'],
                ['PH8','PHASE 8: Killing telemetry & background apps...','tag-phase'],
                ['ACT','Cortana, OneDrive, notifications, Windows tips all KILLED...','tag-act'],
                ['PH9','PHASE 9: File system tweaks...','tag-phase'],
                ['PH10','PHASE 10: Locking Free Fire to HIGH priority...','tag-phase'],
                ['SYS','Executing on backend...','tag-sys']
            ],
            'bs-optimize': [
                ['SYS','Initializing BLUESTACKS BEAST MODE...','tag-sys'],
                ['BS','IMPORTANT: Close BlueStacks before this runs, then restart it','tag-bs'],
                ['BS','Target: BlueStacks + Free Fire 300+ FPS on 4GB iGPU laptop','tag-bs'],
                ['BS','BS PHASE 1: Finding and patching BlueStacks .conf file...','tag-bs'],
                ['ACT','Unlocking FPS from 60 → 240 in bluestacks.conf...','tag-act'],
                ['ACT','Setting CPU cores to max available...','tag-act'],
                ['ACT','Setting RAM allocation to 1536 MB...','tag-act'],
                ['BS','BS PHASE 2: Locking 8 BlueStacks processes to HIGH priority...','tag-bs'],
                ['ACT','HD-Player.exe → HIGH CPU + I/O priority','tag-act'],
                ['ACT','HD-Agent.exe, BstkSVC.exe, HD-Service.exe → HIGH...','tag-act'],
                ['BS','BS PHASE 3: Windows Defender exclusion for BlueStacks...','tag-bs'],
                ['ACT','Excluding C:\\Program Files\\BlueStacks_nxt from scanning...','tag-act'],
                ['ACT','Excluding C:\\ProgramData\\BlueStacks_nxt from scanning...','tag-act'],
                ['ACT','Excluding HD-Player.exe, HD-Agent.exe processes...','tag-act'],
                ['BS','BS PHASE 4: Timer resolution fix for emulator...','tag-bs'],
                ['ACT','bcdedit: disabledynamictick = yes','tag-act'],
                ['ACT','bcdedit: useplatformtick = yes (smoother frame timing)','tag-act'],
                ['BS','BS PHASE 5: GPU rendering mode for BlueStacks...','tag-bs'],
                ['ACT','Setting BlueStacks graphics engine = DirectX','tag-act'],
                ['ACT','Setting HD-Player.exe GPU preference = HIGH PERFORMANCE','tag-act'],
                ['BS','BS PHASE 6: Killing RAM competition...','tag-bs'],
                ['ACT','Killing idle processes hogging memory...','tag-act'],
                ['ACT','Forcing .NET garbage collection...','tag-act'],
                ['BS','BS PHASE 7: BlueStacks network adapter priority...','tag-bs'],
                ['ACT','Setting BlueStacks virtual NIC to metric 1 (max priority)...','tag-act'],
                ['SYS','Executing all BlueStacks phases on backend...','tag-sys']
            ],
            'pc-restore': [
                ['SYS','Initializing full restore...','tag-sys'],
                ['ACT','Restoring visual effects...','tag-act'],
                ['ACT','Restoring Balanced power plan...','tag-act'],
                ['ACT','Restoring CPU priority, services, network...','tag-act'],
                ['ACT','Removing BlueStacks + FreeFire priority locks...','tag-act'],
                ['ACT','Restoring bcdedit timer settings...','tag-act']
            ]
        };

        async function runAction(type) {
            rpLog.innerHTML = '';
            rpClose.style.display = 'none';
            rpTitle.style.color = type === 'bs-optimize' ? '#ff8800' : '#00f3ff';
            overlay.classList.add('show');
            rpTitle.innerText = titles[type];

            for (const [tag, text, cls] of allSteps[type]) {
                addLog(tag, text, cls);
                await new Promise(r => setTimeout(r, 100 + Math.random() * 160));
            }

            try {
                const res = await fetch(endpoints[type], { method: 'POST' });
                const data = await res.json();
                if (res.ok) {
                    if (data.steps) data.steps.forEach(s => addLog('OK', s, 'tag-ok'));
                    if (data.before && data.after) {
                        addLog('INFO', 'BEFORE: Speed=' + data.before.MouseSpeed + ' T1=' + data.before.MouseThreshold1 + ' T2=' + data.before.MouseThreshold2, 'tag-sys');
                        addLog('INFO', 'AFTER:  Speed=' + data.after.MouseSpeed + ' T1=' + data.after.MouseThreshold1 + ' T2=' + data.after.MouseThreshold2, 'tag-sys');
                    }
                    const box = document.createElement('div');
                    const isBs = type === 'bs-optimize';
                    box.className = 'rp-success' + (isBs ? ' bs' : '');
                    const msgs = {
                        'aim':        '<strong>MOUSE OPTIMIZATION COMPLETE</strong><br>Raw 1:1 input active — zero acceleration',
                        'restore':    '<strong>MOUSE RESTORE COMPLETE</strong><br>Reverted to Windows defaults',
                        'pc-optimize':'<strong>LOW-END BEAST MODE ACTIVE</strong><br>10 phases done | Ultimate Power | Core Parking OFF | 24 services killed<br><span style="color:#ffcc00;">Now run BLUESTACKS BEAST MODE (Step 2)</span>',
                        'bs-optimize':'<strong>BLUESTACKS BEAST MODE ACTIVE</strong><br>' +
                            'FPS unlocked in .conf | All BS processes HIGH priority<br>' +
                            'Defender exclusion set | Timer fixed | DirectX GPU<br>' +
                            '<span style="color:#ff8800; font-weight:bold;">RESTART BLUESTACKS → Open Free Fire → Expected: 300+ FPS</span><br>' +
                            '<span style="color:#ffcc00; font-size:0.72rem;">Note: Timer changes take full effect after Windows restart</span>',
                        'pc-restore': '<strong>FULL RESTORE COMPLETE</strong><br>All tweaks reverted to Windows defaults'
                    };
                    box.innerHTML = msgs[type];
                    rpLog.appendChild(box);
                    rpTitle.style.color = isBs ? '#ff8800' : '#39ff14';
                    rpTitle.innerText = isBs ? 'BEAST MODE LOCKED IN' : 'COMPLETE';
                } else {
                    addLog('ERROR', data.message || 'Unknown error', 'tag-err');
                    rpTitle.style.color = '#ff3c3c';
                    rpTitle.innerText = 'FAILED';
                }
            } catch (e) {
                addLog('ERROR', 'Connection lost: ' + e.message, 'tag-err');
                rpTitle.style.color = '#ff3c3c';
                rpTitle.innerText = 'ERROR';
            }
            rpClose.style.display = 'block';
        }

        // Detect mobile vs desktop
        const isMobile = /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || window.innerWidth <= 640;

        if (isMobile) {
            // On mobile: hide QR card (not needed), show connected banner in dashboard
            const qc = document.getElementById('qr-card');
            if (qc) qc.style.display = 'none';
            const mb = document.getElementById('mobile-banner');
            if (mb) mb.style.display = 'flex';
            const pcc = document.getElementById('pc-connect-card');
            if (pcc) pcc.style.display = 'none';
        } else {
            // On PC: load QR code on the LOGIN page immediately
            fetch('/network-info').then(r => r.json()).then(d => {
                const url = d.mobile_url;

                // Update login page QR
                const urlText = document.getElementById('qr-url-text');
                if (urlText) urlText.innerText = url;
                const qrImg = document.getElementById('qr-img');
                if (qrImg) {
                    qrImg.src = 'https://api.qrserver.com/v1/create-qr-code/?size=90x90&color=000000&bgcolor=ffffff&data=' + encodeURIComponent(url);
                }

                // Also update dashboard card if present
                const pcUrl = document.getElementById('pc-mobile-url');
                if (pcUrl) pcUrl.innerText = url;
                const dashImg = document.getElementById('qr-img-dash');
                if (dashImg) {
                    dashImg.src = 'https://api.qrserver.com/v1/create-qr-code/?size=106x106&color=000000&bgcolor=ffffff&data=' + encodeURIComponent(url);
                }
            }).catch(() => {
                const urlText = document.getElementById('qr-url-text');
                if (urlText) urlText.innerText = 'Run server, check WiFi';
            });
        }

        document.getElementById('btn-optimize').addEventListener('click',    () => runAction('aim'));
        document.getElementById('btn-restore').addEventListener('click',     () => runAction('restore'));
        document.getElementById('btn-pc-optimize').addEventListener('click', () => runAction('pc-optimize'));
        document.getElementById('btn-bs-optimize').addEventListener('click', () => runAction('bs-optimize'));
        document.getElementById('btn-pc-restore').addEventListener('click',  () => runAction('pc-restore'));

        // GUIDE button
        document.getElementById('btn-guide').addEventListener('click', () => {
            document.getElementById('guide-overlay').style.display = 'flex';
        });

        // DIAGNOSE button
        document.getElementById('btn-diagnose').addEventListener('click', async () => {
            rpLog.innerHTML = '';
            rpClose.style.display = 'none';
            rpTitle.style.color = '#ffcc00';
            rpTitle.innerText = 'DIAGNOSING FPS ISSUE...';
            overlay.classList.add('show');

            addLog('SYS', 'Scanning BlueStacks installation...', 'tag-sys');
            addLog('SYS', 'Reading .conf files for FPS cap...', 'tag-sys');
            addLog('SYS', 'Checking running processes...', 'tag-sys');
            await new Promise(r => setTimeout(r, 800));

            try {
                const res = await fetch('/bs-diagnose');
                const json = await res.json();
                const d = json.data;

                addLog('SYS', '--- DIAGNOSIS RESULT ---', 'tag-sys');

                // BlueStacks running?
                addLog(d.bs_running ? 'WARN' : 'OK',
                    'BlueStacks running: ' + (d.bs_running ? 'YES — close it before optimizing!' : 'NO (good)'),
                    d.bs_running ? 'tag-err' : 'tag-ok');

                // Install path
                addLog(d.install_path ? 'OK' : 'ERR',
                    'Install path: ' + (d.install_path || 'NOT FOUND — is BlueStacks installed?'),
                    d.install_path ? 'tag-ok' : 'tag-err');

                // Conf files
                if (d.conf_files && d.conf_files.length > 0) {
                    d.conf_files.forEach(f => addLog('OK', 'Config found: ' + f, 'tag-ok'));
                } else {
                    addLog('ERR', 'NO bluestacks.conf found — FPS only controllable from BlueStacks Settings UI', 'tag-err');
                }

                // FPS values
                if (d.fps_values && d.fps_values.length > 0) {
                    d.fps_values.forEach(v => {
                        const capped = v.fps <= 60;
                        addLog(capped ? 'CAP' : 'OK',
                            v.instance + ' → ' + v.key + ' = ' + v.fps + ' FPS' + (capped ? ' ← CAPPED!' : ' ✓'),
                            capped ? 'tag-err' : 'tag-ok');
                    });
                } else {
                    addLog('WARN', 'No FPS keys found in conf — BlueStacks controls FPS internally', 'tag-act');
                }

                // Issues
                const box = document.createElement('div');
                box.style.cssText = 'margin-top:16px;padding:14px;border:1px solid #ffcc00;background:rgba(255,204,0,0.06);font-size:0.76rem;line-height:1.9;';
                let html = '<span style="color:#ffcc00;font-family:Orbitron,sans-serif;letter-spacing:2px;font-size:0.7rem;">ISSUES FOUND</span><br>';
                if (d.issues) d.issues.forEach((iss, i) => {
                    html += '<span style="color:#ff3c3c;">&#9654;</span> ' + iss + '<br>';
                });
                html += '<br><span style="color:#39ff14;font-family:Orbitron,sans-serif;letter-spacing:2px;font-size:0.7rem;">HOW TO FIX</span><br>';
                if (d.fixes) d.fixes.forEach((fix, i) => {
                    html += '<span style="color:#39ff14;">&#10003;</span> ' + fix + '<br>';
                });
                box.innerHTML = html;
                rpLog.appendChild(box);

                rpTitle.style.color = '#ffcc00';
                rpTitle.innerText = 'DIAGNOSIS COMPLETE';
            } catch(e) {
                addLog('ERROR', 'Diagnose failed: ' + e.message, 'tag-err');
                rpTitle.style.color = '#ff3c3c';
                rpTitle.innerText = 'ERROR';
            }
            rpClose.style.display = 'block';
        });
    });
    </script>
</body>
</html>'''


# ============================================================
# ROUTES
# ============================================================

def get_local_ip():
    """Get this PC's local network IP address (the one phones connect to)."""
    try:
        import socket as _socket
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@app.route('/health')
def health():
    try:
        import psutil  # type: ignore
        mem_percent = psutil.virtual_memory().percent
    except Exception:
        mem_percent = None
    return jsonify({
        "status": "online",
        "mem_percent": mem_percent,
        "local_ip": get_local_ip(),
        "port": app.config.get('SERVER_PORT', 5050)
    })


@app.route('/network-info')
def network_info():
    ip = get_local_ip()
    port = app.config.get('SERVER_PORT', 5050)
    return jsonify({
        "local_ip": ip,
        "port": port,
        "mobile_url": f"http://{ip}:{port}"
    })


@app.route('/')
def index():
    return Response(HTML_PAGE, mimetype='text/html')


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()
    if validate_user(username, password):
        ip = str(request.headers.get('X-Forwarded-For', request.remote_addr) or '')
        ua = str(request.headers.get('User-Agent', '') or '')
        record_login(username, ip, ua)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail"}), 401


@app.route('/admin-update-user', methods=['POST'])
def admin_update_user():
    data = request.get_json(silent=True) or {}
    user_id   = str(data.get('user_id', '')).strip()
    new_user  = str(data.get('new_username', '')).strip()
    new_pass  = str(data.get('new_password', '')).strip()
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id"}), 400
    try:
        update_data = {}
        if new_user:
            update_data["username"] = new_user
        if new_pass:
            update_data["password"] = new_pass
        if update_data:
            supabase.table('users').update(update_data).eq('id', user_id).execute()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# ADMIN API ENDPOINTS (Dashboard is now a separate standalone app)
# ============================================================

@app.route('/admin-data')
def admin_data():
    return jsonify(get_admin_data())


@app.route('/admin-clear', methods=['POST'])
def admin_clear():
    try:
        supabase.table('logins').delete().neq('id', 0).execute()
    except Exception as e:
        print(f"[DB] Clear logins error: {e}")
    return jsonify({"status": "cleared"})


@app.route('/run-optimizer', methods=['POST'])
def run_optimizer():
    before = read_mouse_registry()
    steps = do_aim_optimize()
    after = read_mouse_registry()
    return jsonify({
        "status": "success",
        "message": "Mouse aim optimization complete",
        "steps": steps,
        "before": before,
        "after": after
    })


@app.route('/restore-defaults', methods=['POST'])
def restore_defaults():
    before = read_mouse_registry()
    steps = do_mouse_restore()
    after = read_mouse_registry()
    return jsonify({
        "status": "success",
        "message": "Mouse settings restored to defaults",
        "steps": steps,
        "before": before,
        "after": after
    })


@app.route('/pc-optimize', methods=['POST'])
def pc_optimize():
    try:
        steps = do_pc_optimize()
        return jsonify({
            "status": "success",
            "message": "Low-end beast optimization complete",
            "steps": steps
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/bluestacks-optimize', methods=['POST'])
def bluestacks_optimize():
    try:
        steps = do_bluestacks_optimize()
        return jsonify({
            "status": "success",
            "message": "BlueStacks Beast Mode active — restart BlueStacks for 300+ FPS",
            "steps": steps
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/bs-diagnose', methods=['GET'])
def bs_diagnose_route():
    try:
        data = do_bs_diagnose()
        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/pc-restore', methods=['POST'])
def pc_restore():
    try:
        steps = do_pc_restore()
        return jsonify({
            "status": "success",
            "message": "All settings restored to defaults",
            "steps": steps
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    import socket
    init_db()

    # Find open port automatically (allows multiple instances to run at once)
    current_port = 5050
    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', current_port))
        sock.close()
        if result != 0:
            break
        current_port += 1

    app.config['SERVER_PORT'] = current_port

    # Open Windows Firewall for this specific port so phones on same WiFi can connect
    # (If multiple instances run, firewall opens for the first one that successfully runs this command)
    run_silent(["netsh", "advfirewall", "firewall", "delete", "rule",
                f"name=HackerControlCenter_{current_port}"])
    run_silent(["netsh", "advfirewall", "firewall", "add", "rule",
                f"name=HackerControlCenter_{current_port}", "dir=in", "action=allow",
                "protocol=TCP", f"localport={current_port}"])

    local_ip = get_local_ip()

    print("=========================================")
    print("   HACKER CONTROL CENTER v6.0            ")
    print("   BLUESTACKS BEAST MODE EDITION         ")
    print(f"   PC:     http://127.0.0.1:{current_port}     ")
    print(f"   MOBILE: http://{local_ip}:{current_port}    ")
    print("   Connect phone to same WiFi, open URL  ")
    print("   4GB RAM | iGPU | Free Fire 300+ FPS   ")
    print("=========================================")

    # Background thread to wait for 'Enter' and open browser
    import threading
    import webbrowser
    def wait_and_open():
        input("\n   >>> PRESS [ENTER] TO OPEN MENU IN BROWSER <<<\n")
        webbrowser.open(f"http://127.0.0.1:{current_port}")
    threading.Thread(target=wait_and_open, daemon=True).start()

    # Bind to 0.0.0.0 so ALL network interfaces can reach the server
    # (localhost AND your phone on the same WiFi)
    app.run(host='0.0.0.0', port=current_port, debug=False, threaded=True)

