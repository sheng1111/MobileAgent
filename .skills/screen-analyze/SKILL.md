---
name: screen-analyze
description: Analyze current screen state, find UI elements, and determine clickable coordinates. Use when user asks what's on screen, needs to find a button/element, or wants to understand the current UI state before taking action.
---

# Screen Analyze Skill

Comprehensively analyze Android device screen to understand UI state and locate elements.

## When to Activate

- User asks "What's on the screen?"
- Need to find a specific element (button, text field, link)
- Before performing tap/click actions
- Debugging why an action failed
- Understanding current app state

## Tool Priority

**Accessibility tree first, screenshot as fallback.**

| Priority | Tool | When to Use |
|----------|------|-------------|
| 1st | `mobile_list_elements_on_screen` | Default choice - provides coordinates, text, element types |
| 2nd | `mobile_take_screenshot` | When tree is insufficient or visual verification needed |

## Analysis Approach

### Step 1: Get UI Hierarchy (Start Here)

```
mobile_list_elements_on_screen
```

Returns structured data: element type, text, coordinates, bounds, clickability.

**Prefer accessibility tree because:**
- Exact coordinates ready for tap/click
- Structured data, no image parsing needed
- Includes element state and hierarchy

### Step 2: Visual Screenshot (When Needed)

```
mobile_take_screenshot
```

**Use screenshot when:**
- Accessibility tree lacks useful elements
- Visual verification needed (colors, images, layout)
- Custom views without accessibility labels
- User asks to see the screen

### Step 3: Interpret Screen State

Answer these questions:

1. **Where am I?**
   - App name (from status bar or header)
   - Screen title or breadcrumb
   - Position in navigation flow

2. **What can I do here?**
   - Available buttons and their purposes
   - Input fields
   - Navigation options (tabs, menu, back)

3. **What's the state?**
   - Loading? (spinners, progress bars)
   - Empty? (no content messages)
   - Error? (error dialogs, retry buttons)
   - Success? (confirmation messages)

4. **What might block me?**
   - Popups or dialogs
   - Permission requests
   - Login walls
   - Ads or promotions

## Element Location Strategy

### Finding by Text

```
Look for elements where:
- text matches exactly
- text contains keyword
- contentDescription matches
```

### Finding by Type

| Looking for | Element types |
|-------------|--------------|
| Buttons | Button, ImageButton, clickable=true |
| Text input | EditText, TextInputEditText |
| Links | TextView with clickable=true |
| Images | ImageView, ImageButton |
| Lists | RecyclerView, ListView items |

### Finding by Position

```
Common UI patterns:
- Search: Top of screen, often with magnifying glass icon
- Navigation: Bottom tabs or top-left hamburger menu
- Back: Top-left arrow or system back button
- Submit/Confirm: Bottom-right or center-bottom
- Close/Cancel: Top-right X or bottom-left
```

## Output Format

Provide analysis in user's language:

```
Current Screen Analysis
=======================

App: [App name]
Screen: [Screen title/description]
State: [Normal/Loading/Error/etc.]

Key Elements Found:
1. [Element description] - coordinates (x, y)
2. [Element description] - coordinates (x, y)
...

Possible Actions:
- [Action description]: tap (x, y)
- [Action description]: type in field at (x, y)
...

Observations:
- [Any popups, loading states, or blockers]
- [Relevant state information]
```

## Common Patterns Recognition

### Search Interface
```
Elements to look for:
- Search icon (magnifying glass)
- "Search" or "搜尋" text
- EditText at top of screen
- Hint text like "Search..." or "輸入搜尋..."
```

### Login Screen
```
Elements to look for:
- Username/Email field
- Password field
- "Login" / "Sign in" / "登入" button
- "Forgot password" link
- Social login buttons (Google, Facebook, etc.)
```

### List/Feed
```
Elements to look for:
- Repeating item structure
- Scroll indicators
- Load more / pagination
- Filter/sort options
```

### Dialog/Popup
```
Elements to look for:
- Overlay background
- Title text
- Message content
- Action buttons (OK, Cancel, Allow, Deny)
- Close X button
```

## Python Fallback

If MCP tools fail, use Python for screenshot:

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()
path = adb.screenshot(prefix="analyze")
print(f"Screenshot saved: {path}")

# Get screen size for coordinate reference
w, h = adb.get_screen_size()
print(f"Screen size: {w}x{h}")
```

## Tips for Accurate Analysis

1. **Always refresh before acting** - Screen state changes; don't use stale element data

2. **Consider device language** - UI text may be in different language than expected

3. **Check element visibility** - Elements may exist in tree but be off-screen; scroll if needed

4. **Verify clickability** - Not all visible elements are interactive

5. **Account for animations** - Wait 500ms-1s after screen transitions before analyzing
