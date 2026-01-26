---
name: unicode-setup
description: Configure Unicode text input support for Android automation. Install and setup DeviceKit (for MCP) and ADBKeyboard (for Python) to enable Chinese, Japanese, Korean, and other non-ASCII text input. Use when text input fails or before tasks requiring Unicode.
---

# Unicode Setup Skill

Enable full Unicode text input support for MobileAgent automation.

## When to Activate

- User mentions Chinese/Japanese/Korean text input
- Text input shows garbled characters or fails
- Setting up a new device for automation
- User asks about typing non-English text

## Background

Android's default `adb shell input text` only supports ASCII characters. For Unicode (CJK, emoji, special characters), we need special input method apps:

| Tool | Used By | APK Location |
|------|---------|--------------|
| DeviceKit | MCP `mobile_type_keys` | `apk_tools/mobilenext-devicekit.apk` |
| ADBKeyboard | Python `adb.type_text()` | `apk_tools/ADBKeyBoard.apk` |

**Recommendation:** Install both for full compatibility.

## Installation Steps

### Option 1: Install Both (Recommended)

```bash
# Install DeviceKit for MCP Unicode support
adb install apk_tools/mobilenext-devicekit.apk

# Install ADBKeyboard for Python Unicode support
adb install apk_tools/ADBKeyBoard.apk

# Verify installations
adb shell pm list packages | grep -E "mobilenext|adbkeyboard"
```

### Option 2: DeviceKit Only (MCP)

```bash
adb install apk_tools/mobilenext-devicekit.apk
```

### Option 3: ADBKeyboard Only (Python)

```bash
# Install
adb install apk_tools/ADBKeyBoard.apk

# Enable and set as default IME
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME

# Verify
adb shell settings get secure default_input_method
# Should output: com.android.adbkeyboard/.AdbIME
```

## Verification

### Test MCP Unicode

```
1. Open any app with text input (e.g., Chrome, Notes)
2. Tap on text field to focus
3. Use mobile_type_keys with text: "測試中文 テスト 테스트"
4. Verify text appears correctly
```

### Test Python Unicode

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()

# Setup (auto-installs if needed)
ok, msg = adb.setup_adbkeyboard()
print(f"Setup: {msg}")

# Test typing
ok, msg = adb.type_text("測試中文 テスト 테스트")
print(f"Type: {msg}")
```

## Troubleshooting

### APK Not Found

```bash
# Check if APKs exist
ls -la apk_tools/

# If missing, they should be in the project repository
# Download or copy them to apk_tools/ directory
```

### Installation Fails

```bash
# Check available space
adb shell df /data

# Try with replace flag
adb install -r apk_tools/ADBKeyBoard.apk

# Check for signature conflicts
adb uninstall com.android.adbkeyboard
adb install apk_tools/ADBKeyBoard.apk
```

### ADBKeyboard Not Activating

```bash
# List available input methods
adb shell ime list -a

# Enable explicitly
adb shell ime enable com.android.adbkeyboard/.AdbIME

# Set as default
adb shell ime set com.android.adbkeyboard/.AdbIME

# Force refresh
adb shell am broadcast -a com.android.adbkeyboard.REFRESH
```

### Text Still Garbled

1. Ensure the target app supports Unicode
2. Check encoding: ADBKeyboard uses UTF-8 with Base64 encoding
3. Try clearing the text field first before typing

```python
adb.clear_text(50)  # Clear existing text
adb.type_text("新的文字")
```

### Reverting to Original Keyboard

After automation, users may want their original keyboard back:

```bash
# List available IMEs
adb shell ime list -s

# Set back to default (example for Gboard)
adb shell ime set com.google.android.inputmethod.latin/.LatinIME

# Or for Samsung keyboard
adb shell ime set com.samsung.android.honeyboard/.service.HoneyBoardService
```

## How It Works

### ADBKeyboard Method

1. Text is encoded to Base64 (UTF-8)
2. Sent via Android broadcast intent
3. ADBKeyboard receives and inputs the decoded text

```python
# Internal mechanism
encoded = base64.b64encode(text.encode('utf-8')).decode('ascii')
adb shell am broadcast -a ADB_INPUT_B64 --es msg <encoded>
```

### DeviceKit Method

DeviceKit provides a similar broadcast-based input for MCP tools, handling Unicode transparently.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `adb install apk_tools/ADBKeyBoard.apk` | Install ADBKeyboard |
| `adb install apk_tools/mobilenext-devicekit.apk` | Install DeviceKit |
| `adb shell ime enable com.android.adbkeyboard/.AdbIME` | Enable ADBKeyboard |
| `adb shell ime set com.android.adbkeyboard/.AdbIME` | Set as default |
| `adb shell ime list -s` | List active IMEs |
| `adb shell settings get secure default_input_method` | Check current IME |
