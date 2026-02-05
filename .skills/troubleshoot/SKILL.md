---
name: troubleshoot
description: Diagnose and fix MobileAgent issues systematically. Use when encountering ADB problems, Unicode failures, MCP errors, device connection issues, or automation failures.
license: MIT
metadata:
  author: MobileAgent
  version: "2.0"
compatibility: Requires ADB, Python 3.8+, Node.js 18+
---

# Troubleshoot Skill

Systematic diagnostics for MobileAgent issues. Follow the diagnostic flow to identify and resolve problems efficiently.

## When to Use This Skill

Use this skill when you encounter:
- Device connection failures
- MCP tool errors
- Unicode/text input issues
- Automation action failures (tap not working, etc.)
- App launch failures

## Diagnostic Flow

```
SYMPTOM → CATEGORIZE → PREREQUISITES → ISOLATE → FIX → VERIFY
```

1. **Symptom**: What exactly failed? Error message?
2. **Categorize**: Which category below matches?
3. **Prerequisites**: Check basic requirements first
4. **Isolate**: Narrow down the root cause
5. **Fix**: Apply the appropriate solution
6. **Verify**: Confirm the fix works

---

## Category 1: Device Connection Issues

### Symptom: No device detected

**Prerequisites check:**
```bash
# Check ADB is installed
adb version

# Check USB connection physically
# Check device screen is on and unlocked
```

**Diagnostic steps:**
```bash
# Step 1: Restart ADB server
adb kill-server && adb start-server

# Step 2: List devices
adb devices -l

# Step 3: Check USB debugging is enabled on device
# Settings → Developer options → USB debugging → ON
```

**Common causes:**
| Symptom | Cause | Fix |
|---------|-------|-----|
| Empty device list | USB debugging disabled | Enable in Developer options |
| `no permissions` | udev rules missing (Linux) | Add udev rules, restart |
| `offline` | USB debugging not authorized | Accept prompt on device |
| Device not listed | Bad USB cable/port | Try different cable/port |

### Symptom: Device shows "unauthorized"

**Fix:**
1. Check device screen for USB debugging prompt
2. Tap "Allow" on device
3. Check "Always allow from this computer"
4. Run `adb devices` again

---

## Category 2: MCP Tool Errors

### Symptom: `params/noParams must be object`

**Cause:** `mobile_list_available_devices` requires explicit empty params.

**Fix:** Pass the correct argument structure:
```json
{
  "noParams": {}
}
```

### Symptom: MCP timeout

**Diagnostic steps:**
```bash
# Check device is awake
adb shell dumpsys power | grep 'mWakefulness'

# Wake device if sleeping
adb shell input keyevent KEYCODE_WAKEUP

# Unlock screen (swipe up)
adb shell input swipe 540 1800 540 800
```

### Symptom: MCP server not responding

**Diagnostic steps:**
```bash
# Check if MCP process is running
ps aux | grep mobile-mcp

# Restart MCP server
# Kill existing and let AI Agent restart it
pkill -f mobile-mcp
```

**Common MCP errors:**
| Error | Cause | Fix |
|-------|-------|-----|
| Connection refused | MCP not running | Restart MCP server |
| Timeout | Device locked/slow | Wake device, wait |
| Invalid response | Old MCP version | Update: `npx -y @mobilenext/mobile-mcp@latest` |

---

## Category 3: Unicode/Text Input Issues

### Symptom: Unicode input fails (MCP)

**Diagnostic steps:**
```bash
# Check DeviceKit is installed
adb shell pm list packages | grep devicekit
```

**Fix:**
```bash
# Install DeviceKit APK
adb install apk_tools/mobilenext-devicekit.apk
```

### Symptom: Unicode input fails (Python)

**Diagnostic steps:**
```bash
# Check ADBKeyboard is installed
adb shell pm list packages | grep adbkeyboard

# Check current IME
adb shell settings get secure default_input_method
```

**Fix:**
```bash
# Install ADBKeyboard
adb install apk_tools/ADBKeyBoard.apk

# Enable and set as default
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME
```

**Verify:**
```bash
# Test input
adb shell input text "test"
adb shell am broadcast -a ADB_INPUT_TEXT --es msg "你好"
```

---

## Category 4: Automation Action Failures

### Symptom: Tap/Click has no effect

**Diagnostic steps:**
1. Get fresh element list: `mobile_list_elements_on_screen`
2. Verify coordinates are within screen bounds
3. Check for blocking overlay/popup
4. Check element is clickable

**Common causes:**
| Symptom | Cause | Fix |
|---------|-------|-----|
| Tap ignored | Coordinates outside element | Recalculate center |
| Element not found | Screen changed | Refresh element list |
| Click blocked | Popup/dialog overlay | Dismiss popup first |
| Wrong location | Screen resolution mismatch | Use percentages |

**Fix pattern:**
```
1. mobile_list_elements_on_screen
2. Find element by text/type/resourceId
3. Calculate: x = element.x + element.width/2
             y = element.y + element.height/2
4. mobile_click_on_screen_at_coordinates
5. Verify screen changed
```

### Symptom: Swipe not working

**Diagnostic steps:**
```bash
# Test manual swipe
adb shell input swipe 540 1500 540 500 300

# Check if screen responds
```

**Common fixes:**
- Increase swipe duration (last param in ms)
- Start/end points too close to edge
- Content not scrollable

---

## Category 5: App Issues

### Symptom: App won't launch

**Diagnostic steps:**
```bash
# Verify package name
adb shell pm list packages | grep <partial_name>

# Try force stop first
adb shell am force-stop <package>

# Launch with activity manager
adb shell am start -n <package>/<activity>
```

**Common package names:**
| App | Package |
|-----|---------|
| Threads | `com.instagram.barcelona` |
| Instagram | `com.instagram.android` |
| Facebook | `com.facebook.katana` |
| X/Twitter | `com.twitter.android` |
| TikTok | `com.zhiliaoapp.musically` |
| WeChat | `com.tencent.mm` |
| LINE | `jp.naver.line.android` |

### Symptom: App crashes repeatedly

**Diagnostic steps:**
```bash
# Check for crash logs
adb logcat -d | grep -i crash

# Clear app data (destructive)
adb shell pm clear <package>
```

---

## Category 6: Screen/Display Issues

### Symptom: Screen stuck/frozen

**Fix options (least to most destructive):**
```bash
# Option 1: Press HOME
adb shell input keyevent KEYCODE_HOME

# Option 2: Press BACK repeatedly
adb shell input keyevent KEYCODE_BACK
adb shell input keyevent KEYCODE_BACK
adb shell input keyevent KEYCODE_BACK

# Option 3: Force stop current app
adb shell am force-stop $(adb shell dumpsys window | grep -E 'mCurrentFocus' | cut -d'/' -f1 | cut -d'{' -f2 | tr -d ' ')

# Option 4: Reboot device
adb reboot
```

---

## Environment Verification

Run full environment test:
```bash
python tests/test_environment.py
```

Or manual checks:
```bash
# 1. Python version
python3 --version  # Should be 3.8+

# 2. Node.js version
node --version  # Should be 18+

# 3. ADB version
adb version

# 4. Device connection
adb devices -l

# 5. MCP server
npx -y @mobilenext/mobile-mcp@latest --version
```

---

## Escalation Checklist

If all troubleshooting fails, collect this information before reporting:

```bash
# System info
echo "=== System ===" && uname -a
echo "=== Python ===" && python3 --version
echo "=== Node ===" && node --version
echo "=== ADB ===" && adb version

# Device info
echo "=== Device ===" && adb devices -l
echo "=== Android ===" && adb shell getprop ro.build.version.release
echo "=== Model ===" && adb shell getprop ro.product.model

# Error reproduction
echo "=== Steps to reproduce ===" 
# Document exact steps
```

**Report template:**
```
## Issue
[Brief description]

## Environment
- OS: [Linux/macOS/Windows]
- Python: [version]
- Node: [version]
- Android: [version]
- Device: [model]

## Steps to Reproduce
1. ...
2. ...

## Expected Behavior
...

## Actual Behavior
...

## Error Message
```
[paste full error]
```

## Already Tried
- [ ] Restarted ADB server
- [ ] Reinstalled DeviceKit/ADBKeyboard
- [ ] Checked device permissions
```

---

## Quick Reference Card

| Problem | Quick Fix |
|---------|-----------|
| No device | `adb kill-server && adb start-server` |
| Unauthorized | Accept USB debugging on device |
| Unicode fails | `adb install apk_tools/mobilenext-devicekit.apk` |
| Tap no effect | Refresh element list, recalculate coords |
| App stuck | `adb shell input keyevent KEYCODE_HOME` |
| MCP timeout | Wake device: `adb shell input keyevent KEYCODE_WAKEUP` |
