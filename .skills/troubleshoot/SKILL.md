---
name: troubleshoot
description: Diagnose and fix MobileAgent issues. ADB problems, Unicode failures, MCP errors, device issues.
---

# Troubleshoot Skill

## Diagnostic Flow

```
Symptom → Prerequisites → Isolate → Fix → Verify
```

## Common Issues

### No Device

```bash
adb kill-server && adb start-server && adb devices
```

If still empty: check USB, enable USB debugging, try different port.

### Unauthorized

Check device for USB debugging prompt → Accept → Check "Always allow"

### Unicode Fails (MCP)

```bash
adb install apk_tools/mobilenext-devicekit.apk
```

### Unicode Fails (Python)

```bash
adb install apk_tools/ADBKeyBoard.apk
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME
```

### MCP Tool Parameter Errors

Error: `params/noParams must be object` or `params must have required property 'noParams'`

Fix: `mobile_list_available_devices` requires `{ "noParams": {} }` argument:

```json
{
  "noParams": {}
}
```

### Tap No Effect

1. Get fresh elements: `mobile_list_elements_on_screen`
2. Verify coordinates in bounds
3. Check for blocking popup/overlay
4. Try long press instead

### MCP Timeout

```bash
# Wake device
adb shell input keyevent KEYCODE_WAKEUP
# Unlock (swipe up)
adb shell input swipe 540 1800 540 800
```

### App Won't Launch

```bash
# Verify package name
adb shell pm list packages | grep <name>
# Force stop and retry
adb shell am force-stop <package>
```

### Screen Stuck

```bash
adb shell input keyevent KEYCODE_HOME
# or
adb reboot
```

## Environment Test

```bash
python tests/test_environment.py
```

## Escalation

If all else fails, collect:
- `adb devices -l`
- Device model and Android version
- Exact error message
- Steps to reproduce
