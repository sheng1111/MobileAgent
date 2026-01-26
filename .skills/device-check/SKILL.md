---
name: device-check
description: Check Android device connection status, verify ADB setup, and display device information. Use when user asks about device status, connection issues, or wants to verify setup before automation tasks.
---

# Device Check Skill

Verify Android device connectivity and environment setup for MobileAgent.

## When to Activate

- User asks "Is my device connected?"
- User wants to check device status before starting tasks
- User mentions connection problems
- Starting a new automation session

## Execution Steps

### 1. Check ADB Connection

Run the following command to list connected devices:

```bash
adb devices
```

**Expected output:**
- `device` status = connected and ready
- `unauthorized` = USB debugging not authorized on device
- `offline` = device detected but not responding
- Empty list = no device connected

### 2. Get Device Information

If device is connected, gather details:

```bash
# Device model
adb shell getprop ro.product.model

# Android version
adb shell getprop ro.build.version.release

# Screen size
adb shell wm size
```

### 3. Verify Required APKs

Check if Unicode input tools are installed:

```bash
# Check DeviceKit (for MCP Unicode)
adb shell pm list packages | grep mobilenext.devicekit

# Check ADBKeyboard (for Python Unicode)
adb shell pm list packages | grep com.android.adbkeyboard
```

### 4. Test MCP Connection (Optional)

If MCP tools are available, verify device accessibility:

```
Use mobile_list_available_devices to confirm MCP can see the device
```

## Troubleshooting Guidance

| Status | Issue | Solution |
|--------|-------|----------|
| No devices | USB not connected or debugging off | Enable USB debugging in Developer Options |
| unauthorized | Permission not granted | Accept USB debugging prompt on device |
| offline | ADB daemon issue | Run `adb kill-server && adb start-server` |
| Missing APKs | Unicode input won't work | Install from `apk_tools/` directory |

## Report Format

Provide a summary in user's language:

```
Device Status: [Connected/Not Connected]
Model: [device model]
Android: [version]
Screen: [width x height]
Unicode Support:
  - DeviceKit (MCP): [Installed/Not Installed]
  - ADBKeyboard (Python): [Installed/Not Installed]
```

## Python Alternative

If bash commands fail, use Python:

```python
from src.adb_helper import ADBHelper, list_devices

devices = list_devices()
if devices:
    adb = ADBHelper(devices[0])
    info = adb.get_device_info()
    print(info)
```
