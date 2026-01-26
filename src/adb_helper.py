#!/usr/bin/env python3
"""
ADB Helper - Comprehensive ADB commands wrapper for AI Agents

This module provides Python interfaces for ADB operations, allowing AI agents
to execute device operations without direct terminal access.

Usage:
    from src.adb_helper import ADBHelper
    adb = ADBHelper()
    
    # Or use standalone functions
    from src.adb_helper import tap, swipe, type_text, screenshot
"""
import os
import sys
import subprocess
import time
import base64
from datetime import datetime

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from logger import get_logger

logger = get_logger(__name__)

# Directories
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp")
APK_TOOLS_DIR = os.path.join(PROJECT_ROOT, "apk_tools")

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# ADBKeyboard constants
ADBKEYBOARD_PACKAGE = "com.android.adbkeyboard"
ADBKEYBOARD_IME = f"{ADBKEYBOARD_PACKAGE}/.AdbIME"
ADBKEYBOARD_APK = os.path.join(APK_TOOLS_DIR, "ADBKeyBoard.apk")

# Common keycodes
KEYCODE = {
    "HOME": 3,
    "BACK": 4,
    "CALL": 5,
    "END_CALL": 6,
    "VOLUME_UP": 24,
    "VOLUME_DOWN": 25,
    "POWER": 26,
    "CAMERA": 27,
    "CLEAR": 28,
    "TAB": 61,
    "ENTER": 66,
    "DELETE": 67,
    "MENU": 82,
    "SEARCH": 84,
    "MEDIA_PLAY_PAUSE": 85,
    "PAGE_UP": 92,
    "PAGE_DOWN": 93,
    "ESCAPE": 111,
    "MOVE_HOME": 122,
    "MOVE_END": 123,
}


# Execute ADB command and return (success, output)
def run_adb(args, timeout=30):
    cmd = ["adb"] + args
    logger.debug(f"Executing: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            text=True
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            logger.error(f"ADB error: {result.stderr}")
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        logger.error("ADB command timeout")
        return False, "timeout"
    except FileNotFoundError:
        logger.error("ADB not found, please install Android platform-tools")
        return False, "adb not found"


# =============================================================================
# Device Management
# =============================================================================

# List all connected devices
def list_devices():
    ok, output = run_adb(["devices"])
    if not ok:
        return []

    devices = []
    for line in output.split("\n")[1:]:
        if "\t" in line:
            serial, status = line.split("\t")
            if status == "device":
                devices.append(serial)
    return devices


# Get device model name
def get_device_model(serial=None):
    args = ["shell", "getprop", "ro.product.model"]
    if serial:
        args = ["-s", serial] + args
    ok, output = run_adb(args)
    return output if ok else None


# Get screen size as (width, height)
def get_screen_size(serial=None):
    args = ["shell", "wm", "size"]
    if serial:
        args = ["-s", serial] + args
    ok, output = run_adb(args)
    if ok and "Physical size:" in output:
        size = output.split(":")[-1].strip()
        w, h = size.split("x")
        return int(w), int(h)
    return None, None


# Get comprehensive device information
def get_device_info(serial=None):
    info = {
        "serial": serial or list_devices()[0] if list_devices() else None,
        "model": get_device_model(serial),
        "screen_size": get_screen_size(serial),
    }
    
    # Get Android version
    args = ["shell", "getprop", "ro.build.version.release"]
    if serial:
        args = ["-s", serial] + args
    ok, version = run_adb(args)
    info["android_version"] = version if ok else None
    
    return info


# =============================================================================
# Screenshot
# =============================================================================

# Take screenshot and save to local
def screenshot(output_path=None, serial=None, prefix="screen"):
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUTS_DIR, f"{prefix}_{timestamp}.png")

    args = ["exec-out", "screencap", "-p"]
    if serial:
        args = ["-s", serial] + args

    cmd = ["adb"] + args
    logger.info(f"Taking screenshot: {output_path}")

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=10)
        if result.returncode == 0 and result.stdout:
            with open(output_path, "wb") as f:
                f.write(result.stdout)
            logger.info(f"Screenshot saved: {output_path}")
            return output_path
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
    return None


# =============================================================================
# Touch Operations
# =============================================================================

# Tap at screen coordinates
def tap(x, y, serial=None):
    args = ["shell", "input", "tap", str(int(x)), str(int(y))]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Tap at ({x}, {y})")
    return run_adb(args)


# Double tap at screen coordinates
def double_tap(x, y, serial=None, interval_ms=100):
    tap(x, y, serial)
    time.sleep(interval_ms / 1000)
    return tap(x, y, serial)


# Long press at screen coordinates
def long_press(x, y, duration_ms=1000, serial=None):
    args = ["shell", "input", "swipe", 
            str(int(x)), str(int(y)), str(int(x)), str(int(y)), str(duration_ms)]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Long press at ({x}, {y}) for {duration_ms}ms")
    return run_adb(args)


# Swipe from (x1, y1) to (x2, y2)
def swipe(x1, y1, x2, y2, duration_ms=300, serial=None):
    args = ["shell", "input", "swipe",
            str(int(x1)), str(int(y1)),
            str(int(x2)), str(int(y2)),
            str(duration_ms)]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Swipe ({x1},{y1}) -> ({x2},{y2})")
    return run_adb(args)


# Scroll up (swipe from bottom to top)
def scroll_up(serial=None):
    w, h = get_screen_size(serial)
    if w and h:
        return swipe(w // 2, h * 3 // 4, w // 2, h // 4, 300, serial)
    return False, "Cannot get screen size"


# Scroll down (swipe from top to bottom)
def scroll_down(serial=None):
    w, h = get_screen_size(serial)
    if w and h:
        return swipe(w // 2, h // 4, w // 2, h * 3 // 4, 300, serial)
    return False, "Cannot get screen size"


# =============================================================================
# Text Input (ADBKeyboard)
# =============================================================================

# Check if ADBKeyboard is installed
def is_adbkeyboard_installed(serial=None):
    args = ["shell", "pm", "list", "packages", ADBKEYBOARD_PACKAGE]
    if serial:
        args = ["-s", serial] + args
    ok, output = run_adb(args)
    return ADBKEYBOARD_PACKAGE in output


# Get current input method
def get_current_ime(serial=None):
    args = ["shell", "settings", "get", "secure", "default_input_method"]
    if serial:
        args = ["-s", serial] + args
    ok, output = run_adb(args)
    return output if ok else None


# Enable ADBKeyboard and set as default IME
def enable_adbkeyboard(serial=None):
    args_enable = ["shell", "ime", "enable", ADBKEYBOARD_IME]
    args_set = ["shell", "ime", "set", ADBKEYBOARD_IME]
    if serial:
        args_enable = ["-s", serial] + args_enable
        args_set = ["-s", serial] + args_set
    
    run_adb(args_enable)
    run_adb(args_set)
    return get_current_ime(serial) == ADBKEYBOARD_IME


# Install and setup ADBKeyboard
def setup_adbkeyboard(serial=None):
    if is_adbkeyboard_installed(serial):
        if enable_adbkeyboard(serial):
            return True, "ADBKeyboard already installed and enabled"
        return False, "ADBKeyboard installed but failed to enable"
    
    # Install APK
    if not os.path.exists(ADBKEYBOARD_APK):
        return False, f"APK not found: {ADBKEYBOARD_APK}"
    
    args = ["install", ADBKEYBOARD_APK]
    if serial:
        args = ["-s", serial] + args
    
    logger.info(f"Installing ADBKeyboard: {ADBKEYBOARD_APK}")
    ok, output = run_adb(args)
    if not ok:
        return False, f"Install failed: {output}"
    
    time.sleep(1)
    if enable_adbkeyboard(serial):
        return True, "ADBKeyboard installed and enabled"
    return False, "Installed but failed to enable"


# Type text on device, supports Unicode via ADBKeyboard
def type_text(text, serial=None, use_adbkeyboard=True):
    if use_adbkeyboard:
        # Ensure ADBKeyboard is ready
        if not is_adbkeyboard_installed(serial):
            ok, msg = setup_adbkeyboard(serial)
            if not ok:
                logger.warning(f"ADBKeyboard setup failed: {msg}, falling back to basic input")
                use_adbkeyboard = False
        elif get_current_ime(serial) != ADBKEYBOARD_IME:
            enable_adbkeyboard(serial)
            time.sleep(0.3)
    
    if use_adbkeyboard and is_adbkeyboard_installed(serial):
        # Use ADBKeyboard (supports Unicode)
        encoded = base64.b64encode(text.encode('utf-8')).decode('ascii')
        args = ["shell", "am", "broadcast", "-a", "ADB_INPUT_B64", "--es", "msg", encoded]
        if serial:
            args = ["-s", serial] + args
        logger.info(f"Type text via ADBKeyboard: {text[:50]}...")
        ok, output = run_adb(args)
        if ok and "result=0" in output:
            return True, "Text input successful"
        return False, f"Input failed: {output}"
    else:
        # Basic input (ASCII only)
        safe_text = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
        args = ["shell", "input", "text", safe_text]
        if serial:
            args = ["-s", serial] + args
        logger.info(f"Type text via basic input: {text[:50]}...")
        return run_adb(args)


# Tap input field and type text
def tap_and_type(x, y, text, serial=None, wait_ms=500):
    # Tap to focus
    ok, msg = tap(x, y, serial)
    if not ok:
        return False, f"Tap failed: {msg}"
    
    # Wait for keyboard
    time.sleep(wait_ms / 1000)
    
    # Type text
    return type_text(text, serial)


# Clear text by sending DELETE key multiple times
def clear_text(length=100, serial=None):
    args = ["shell", "input", "keyevent"]
    if serial:
        args = ["-s", serial] + args
    
    # Send DELETE key
    for _ in range(length):
        run_adb(args + [str(KEYCODE["DELETE"])])
    
    return True, f"Sent {length} DELETE keys"


# =============================================================================
# Key Events
# =============================================================================

# Press a key by keycode
def press_key(keycode, serial=None):
    args = ["shell", "input", "keyevent", str(keycode)]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Press key: {keycode}")
    return run_adb(args)


# Press a key by name (e.g., 'HOME', 'BACK', 'ENTER')
def press_key_by_name(name, serial=None):
    name = name.upper()
    if name not in KEYCODE:
        return False, f"Unknown key: {name}. Available: {list(KEYCODE.keys())}"
    return press_key(KEYCODE[name], serial)


# Press HOME key
def press_home(serial=None):
    return press_key(KEYCODE["HOME"], serial)


# Press BACK key
def press_back(serial=None):
    return press_key(KEYCODE["BACK"], serial)


# Press ENTER key
def press_enter(serial=None):
    return press_key(KEYCODE["ENTER"], serial)


# =============================================================================
# App Management
# =============================================================================

# Launch an app by package name
def launch_app(package, serial=None):
    args = ["shell", "monkey", "-p", package, "-c",
            "android.intent.category.LAUNCHER", "1"]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Launch app: {package}")
    return run_adb(args)


# Force stop an app
def stop_app(package, serial=None):
    args = ["shell", "am", "force-stop", package]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Stop app: {package}")
    return run_adb(args)


# List installed packages
def list_packages(serial=None, filter_text=None):
    args = ["shell", "pm", "list", "packages"]
    if serial:
        args = ["-s", serial] + args
    ok, output = run_adb(args)
    if ok:
        packages = [line.replace("package:", "") for line in output.split("\n")]
        if filter_text:
            packages = [p for p in packages if filter_text.lower() in p.lower()]
        return packages
    return []


# Open URL in default browser
def open_url(url, serial=None):
    args = ["shell", "am", "start", "-a", "android.intent.action.VIEW", "-d", url]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Open URL: {url}")
    return run_adb(args)


# =============================================================================
# File Operations
# =============================================================================

# Pull file from device to local
def pull_file(remote_path, local_path, serial=None):
    args = ["pull", remote_path, local_path]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Pull file: {remote_path} -> {local_path}")
    return run_adb(args)


# Push file from local to device
def push_file(local_path, remote_path, serial=None):
    args = ["push", local_path, remote_path]
    if serial:
        args = ["-s", serial] + args
    logger.info(f"Push file: {local_path} -> {remote_path}")
    return run_adb(args)


# =============================================================================
# ADBHelper Class (Stateful wrapper)
# =============================================================================

class ADBHelper:
    """
    Stateful ADB helper class that caches device ID.
    
    Usage:
        adb = ADBHelper()  # Auto-detect device
        adb = ADBHelper(device_id="192.168.1.100:5555")  # Specific device
        
        adb.tap(540, 1200)
        adb.type_text("Hello World")
        adb.screenshot(prefix="test")
    """
    
    # Initialize with optional device ID
    def __init__(self, device_id=None):
        self.device_id = device_id
        if not self.device_id:
            devices = list_devices()
            if devices:
                self.device_id = devices[0]
                logger.info(f"Auto-detected device: {self.device_id}")
    
    def tap(self, x, y):
        return tap(x, y, self.device_id)
    
    def double_tap(self, x, y, interval_ms=100):
        return double_tap(x, y, self.device_id, interval_ms)
    
    def long_press(self, x, y, duration_ms=1000):
        return long_press(x, y, duration_ms, self.device_id)
    
    def swipe(self, x1, y1, x2, y2, duration_ms=300):
        return swipe(x1, y1, x2, y2, duration_ms, self.device_id)
    
    def scroll_up(self):
        return scroll_up(self.device_id)
    
    def scroll_down(self):
        return scroll_down(self.device_id)
    
    def type_text(self, text):
        return type_text(text, self.device_id)
    
    def tap_and_type(self, x, y, text, wait_ms=500):
        return tap_and_type(x, y, text, self.device_id, wait_ms)
    
    def clear_text(self, length=100):
        return clear_text(length, self.device_id)
    
    def press_key(self, keycode):
        return press_key(keycode, self.device_id)
    
    def press_key_by_name(self, name):
        return press_key_by_name(name, self.device_id)
    
    def press_home(self):
        return press_home(self.device_id)
    
    def press_back(self):
        return press_back(self.device_id)
    
    def press_enter(self):
        return press_enter(self.device_id)
    
    def screenshot(self, output_path=None, prefix="screen"):
        return screenshot(output_path, self.device_id, prefix)
    
    def launch_app(self, package):
        return launch_app(package, self.device_id)
    
    def stop_app(self, package):
        return stop_app(package, self.device_id)
    
    def list_packages(self, filter_text=None):
        return list_packages(self.device_id, filter_text)
    
    def open_url(self, url):
        return open_url(url, self.device_id)
    
    def get_screen_size(self):
        return get_screen_size(self.device_id)
    
    def get_device_info(self):
        return get_device_info(self.device_id)
    
    def setup_adbkeyboard(self):
        return setup_adbkeyboard(self.device_id)


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print("=== ADB Helper Test ===\n")
    
    devices = list_devices()
    print(f"Connected devices: {devices}")

    if devices:
        adb = ADBHelper(devices[0])
        info = adb.get_device_info()
        print(f"Device info: {info}")
        
        # Test screenshot
        img = adb.screenshot(prefix="test")
        if img:
            print(f"Screenshot saved: {img}")
        
        # Test ADBKeyboard
        ok, msg = adb.setup_adbkeyboard()
        print(f"ADBKeyboard setup: {msg}")
    else:
        print("No device connected")
