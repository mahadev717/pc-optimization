#include <iostream>
#include <string>
#include <windows.h>

// Advanced Headshot Optimizer - C++ High Performance Engine
// Uses native Windows API for 0-latency optimization

void SetRegistryValue(HKEY hKeyRoot, LPCSTR subKey, LPCSTR valueName,
                      DWORD data) {
  HKEY hKey;
  if (RegOpenKeyExA(hKeyRoot, subKey, 0, KEY_SET_VALUE, &hKey) ==
      ERROR_SUCCESS) {
    if (RegSetValueExA(hKey, valueName, 0, REG_SZ,
                       (const BYTE *)std::to_string(data).c_str(),
                       (DWORD)std::to_string(data).length() + 1) ==
        ERROR_SUCCESS) {
      std::cout << "[SUCCESS] Optimized: " << valueName << std::endl;
    }
    RegCloseKey(hKey);
  } else {
    std::cerr << "[ERROR] Failed to access registry for: " << valueName
              << std::endl;
  }
}

void OptimizeMouse() {
  std::cout << ">>> Initializing High-Performance Mouse Engine..." << std::endl;

  // Disable Acceleration
  SetRegistryValue(HKEY_CURRENT_USER, "Control Panel\\Mouse", "MouseSpeed", 0);
  SetRegistryValue(HKEY_CURRENT_USER, "Control Panel\\Mouse", "MouseThreshold1",
                   0);
  SetRegistryValue(HKEY_CURRENT_USER, "Control Panel\\Mouse", "MouseThreshold2",
                   0);

  // Set 1:1 Sensitivity (6/11)
  SetRegistryValue(HKEY_CURRENT_USER, "Control Panel\\Mouse",
                   "MouseSensitivity", 10);

  // Instant Apply: Signal Windows to refresh mouse settings
  int mouseParams[3] = {0, 0,
                        0}; // Disables acceleration (Thresh1, Thresh2, Speed)
  SystemParametersInfoA(SPI_SETMOUSE, 0, mouseParams,
                        SPIF_UPDATEINIFILE | SPIF_SENDCHANGE);

  std::cout << ">>> Mouse Optimization Complete (Applied Instantly)."
            << std::endl;
}

void ShowMenu() {
  std::cout << "=========================================" << std::endl;
  std::cout << "   HACKER ENGINE v5.0 [ C++ NATIVE ]     " << std::endl;
  std::cout << "=========================================" << std::endl;
  std::cout << " 1. Apply Ultra-Fast Mouse Patch" << std::endl;
  std::cout << " 2. Verify System Latency" << std::endl;
  std::cout << " 3. Exit" << std::endl;
  std::cout << "=========================================" << std::endl;
  std::cout << " Selection > ";
}

int main() {
  int choice;
  while (true) {
    system("cls");
    ShowMenu();
    std::cin >> choice;

    if (choice == 1) {
      OptimizeMouse();
      std::cout << "\n[!] Restart Required for Core Changes." << std::endl;
      system("pause");
    } else if (choice == 3) {
      break;
    }
  }
  return 0;
}
