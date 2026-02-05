---
name: app-action
description: Quick single-step app operations like launch, tap, type, swipe. Use for simple actions. For research, browsing, or multi-step tasks, use app-explore skill instead.
license: MIT
metadata:
  author: MobileAgent
  version: "1.1"
compatibility: Requires mobile-mcp MCP server and connected Android device
---

# App Action Skill

Quick reference for single-step operations.

## When to Use This Skill

- Simple, one-time actions (tap a button, launch an app)
- Quick text input
- Navigation (back, home, scroll)

## When NOT to Use This Skill

- User asks to find/research/compare something → use `app-explore`
- Task requires browsing multiple items → use `app-explore`
- Information gathering before reporting → use `app-explore`

Quick reference for single-step operations. For research or complex multi-step tasks, use `app-explore` skill.

## Core Loop

```
OBSERVE → ACT → VERIFY
```

## Element-First Strategy (CRITICAL)

**NEVER guess coordinates from screenshots. ALWAYS use element list first.**

```
CORRECT:
1. mobile_list_elements_on_screen → Find target by text/type/id
2. Calculate center: (x + width/2, y + height/2)
3. mobile_click_on_screen_at_coordinates

WRONG:
1. mobile_take_screenshot → Guess where to click
2. mobile_click_on_screen_at_coordinates → Miss, repeat
```

## MCP Tools Quick Reference

| Priority | Tool | When |
|----------|------|------|
| 1 | `mobile_list_elements_on_screen` | Before ANY click/tap |
| 2 | `mobile_click_on_screen_at_coordinates` | Click element center |
| 3 | `mobile_type_keys` | Text input |
| 4 | `mobile_swipe_on_screen` | Scroll/navigate |
| 5 | `mobile_press_button` | BACK, HOME, ENTER |
| 6 | `mobile_launch_app` | Start app by package |
| 7 | `mobile_take_screenshot` | ONLY when element not in tree |

## Python Fallback

```python
from src.adb_helper import ADBHelper
adb = ADBHelper()
adb.tap(x, y)
adb.type_text("text")
adb.swipe(x1, y1, x2, y2)
adb.screenshot(prefix="step")
```

## Common Patterns

| Task | Steps |
|------|-------|
| Open app | `mobile_launch_app` → verify |
| Tap button | Get elements → find by pattern → tap coords |
| Type text | Tap input field → type_keys |
| Scroll | swipe from center up/down |
| Go back | `mobile_press_button` BACK |

## When to Use app-explore

- User asks to find/research/compare something
- Task requires browsing multiple items
- Information gathering before reporting
