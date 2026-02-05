---
name: device-check
description: Check device connection, ADB status, and device info. Use before starting automation, when connection issues occur, or when user asks about device status.
license: MIT
metadata:
  author: MobileAgent
  version: "1.1"
compatibility: Requires ADB installed and Android device with USB debugging enabled
---

# Device Check Skill

Verify device connectivity and readiness before automation tasks.

## When to Use This Skill

- Before starting any automation workflow
- When encountering connection errors
- When user asks "Is my device connected?"
- After device disconnection/reconnection

## Quick Check

```bash
adb devices
```

| Status | Meaning |
|--------|---------|
| `device` | Ready |
| `unauthorized` | Accept prompt on device |
| `offline` | Run: `adb kill-server && adb start-server` |
| Empty | No device, check USB/debugging |

## Device Info

```bash
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell wm size
```

## Unicode Support Check

```bash
# MCP Unicode (DeviceKit)
adb shell pm list packages | grep mobilenext.devicekit

# Python Unicode (ADBKeyboard)
adb shell pm list packages | grep com.android.adbkeyboard
```

## MCP Verification

```
mobile_list_available_devices with arguments: { "noParams": {} }
```

**IMPORTANT**: This tool requires `noParams` empty object argument. Without it:
- `params/noParams must be object`
- `params must have required property 'noParams'`

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No device | Enable USB debugging in Developer Options |
| Unauthorized | Accept USB debugging prompt on device |
| Offline | `adb kill-server && adb start-server` |
| Missing APKs | `adb install apk_tools/<apk>` |

## Report Format

```
Device: [Connected/Not Connected]
Model: [model]
Android: [version]
Screen: [WxH]
Unicode: DeviceKit [Y/N], ADBKeyboard [Y/N]
```
