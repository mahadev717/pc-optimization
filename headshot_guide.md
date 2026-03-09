# Free Fire Headshot Optimization Guide

This guide covers the three pillars of hitting consistent headshots: Server-side logic (Craftland), In-game sensitivity, and Windows system tuning.

## 1. Craftland "Headshot Only" Logic
To make your map server-side "Headshot Only" (where body shots do 0 damage), follow these steps in the **Script Editor**:

1. Open **Block Script** > **Player**.
2. **On Awake** Block:
   - Use `Set Property` -> `This Entity` -> `Weapon Damage Rate` = `0.005` (Optional, for global reduction).
3. **On Equip Weapon** Block:
   - Add three `Set Property` blocks (Target: `Weapon`):
     - `Body Shot Damage Factor` = `0`
     - `Lim Shot Damage Factor` = `0`
     - `Headshot Damage Factor` = `10000` (or higher to ensure insta-kill).

---

## 2. Optimized PC Sensitivity (Emulator)
These settings are optimized for smooth "Drag Shots" on Windows emulators (Bluestacks/MSI).

### In-Game Settings:
- **General**: 95 - 100
- **Red Dot**: 90 - 95
- **2x Scope**: 85 - 90
- **4x Scope**: 75 - 85
- **AWM Scope**: 40 - 50

### Emulator Settings:
- **X-Axis (Horizontal)**: 1.0 - 1.5
- **Y-Axis (Vertical/Recoil)**: 2.0 - 3.0 (Higher Y-sens makes it easier to drag up for headshots).

---

## 3. Windows Mouse Registry Fix
The provided `mouse_optimizer.reg` file does the following:
- **Disables Mouse Acceleration**: Ensures 1:1 movement.
- **Sets Raw Input**: Disables Windows filters that cause inconsistent aim.
- **Optimizes Sensitivity**: Sets Windows sensitivity to the standard 6/11 (10).

## 4. C++ High-Performance Engine (v5.0)
For the **fastest possible runtime** and zero-latency optimization, I have included a native C++ engine (`optimizer.cpp`).

### Why C++?
- **Zero Overhead**: Unlike scripts or web apps, C++ talks directly to the Windows Kernel.
- **Fast Execution**: Registry patches are applied in microseconds.
- **Reliability**: Hardcoded logic ensures settings are never lost.

### How to Deploy:
1. **Install a Compiler**: Download [MinGW](https://osdn.net/projects/mingw/) or use Visual Studio.
2. **Compile**: Run `g++ optimizer.cpp -o optimizer.exe` in your terminal.
3. **Execute**: Run the `optimizer.exe` to apply the "Ultra-Fast Mouse Patch".

---

### Files Included in the Package:
- `index.html`, `style.css`, `script.js` (3D Neural Link UI)
- `server.py` (High-speed Python Backend)
- `optimizer.cpp` (Fast Runtime C++ Engine)
- `mouse_optimizer.reg` (Direct Registry Fix)
- `headshot_guide.md` (This Guide)
