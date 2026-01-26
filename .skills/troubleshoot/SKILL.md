---
name: troubleshoot
description: Diagnose and fix common MobileAgent issues including ADB connection problems, Unicode input failures, MCP tool errors, and device communication issues. Use when user reports errors or automation is not working.
---

# Troubleshoot Skill

Diagnose and resolve common MobileAgent problems systematically.

## When to Activate

- User reports an error or failure
- Automation actions are not working
- Unicode text input fails
- MCP tools return errors
- Device becomes unresponsive

## Diagnostic Flow

```
┌─────────────────────────────────────────┐
│  1. Identify the symptom                │
│     What exactly is failing?            │
├─────────────────────────────────────────┤
│  2. Check prerequisites                 │
│     Device? ADB? Required packages?     │
├─────────────────────────────────────────┤
│  3. Isolate the problem                 │
│     MCP vs Python? Network vs USB?      │
├─────────────────────────────────────────┤
│  4. Apply fix                           │
│     Follow specific solution            │
├─────────────────────────────────────────┤
│  5. Verify resolution                   │
│     Test the original action            │
└─────────────────────────────────────────┘
```

## Common Issues and Solutions

### Issue: No Device Found

**Symptoms:** `adb devices` shows empty list, MCP tools fail

**Diagnosis:**
```bash
# Check USB connection
lsusb | grep -i android

# Check ADB server
adb kill-server && adb start-server && adb devices
```

**Solutions:**
1. Reconnect USB cable
2. Enable USB debugging: Settings > Developer Options > USB Debugging
3. Try different USB port or cable
4. For wireless: `adb connect <device-ip>:5555`

---

### Issue: Device Unauthorized

**Symptoms:** `adb devices` shows "unauthorized"

**Solution:**
1. Check device screen for USB debugging authorization prompt
2. Tap "Allow" and check "Always allow from this computer"
3. If no prompt appears:
   ```bash
   adb kill-server
   # Revoke USB debugging authorizations on device
   # Settings > Developer Options > Revoke USB debugging authorizations
   adb start-server
   ```

---

### Issue: Unicode Input Fails (MCP)

**Symptoms:** `mobile_type_keys` outputs garbled text or fails for non-ASCII

**Diagnosis:**
```bash
adb shell pm list packages | grep mobilenext.devicekit
```

**Solution:**
```bash
# Install DeviceKit
adb install apk_tools/mobilenext-devicekit.apk

# Verify installation
adb shell pm list packages | grep mobilenext.devicekit
```

---

### Issue: Unicode Input Fails (Python)

**Symptoms:** `adb.type_text()` fails for Chinese/Japanese/Korean text

**Diagnosis:**
```bash
# Check ADBKeyboard
adb shell pm list packages | grep com.android.adbkeyboard

# Check current IME
adb shell settings get secure default_input_method
```

**Solution:**
```bash
# Install ADBKeyboard
adb install apk_tools/ADBKeyBoard.apk

# Enable and set as default
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME
```

Or use Python:
```python
from src.adb_helper import ADBHelper
adb = ADBHelper()
adb.setup_adbkeyboard()
```

---

### Issue: Tap/Click Has No Effect

**Symptoms:** `mobile_click_on_screen_at_coordinates` or `adb.tap()` does nothing

**Diagnosis:**
1. Verify coordinates are within screen bounds
2. Check if element is actually visible (not covered by popup)
3. Verify screen hasn't changed since getting coordinates

**Solutions:**
1. Get fresh UI elements: `mobile_list_elements_on_screen`
2. Take screenshot to verify current state
3. Dismiss any blocking popups/dialogs first
4. Try long press instead of tap for stubborn elements

---

### Issue: MCP Tool Timeout

**Symptoms:** MCP calls hang or timeout

**Diagnosis:**
- Check if device screen is on
- Check if device is locked
- Verify MCP server is running

**Solutions:**
1. Wake device: `adb shell input keyevent KEYCODE_WAKEUP`
2. Unlock if needed (swipe up): `adb shell input swipe 540 1800 540 800`
3. Restart MCP server if needed

---

### Issue: App Won't Launch

**Symptoms:** `mobile_launch_app` or `adb.launch_app()` fails

**Diagnosis:**
```bash
# Verify package name
adb shell pm list packages | grep <partial-name>

# Check if app is installed
adb shell pm path <package-name>
```

**Solutions:**
1. Use correct package name (case-sensitive)
2. Clear app cache: `adb shell pm clear <package>`
3. Force stop and retry: `adb shell am force-stop <package>`

---

### Issue: Screen Stuck / App Frozen

**Symptoms:** No response to any input

**Solutions:**
```bash
# Force stop current app
adb shell am force-stop <package>

# Or go home
adb shell input keyevent KEYCODE_HOME

# Last resort: restart device
adb reboot
```

## Environment Verification Script

Run comprehensive check:

```bash
python tests/test_environment.py
```

Or manually:

```python
from src.adb_helper import ADBHelper, list_devices

print("=== Environment Check ===")

# Device
devices = list_devices()
print(f"Devices: {devices}")

if devices:
    adb = ADBHelper()

    # Device info
    info = adb.get_device_info()
    print(f"Model: {info['model']}")
    print(f"Android: {info['android_version']}")
    print(f"Screen: {info['screen_size']}")

    # ADBKeyboard
    ok, msg = adb.setup_adbkeyboard()
    print(f"ADBKeyboard: {msg}")

    # Screenshot test
    path = adb.screenshot(prefix="test")
    print(f"Screenshot: {path}")
```

## Escalation

If none of the above solutions work:

1. Collect diagnostic information:
   - `adb devices -l`
   - `adb shell getprop`
   - Error messages from failed commands

2. Check device-specific issues:
   - Some devices require specific drivers
   - Manufacturer-specific ADB quirks

3. Report issue with:
   - Device model and Android version
   - Exact error message
   - Steps to reproduce
