---
name: app-action
description: Perform common app operations including launching apps, searching within apps, navigating UI, and executing typical user workflows. Use when user wants to open an app, search for something, or perform a multi-step task on the device.
---

# App Action Skill

Execute common app operations and user workflows on Android devices.

## When to Activate

- User wants to open/launch an app
- User wants to search for something in an app
- User requests a multi-step task (e.g., "search for X on YouTube")
- User wants to navigate within an app

## Core Principles

Follow the cognitive loop from AGENTS.md:

```
PERCEIVE → INTERPRET → DECIDE → ACT → VERIFY
```

**Never assume UI state. Always observe before acting.**

## Common Operations

### 1. Launch App

**Preferred: MCP Tool**
```
mobile_launch_app with packageName
```

**Fallback: Python**
```python
from src.adb_helper import ADBHelper
adb = ADBHelper()
adb.launch_app("com.example.app")
```

**Finding Package Names:**
```bash
# Search by keyword
adb shell pm list packages | grep -i youtube
# Result: package:com.google.android.youtube

# Common packages:
# Chrome: com.android.chrome
# YouTube: com.google.android.youtube
# Google Maps: com.google.android.apps.maps
# Settings: com.android.settings
# Play Store: com.android.vending
```

### 2. Search Within App

General pattern for most apps:

```
1. PERCEIVE: Get UI elements or screenshot
2. FIND: Locate search icon (🔍) or search bar
3. TAP: Click search element
4. WAIT: Allow keyboard/search UI to appear
5. TYPE: Enter search query
6. SUBMIT: Press Enter or tap search button
7. VERIFY: Confirm results appear
```

**Example: YouTube Search**
```
1. Launch YouTube: mobile_launch_app(com.google.android.youtube)
2. Wait 2 seconds for app load
3. Get elements: mobile_list_elements_on_screen
4. Find search icon (usually top-right)
5. Tap search: mobile_click_on_screen_at_coordinates
6. Wait for search field
7. Type query: mobile_type_keys
8. Submit: mobile_press_button(ENTER)
9. Verify results loaded
```

### 3. Navigate UI

**Back Navigation:**
```
mobile_press_button with button: "BACK"
```

**Home Screen:**
```
mobile_press_button with button: "HOME"
```

**Scroll/Swipe:**
```
mobile_swipe_on_screen with direction: "up" / "down" / "left" / "right"
```

### 4. Handle Common Obstacles

**Popups/Dialogs:**
```
1. Get elements - look for dismiss buttons
2. Common dismiss text: "OK", "Cancel", "Skip", "Not Now", "X", "關閉", "略過"
3. Tap the appropriate button
4. Verify popup dismissed
```

**Permission Requests:**
```
1. Identify the permission type
2. If reasonable for the task: tap "Allow" / "允許"
3. If not needed: tap "Deny" / "拒絕"
```

**Login Walls:**
```
STOP - Report to user
Do not attempt to log in without explicit instruction
```

**Ads:**
```
1. Look for "Skip" / "略過" / "X" button
2. Wait if countdown timer exists
3. Tap skip when available
```

## Task Decomposition

When given a complex task, break it down:

**Example: "幫我在蝦皮搜尋藍牙耳機"**

```
Goal: Search for Bluetooth earphones on Shopee

Subtasks:
1. Open Shopee app
   - Find package: adb shell pm list packages | grep shopee
   - Launch: mobile_launch_app

2. Navigate to search
   - Get UI elements
   - Find search bar/icon
   - Tap to focus

3. Enter search query
   - Type "藍牙耳機"
   - Submit search

4. Verify results
   - Check search results appear
   - Report to user
```

## Adaptive Strategies

### If Element Not Found:

```
1. Scroll to look for off-screen elements
2. Wait 1-2 seconds for lazy loading
3. Try alternative text (different language)
4. Take screenshot for visual analysis
5. Report if still not found
```

### If Action Has No Effect:

```
1. Verify coordinates are correct
2. Wait and retry once
3. Try alternative action (long press vs tap)
4. Check for blocking overlay
5. Report current state
```

### If Unexpected Screen:

```
1. Take screenshot
2. Identify current location
3. Determine if recoverable (back, dismiss dialog)
4. If not recoverable, report to user
```

## Tool Selection Guide

**Accessibility tree first, screenshot as fallback.**

| Action | Preferred Tool | Fallback |
|--------|---------------|----------|
| Understand UI / find elements | `mobile_list_elements_on_screen` | Screenshot (when tree insufficient) |
| Tap/Click | `mobile_click_on_screen_at_coordinates` | Python `adb.tap()` |
| Type text (Unicode) | `mobile_type_keys` + DeviceKit | Python `adb.type_text()` |
| Type text (ASCII) | `mobile_type_keys` | Python `adb.type_text()` |
| Swipe/Scroll | `mobile_swipe_on_screen` | Python `adb.swipe()` |
| Launch app | `mobile_launch_app` | Python `adb.launch_app()` |
| Press button | `mobile_press_button` | Python `adb.press_back()` etc. |

## Example Workflows

### Open Chrome and Go to URL

```
1. mobile_launch_app(com.android.chrome)
2. Wait 2s
3. mobile_list_elements_on_screen
4. Find address bar (usually has "Search or type URL" hint)
5. mobile_click_on_screen_at_coordinates(address bar coords)
6. mobile_type_keys("https://example.com")
7. mobile_press_button(ENTER)
8. Verify page loaded
```

### Search in Google Maps

```
1. mobile_launch_app(com.google.android.apps.maps)
2. Wait for map to load
3. Find search bar at top
4. Tap search bar
5. Type location name
6. Select from suggestions or press Enter
7. Verify location shown on map
```

### Send Message in LINE

```
1. mobile_launch_app(jp.naver.line.android)
2. Wait for app load
3. Navigate to Chats tab (if not already there)
4. Find target conversation or use search
5. Open conversation
6. Find message input field
7. Type message
8. Find and tap send button
9. Verify message sent
```

## Output Format

After completing an action, report:

```
Action: [What was attempted]
Result: [Success/Failure]
Current State: [Brief description of screen]
Next Options: [Available actions from here]
```
