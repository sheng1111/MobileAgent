# APK Tools

APK files required for automation tools.

## Contents

| APK | Purpose | Installation Command |
| --- | --- | --- |
| `mobilenext-devicekit.apk` | MCP non-ASCII input (Recommended) | `adb install apk_tools/mobilenext-devicekit.apk` |
| `ADBKeyBoard.apk` | Chinese input (for adb_helper) | `adb install apk_tools/ADBKeyBoard.apk` |
| `gnirehtet.apk` | Reverse tethering | `adb install apk_tools/gnirehtet.apk` |

## DeviceKit Installation (Recommended)

Enables support for Chinese and other non-ASCII characters in mobile-mcp's `mobile_type_keys`.

```bash
adb install apk_tools/mobilenext-devicekit.apk

```

Once installed, MCP tools will automatically use the clipboard method for text input.

* **Source:** [https://github.com/mobile-next/devicekit-android](https://github.com/mobile-next/devicekit-android)
* **Requirement:** Android 10+ (API 29)

## ADBKeyboard Installation

```bash
adb install apk_tools/ADBKeyBoard.apk
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME

```

## Verify Installation

```bash
adb shell pm list packages | grep adbkeyboard
```

## DeviceKit vs ADBKeyboard

The two do **not conflict** and can be installed simultaneously:

| Tool | Mechanism | Applicable Scenario |
| --- | --- | --- |
| DeviceKit | Clipboard | MCP `mobile_type_keys` |
| ADBKeyboard | Input Method (IME) | Python `adb_helper.type_text()` |

**Recommendation**: Install both to ensure Chinese support across all input methods.

## Sources

* mobilenext-devicekit: [https://github.com/mobile-next/devicekit-android](https://github.com/mobile-next/devicekit-android)
* ADBKeyBoard: [https://github.com/senzhk/ADBKeyBoard](https://github.com/senzhk/ADBKeyBoard)
* gnirehtet: [https://github.com/nicajonh/gnirehtet](https://github.com/nicajonh/gnirehtet)