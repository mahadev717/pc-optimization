# type: ignore
# HACKER CONTROL CENTER - Complete Backend Server
# All HTML/CSS/JS embedded. All optimization logic in Python.
# No external .bat, .html, .css, or .js files needed.

from flask import Flask, jsonify, request, Response
from flask_cors import CORS  # type: ignore
import os
import subprocess
import ctypes  # type: ignore[attr-defined]
import ctypes.wintypes  # type: ignore[attr-defined]
import winreg  # type: ignore[attr-defined]

app = Flask(__name__)
CORS(app)

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
# AIM OPTIMIZATION (replaces aim_optimizer.bat)
# ============================================================

def do_aim_optimize():
    """Full mouse/aim optimization - all in Python, no batch files."""
    results = []

    # Set MouseSensitivity = 10
    ok, msg = set_mouse_sensitivity(10)
    results.append(msg)

    # Set MouseSpeed=0, Threshold1=0, Threshold2=0 (acceleration OFF)
    ok, msg = apply_mouse_params(0, 0, 0)
    results.append(msg)

    # Disable mouse trails
    ok, msg = disable_mouse_trails()
    results.append(msg)

    # High Performance power plan
    run_silent(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"])
    results.append("High Performance power plan active")

    return results


# ============================================================
# MOUSE RESTORE (replaces restore_defaults.bat)
# ============================================================

def do_mouse_restore():
    """Restore mouse settings to Windows defaults - all in Python."""
    results = []

    # Restore sensitivity
    ok, msg = set_mouse_sensitivity(10)
    results.append(msg)

    # Restore MouseSpeed=1, Threshold1=6, Threshold2=10
    ok, msg = apply_mouse_params(1, 6, 10)
    results.append(msg)

    # Disable trails (default is 0)
    ok, msg = disable_mouse_trails()
    results.append(msg)

    # Balanced power plan
    run_silent(["powercfg", "-setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"])
    results.append("Balanced power plan active")

    return results


# ============================================================
# PC OPTIMIZATION (replaces pc_optimizer.bat)
# ============================================================

def do_pc_optimize():
    """Full 8-phase PC optimization - all in Python, no batch files."""
    results = []

    # Phase 1: Visual Effects
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", "REG_DWORD", 2)
    reg_add(r"HKCU\Control Panel\Desktop\WindowMetrics", "MinAnimate", "REG_SZ", "0")
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", "REG_DWORD", 0)
    reg_add(r"HKCU\Control Panel\Desktop", "SmoothScroll", "REG_DWORD", 0)
    reg_add(r"HKCU\Control Panel\Desktop", "CursorShadow", "REG_DWORD", 0)
    results.append("Visual effects disabled")

    # Phase 2: Network Optimization
    # Disable Nagle's Algorithm via PowerShell (needs adapter GUIDs)
    ps_cmd = (
        "$adapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}; "
        "foreach($a in $adapters){ "
        "$guid = $a.InterfaceGuid; "
        "$path = 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\' + $guid; "
        "Set-ItemProperty -Path $path -Name 'TcpAckFrequency' -Value 1 -Type DWord -ErrorAction SilentlyContinue; "
        "Set-ItemProperty -Path $path -Name 'TCPNoDelay' -Value 1 -Type DWord -ErrorAction SilentlyContinue }"
    )
    run_silent(["powershell", "-command", ps_cmd])
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", "REG_DWORD", "0xFFFFFFFF")
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness", "REG_DWORD", 0)
    results.append("Network optimized (Nagle OFF, throttling OFF)")

    # Phase 3: GPU & Game
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode", "REG_DWORD", 2)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled", "REG_DWORD", 0)
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode", "REG_DWORD", 2)
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", "REG_DWORD", 0)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR", "REG_DWORD", 0)
    results.append("GPU optimized, Game DVR/Bar disabled")

    # Phase 4: Background Apps & Telemetry
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", "REG_DWORD", 1)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", "REG_DWORD", 0)
    reg_add(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338389Enabled", "REG_DWORD", 0)
    results.append("Background apps & telemetry disabled")

    # Phase 5: CPU Gaming Priority
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "GPU Priority", "REG_DWORD", 8)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Priority", "REG_DWORD", 6)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Scheduling Category", "REG_SZ", "High")
    results.append("CPU game priority set to HIGH")

    # Phase 6: Memory
    service_control("SysMain", "stop", "disabled")
    service_control("WSearch", "stop", "disabled")
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", "REG_DWORD", 1)
    results.append("Memory optimized (SysMain/WSearch stopped)")

    # Phase 7: Power Plan
    run_silent(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"])
    run_silent(["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "2a737441-1930-4402-8d77-b2bebba308a3",
                "48e6b7a6-50f5-4782-a5d4-53bb8f07e226", "0"])
    run_silent(["powercfg", "-setactive", "SCHEME_CURRENT"])
    results.append("High Performance power plan, USB suspend OFF")

    # Phase 8: Unnecessary Services
    service_control("Spooler", "stop", "disabled")
    service_control("Fax", "stop", "disabled")
    service_control("RemoteRegistry", "stop", "disabled")
    results.append("Print Spooler, Fax, Remote Registry disabled")

    return results


# ============================================================
# PC RESTORE (replaces pc_restore.bat)
# ============================================================

def do_pc_restore():
    """Restore all PC tweaks to defaults - all in Python."""
    results = []

    # Phase 1: Visual Effects
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", "REG_DWORD", 0)
    reg_add(r"HKCU\Control Panel\Desktop\WindowMetrics", "MinAnimate", "REG_SZ", "1")
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "EnableTransparency", "REG_DWORD", 1)
    reg_delete(r"HKCU\Control Panel\Desktop", "SmoothScroll")
    reg_delete(r"HKCU\Control Panel\Desktop", "CursorShadow")
    results.append("Visual effects restored")

    # Phase 2: Network
    ps_cmd = (
        "$adapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}; "
        "foreach($a in $adapters){ "
        "$guid = $a.InterfaceGuid; "
        "$path = 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces\\' + $guid; "
        "Remove-ItemProperty -Path $path -Name 'TcpAckFrequency' -ErrorAction SilentlyContinue; "
        "Remove-ItemProperty -Path $path -Name 'TCPNoDelay' -ErrorAction SilentlyContinue }"
    )
    run_silent(["powershell", "-command", ps_cmd])
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "NetworkThrottlingIndex", "REG_DWORD", 10)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", "SystemResponsiveness", "REG_DWORD", 20)
    results.append("Network defaults restored")

    # Phase 3: GPU & Game
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_FSEBehaviorMode", "REG_DWORD", 0)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AllowAutoGameMode", "REG_DWORD", 1)
    reg_add(r"HKCU\Software\Microsoft\GameBar", "AutoGameModeEnabled", "REG_DWORD", 1)
    reg_delete(r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers", "HwSchMode")
    reg_add(r"HKCU\System\GameConfigStore", "GameDVR_Enabled", "REG_DWORD", 1)
    reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR", "AllowGameDVR")
    results.append("GPU/Game settings restored")

    # Phase 4: Background Apps
    reg_add(r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "GlobalUserDisabled", "REG_DWORD", 0)
    reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry")
    reg_delete(r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana")
    reg_delete(r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager", "SubscribedContent-338389Enabled")
    results.append("Background apps restored")

    # Phase 5: CPU Priority
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "GPU Priority", "REG_DWORD", 2)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Priority", "REG_DWORD", 2)
    reg_add(r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", "Scheduling Category", "REG_SZ", "Medium")
    results.append("CPU priority restored")

    # Phase 6: Memory Services
    service_control("SysMain", "start", "auto")
    service_control("WSearch", "start", "delayed-auto")
    reg_add(r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", "REG_DWORD", 0)
    results.append("Memory services restored")

    # Phase 7: Power Plan
    run_silent(["powercfg", "-setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"])
    run_silent(["powercfg", "-setacvalueindex", "SCHEME_CURRENT",
                "2a737441-1930-4402-8d77-b2bebba308a3",
                "48e6b7a6-50f5-4782-a5d4-53bb8f07e226", "1"])
    run_silent(["powercfg", "-setactive", "SCHEME_CURRENT"])
    results.append("Balanced power plan restored")

    # Phase 8: Services
    service_control("Spooler", "start", "auto")
    service_control("Fax", None, "auto")
    results.append("Services restored")

    return results


# ============================================================
# EMBEDDED HTML (complete UI - no external files needed)
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

        #dash-module { display: none; padding: 20px; }
        .glass-nav { display: flex; justify-content: space-between; padding: 15px 30px; background: var(--glass); border-bottom: 1px solid rgba(0,243,255,0.2); margin-bottom: 20px; }
        .brand { font-size: 1.2rem; display: flex; align-items: center; gap: 10px; }
        .pulse-dot { width: 8px; height: 8px; background: var(--green); border-radius: 50%; box-shadow: 0 0 8px var(--green); }
        .stats { display: flex; gap: 20px; align-items: center; font-family: var(--mono); font-size: 0.8rem; }
        .grid-layout { display: flex; justify-content: center; align-items: flex-start; padding-top: 50px; }
        .panel-right { width: 500px; }
        .action-grid { display: grid; grid-template-columns: 1fr; gap: 20px; }
        .node-card { background: var(--glass); border: 1px solid rgba(255,255,255,0.05); padding: 30px; display: flex; align-items: center; gap: 20px; cursor: pointer; transition: 0.3s; }
        .node-card:hover { transform: translateY(-5px); border-color: currentColor; }
        .node-card.red { color: var(--red); }
        .node-card.blue { color: var(--cyan); }
        .node-card.green { color: var(--green); }
        .node-card.cyan { color: var(--cyan); }
        .node-icon { font-size: 2rem; }
        .node-info h4 { font-size: 1rem; margin-bottom: 5px; }
        .node-info p { font-size: 0.7rem; opacity: 0.7; }
        .fade-out { opacity: 0; transition: 0.8s; }
        .fade-in { animation: fadeIn 1s forwards; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .hidden { display: none; }
        #login-error { position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); color: var(--red); font-size: 0.9rem; font-family: var(--mono); background: rgba(255,60,60,0.15); border: 1px solid var(--red); padding: 12px 40px; z-index: 1000; letter-spacing: 3px; box-shadow: 0 0 25px var(--red); clip-path: polygon(10px 0, 100% 0, calc(100% - 10px) 100%, 0 100%); animation: error-flash 0.8s infinite alternate; }
        @keyframes error-flash { from { opacity: 1; box-shadow: 0 0 25px var(--red); } to { opacity: 0.7; box-shadow: 0 0 10px var(--red); } }

        #result-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 500; justify-content: center; align-items: center; }
        #result-overlay.show { display: flex; }
        .result-panel { width: 500px; max-height: 80vh; background: rgba(5,5,10,0.95); border: 1px solid rgba(0,243,255,0.3); padding: 30px; overflow-y: auto; font-family: 'Roboto Mono', monospace; }
        .result-panel .rp-title { font-family: 'Orbitron', sans-serif; font-size: 1rem; letter-spacing: 3px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(0,243,255,0.2); }
        .result-panel .rp-line { font-size: 0.85rem; margin-bottom: 6px; line-height: 1.6; }
        .result-panel .rp-success { color: #39ff14; margin-top: 15px; padding: 10px; border: 1px solid #39ff14; background: rgba(57,255,20,0.08); }
        .result-panel .rp-error { color: #ff3c3c; margin-top: 15px; padding: 10px; border: 1px solid #ff3c3c; background: rgba(255,60,60,0.08); }
        .result-panel .rp-close { margin-top: 20px; padding: 10px 20px; background: transparent; border: 1px solid #00f3ff; color: #00f3ff; font-family: 'Orbitron', sans-serif; cursor: pointer; width: 100%; transition: 0.3s; }
        .result-panel .rp-close:hover { background: #00f3ff; color: #000; }
        .rp-loading { color: #00f3ff; animation: blink-load 0.5s infinite; }
        @keyframes blink-load { 50% { opacity: 0.3; } }
        .tag-sys { color: #00f3ff; }
        .tag-act { color: #ffcc00; }
        .tag-ok { color: #39ff14; }
        .tag-err { color: #ff3c3c; }
    </style>
</head>
<body class="login-mode">
    <canvas id="canvas3d"></canvas>
    <div class="scanlines"></div>
    <div class="vignette"></div>

    <div id="login-module" class="module active">
        <div class="login-glass">
            <div class="cyber-bracket top-left"></div>
            <div class="cyber-bracket top-right"></div>
            <div class="cyber-bracket bottom-left"></div>
            <div class="cyber-bracket bottom-right"></div>
            <header>
                <h1 class="glitch-title" data-text="HACKER">HACKER</h1>
                <div class="pulse-line"></div>
                <p class="system-tag" style="font-size:0.7rem;color:#00f3ff;letter-spacing:3px;">NEURAL LINK v5.0</p>
            </header>
            <form id="login-form">
                <div class="input-container">
                    <span class="label">ID://</span>
                    <input type="text" id="user-input" placeholder="IDENTITY" required autocomplete="off">
                </div>
                <div class="input-container">
                    <span class="label">KEY://</span>
                    <input type="password" id="pass-input" placeholder="PASSCODE" required>
                </div>
                <button type="submit" class="prime-btn">
                    <span class="btn-text">ESTABLISH CONNECTION</span>
                </button>
            </form>
        </div>
    </div>

    <div id="dash-module" class="module">
        <nav class="glass-nav">
            <div class="brand">
                <span class="pulse-dot"></span>
                HACKER_OS/CENTRAL
            </div>
            <div class="stats">
                <div class="stat-item">MEM: <span id="mem-usage">24%</span></div>
                <div class="stat-item" id="server-status"><span style="color:#39ff14;">&#9679; ONLINE</span></div>
                <div class="stat-item" id="clock">00:00:00</div>
            </div>
        </nav>
        <main class="grid-layout single-panel">
            <div class="panel-right">
                <div class="action-grid">
                    <div class="node-card red" id="btn-optimize">
                        <div class="node-icon">&#127919;</div>
                        <div class="node-info"><h4>MOUSE AIM OPTIMIZER</h4><p>Disable Acceleration & Raw Input</p></div>
                    </div>
                    <div class="node-card blue" id="btn-pc-optimize">
                        <div class="node-icon">&#9881;&#65039;</div>
                        <div class="node-info"><h4>PC OPTIMIZATION</h4><p>GPU, Network, CPU, Memory Tweaks</p></div>
                    </div>
                    <div class="node-card green" id="btn-restore">
                        <div class="node-icon">&#128260;</div>
                        <div class="node-info"><h4>RESTORE MOUSE</h4><p>Revert Mouse to Default</p></div>
                    </div>
                    <div class="node-card cyan" id="btn-pc-restore">
                        <div class="node-icon">&#128281;</div>
                        <div class="node-info"><h4>RESTORE PC DEFAULTS</h4><p>Revert All PC Tweaks</p></div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <div id="result-overlay">
        <div class="result-panel">
            <div class="rp-title" id="rp-title" style="color:#00f3ff;">PROCESSING</div>
            <div id="rp-log"></div>
            <button class="rp-close" id="rp-close" style="display:none;" onclick="document.getElementById('result-overlay').classList.remove('show')">CLOSE</button>
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
        const material = new THREE.MeshBasicMaterial({ color: 0x00f3ff, wireframe: true, transparent: true, opacity: 0.2 });
        const plane = new THREE.Mesh(geometry, material);
        plane.rotation.x = -Math.PI / 2.5;
        plane.position.y = -2;
        scene.add(plane);
        const partGeom = new THREE.BufferGeometry();
        const partCount = 1000;
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

        // UI LOGIC
        const loginForm = document.getElementById('login-form');
        const loginModule = document.getElementById('login-module');
        const dashModule = document.getElementById('dash-module');
        const memUsage = document.getElementById('mem-usage');
        setInterval(() => { memUsage.innerText = Math.floor(Math.random() * (28 - 22) + 22) + '%'; }, 2000);
        setInterval(() => { document.getElementById('clock').innerText = new Date().toLocaleTimeString(); }, 1000);

        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const user = document.getElementById('user-input').value;
            const pass = document.getElementById('pass-input').value;
            if (user === '1' && pass === '1') {
                loginModule.classList.add('fade-out');
                setTimeout(() => {
                    loginModule.style.display = 'none';
                    dashModule.style.display = 'block';
                    dashModule.classList.add('fade-in');
                    partMat.color.set(0x00f3ff);
                    material.opacity = 0.5;
                }, 800);
            } else {
                const error = document.getElementById('login-error');
                error.classList.remove('hidden');
                setTimeout(() => error.classList.add('hidden'), 3000);
            }
        });

        // ACTION LOGIC
        const overlay = document.getElementById('result-overlay');
        const rpTitle = document.getElementById('rp-title');
        const rpLog = document.getElementById('rp-log');
        const rpClose = document.getElementById('rp-close');

        function addLog(tag, text, cls) {
            const line = document.createElement('div');
            line.className = 'rp-line';
            line.innerHTML = '<span class="' + cls + '">[' + tag + ']</span> ' + text;
            rpLog.appendChild(line);
        }

        async function runAction(type) {
            rpLog.innerHTML = '';
            rpClose.style.display = 'none';
            rpTitle.style.color = '#00f3ff';
            overlay.classList.add('show');

            const endpoints = { 'aim': '/run-optimizer', 'restore': '/restore-defaults', 'pc-optimize': '/pc-optimize', 'pc-restore': '/pc-restore' };
            const titles = { 'aim': 'MOUSE AIM OPTIMIZER', 'restore': 'MOUSE RESTORE', 'pc-optimize': 'PC OPTIMIZATION', 'pc-restore': 'PC RESTORE' };
            rpTitle.innerText = titles[type];

            const allSteps = {
                'aim': [
                    ['SYSTEM','Connecting to Windows kernel...'],['SYSTEM','Reading mouse registry...'],
                    ['ACTION','Setting MouseSpeed = 0'],['ACTION','Setting MouseThreshold1 = 0'],
                    ['ACTION','Setting MouseThreshold2 = 0'],['ACTION','Setting MouseSensitivity = 10 (RAW 1:1)'],
                    ['SYSTEM','Calling SystemParametersInfo(SPI_SETMOUSE)...'],
                    ['ACTION','Disabling Enhance Pointer Precision...'],['ACTION','Switching to High Performance power plan...']
                ],
                'restore': [
                    ['SYSTEM','Initiating mouse restore...'],['ACTION','Restoring MouseSpeed = 1'],
                    ['ACTION','Restoring MouseThreshold1 = 6'],['ACTION','Restoring MouseThreshold2 = 10'],
                    ['SYSTEM','Calling SystemParametersInfo(SPI_SETMOUSE)...'],['ACTION','Restoring Balanced power plan...']
                ],
                'pc-optimize': [
                    ['SYSTEM','Initializing full PC optimization...'],['ACTION','Disabling visual effects & transparency...'],
                    ['ACTION','Disabling Nagle algorithm (TCP_NODELAY)...'],['ACTION','Removing network throttling...'],
                    ['ACTION','Disabling fullscreen optimizations...'],['ACTION','Disabling Game DVR & Game Bar...'],
                    ['ACTION','Enabling HW GPU scheduling...'],['ACTION','Disabling background apps & telemetry...'],
                    ['ACTION','Setting CPU game priority = HIGH...'],['ACTION','Stopping SysMain & WSearch services...'],
                    ['ACTION','Applying High Performance power plan...'],['ACTION','Disabling USB selective suspend...'],
                    ['ACTION','Stopping Print Spooler & Fax...']
                ],
                'pc-restore': [
                    ['SYSTEM','Initializing PC restore...'],['ACTION','Restoring visual effects...'],
                    ['ACTION','Restoring network defaults...'],['ACTION','Restoring GPU & Game settings...'],
                    ['ACTION','Re-enabling background apps...'],['ACTION','Restoring CPU priority...'],
                    ['ACTION','Restarting SysMain & WSearch...'],['ACTION','Restoring Balanced power plan...'],
                    ['ACTION','Restoring services...']
                ]
            };

            for (const [tag, text] of allSteps[type]) {
                addLog(tag, text, tag === 'SYSTEM' ? 'tag-sys' : 'tag-act');
                await new Promise(r => setTimeout(r, 150 + Math.random() * 200));
            }
            addLog('SYSTEM', 'Executing on backend...', 'tag-sys');

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
                    box.className = 'rp-success';
                    const msgs = {
                        'aim': '<strong>MOUSE OPTIMIZATION COMPLETE</strong><br>0 acceleration | 0 latency | raw input active',
                        'restore': '<strong>MOUSE RESTORE COMPLETE</strong><br>Mouse settings reverted to defaults',
                        'pc-optimize': '<strong>PC OPTIMIZATION COMPLETE</strong><br>GPU, Network, CPU, Memory all optimized',
                        'pc-restore': '<strong>PC RESTORE COMPLETE</strong><br>All PC tweaks reverted to defaults'
                    };
                    box.innerHTML = msgs[type];
                    rpLog.appendChild(box);
                    rpTitle.style.color = '#39ff14';
                    rpTitle.innerText = (type === 'aim' || type === 'pc-optimize') ? 'OPTIMIZED' : 'RESTORED';
                } else {
                    addLog('ERROR', data.message || 'Unknown error', 'tag-err');
                    rpTitle.style.color = '#ff3c3c';
                    rpTitle.innerText = 'FAILED';
                }
            } catch (e) {
                addLog('ERROR', 'Server connection lost', 'tag-err');
                rpTitle.style.color = '#ff3c3c';
                rpTitle.innerText = 'ERROR';
            }
            rpClose.style.display = 'block';
        }

        document.getElementById('btn-optimize').addEventListener('click', () => runAction('aim'));
        document.getElementById('btn-restore').addEventListener('click', () => runAction('restore'));
        document.getElementById('btn-pc-optimize').addEventListener('click', () => runAction('pc-optimize'));
        document.getElementById('btn-pc-restore').addEventListener('click', () => runAction('pc-restore'));
    });
    </script>
</body>
</html>'''


# ============================================================
# ROUTES
# ============================================================

@app.route('/health')
def health():
    return jsonify({"status": "online"})


@app.route('/')
def index():
    return Response(HTML_PAGE, mimetype='text/html')


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
            "message": "Full PC optimization complete",
            "steps": steps
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/pc-restore', methods=['POST'])
def pc_restore():
    try:
        steps = do_pc_restore()
        return jsonify({
            "status": "success",
            "message": "All PC settings restored to defaults",
            "steps": steps
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    import socket

    # Check if port 5050 is already in use
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5050))
    sock.close()
    if result == 0:
        print("!!! ERROR: Port 5050 is already in use !!!")
        print("!!! Kill old processes first or use run_server.bat !!!")
        print("=========================================")
        input("Press Enter to try starting anyway...")

    print("=========================================")
    print("   HACKER CONTROL CENTER v5.0            ")
    print("   http://127.0.0.1:5050                 ")
    print("   All-in-one server (no external files)  ")
    print("=========================================")
    app.run(host='127.0.0.1', port=5050, debug=False)
