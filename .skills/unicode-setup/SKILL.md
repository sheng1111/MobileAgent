---
name: unicode-setup
description: Setup Unicode text input (Chinese, Japanese, Korean). Install DeviceKit for MCP, ADBKeyboard for Python.
---

# Unicode Setup Skill

## Why Needed

Default ADB only supports ASCII. Unicode requires special IME apps.

| Tool | For | APK |
|------|-----|-----|
| DeviceKit | MCP `mobile_type_keys` | `apk_tools/mobilenext-devicekit.apk` |
| ADBKeyboard | Python `adb.type_text()` | `apk_tools/ADBKeyBoard.apk` |

## Install Both (Recommended)

```bash
adb install apk_tools/mobilenext-devicekit.apk
adb install apk_tools/ADBKeyBoard.apk
adb shell pm list packages | grep -E "mobilenext|adbkeyboard"
```

## ADBKeyboard Activation

```bash
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME
adb shell settings get secure default_input_method
```

## Verification

Test in any text field:
```
mobile_type_keys with text: "Test Unicode"
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Install fails | `adb install -r <apk>` |
| IME not activating | `adb shell ime list -a` then enable manually |
| Still garbled | Clear field first, verify app supports Unicode |

## Revert to Original Keyboard

```bash
adb shell ime list -s
# Set back (example: Gboard)
adb shell ime set com.google.android.inputmethod.latin/.LatinIME
```
