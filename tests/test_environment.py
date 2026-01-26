#!/usr/bin/env python3
"""
Environment Test - Verify MobileAgent setup is correct

Run: python tests/test_environment.py

Checks:
1. Python imports work
2. ADB is available and devices connected
3. Required directories exist
4. ADBKeyboard status
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def test_imports():
    """Test Python module imports"""
    print("1. Testing imports...")
    try:
        from src.adb_helper import ADBHelper, list_devices
        from src.logger import get_logger
        print("   [OK] All modules imported")
        return True
    except ImportError as e:
        print(f"   [FAIL] Import error: {e}")
        return False


def test_directories():
    """Test required directories exist"""
    print("\n2. Testing directories...")
    dirs = ["src", "mcp", "apk_tools", "outputs", "temp"]
    all_ok = True

    for d in dirs:
        path = os.path.join(PROJECT_ROOT, d)
        if os.path.isdir(path):
            print(f"   [OK] {d}/")
        else:
            print(f"   [MISSING] {d}/")
            all_ok = False

    return all_ok


def test_adb():
    """Test ADB availability and device connection"""
    print("\n3. Testing ADB...")
    try:
        from src.adb_helper import list_devices, get_device_info

        devices = list_devices()
        if devices:
            print(f"   [OK] {len(devices)} device(s) connected")
            for d in devices:
                info = get_device_info(d)
                print(f"       - {d}: {info.get('model')} (Android {info.get('android_version')})")
            return True
        else:
            print("   [WARN] No devices connected")
            print("          Connect a device and run: adb devices")
            return False
    except Exception as e:
        print(f"   [FAIL] ADB error: {e}")
        return False


def test_adbkeyboard():
    """Test ADBKeyboard status"""
    print("\n4. Testing ADBKeyboard...")
    try:
        from src.adb_helper import list_devices, is_adbkeyboard_installed, get_current_ime

        devices = list_devices()
        if not devices:
            print("   [SKIP] No device connected")
            return True

        serial = devices[0]
        installed = is_adbkeyboard_installed(serial)
        current_ime = get_current_ime(serial)

        if installed:
            print(f"   [OK] ADBKeyboard installed")
            if "adbkeyboard" in (current_ime or "").lower():
                print(f"   [OK] ADBKeyboard is active IME")
            else:
                print(f"   [WARN] ADBKeyboard not active, current: {current_ime}")
        else:
            print("   [WARN] ADBKeyboard not installed")
            print("          Run: python -c \"from src.adb_helper import setup_adbkeyboard; setup_adbkeyboard()\"")

        return True
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False


def test_mcp_config():
    """Test MCP configuration file"""
    print("\n5. Testing MCP config...")
    mcp_path = os.path.join(PROJECT_ROOT, "mcp", "mcp_setting.json")

    if os.path.exists(mcp_path):
        print(f"   [OK] mcp_setting.json exists")
        with open(mcp_path) as f:
            content = f.read()
            if "<PROJECT_PATH>" in content:
                print("   [WARN] Config contains placeholder, run: ./set.sh")
                return False
            else:
                print("   [OK] Config has valid paths")
        return True
    else:
        print("   [MISSING] mcp_setting.json")
        print("             Run: ./set.sh")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("MobileAgent Environment Test")
    print("=" * 50)

    results = [
        test_imports(),
        test_directories(),
        test_adb(),
        test_adbkeyboard(),
        test_mcp_config(),
    ]

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")

    if all(results):
        print("Environment is ready!")
    else:
        print("Some issues found. See above for details.")

    print("=" * 50)
