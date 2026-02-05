---
name: screen-analyze
description: Analyze current screen state, find UI elements, and get precise coordinates for automation. Use before performing actions or when user asks about what's on screen.
license: MIT
metadata:
  author: MobileAgent
  version: "1.1"
compatibility: Requires mobile-mcp MCP server connected to device
---

# Screen Analyze Skill

Understand the current screen state and locate UI elements for automation.

## When to Use This Skill

- Before clicking/tapping any element
- When user asks "What's on the screen?"
- When automation actions fail (wrong location)
- To verify screen changed after an action

## Tool Priority (CRITICAL)

**ALWAYS use accessibility tree FIRST. Screenshots are LAST resort.**

| Priority | Tool | Use When |
|----------|------|----------|
| 1 | `mobile_list_elements_on_screen` | Finding elements, getting coordinates |
| 2 | `mobile_take_screenshot` | Element not in tree, visual verify, debug |

### Why This Order Matters

- **Speed**: Element list ~100ms vs screenshot+vision 2-5s
- **Accuracy**: Element bounds are pixel-perfect, visual guessing is error-prone
- **Reliability**: Elements have stable identifiers, visual positions vary

### Element Selection

Find targets by (in order of preference):
1. **Identifier/resourceId** - Most stable, use when available
2. **Text content** - Exact or partial match
3. **Element type** - Button, EditText, ImageButton, etc.
4. **Position pattern** - Top-right for menu, bottom for nav

### Click Point Calculation

```
Given: { x: 100, y: 200, width: 80, height: 40 }
Click: (x + width/2, y + height/2) = (140, 220)
```

### When to Use Screenshot

- Element not in accessibility tree (custom UI, games)
- Verifying visual state (colors, images, layout)
- Debugging mismatches between tree and display

## Analysis Questions

1. **Where am I?** - App, screen, navigation position
2. **What can I do?** - Buttons, inputs, links, gestures
3. **What's the state?** - Loading, empty, error, success
4. **What's blocking?** - Popups, permissions, overlays

## Finding Elements

### By Pattern (not position)

| Element Type | Look For |
|--------------|----------|
| Search | magnifying glass icon, "Search" text, EditText at top |
| Submit | "OK"/"Send"/confirm text, bottom-right |
| Close | X icon, "Cancel", top-right |
| Back | arrow icon top-left, BACK button |
| Menu | hamburger icon, three dots |
| Input | EditText, focused field with cursor |

### By Type

| Looking for | Element types |
|-------------|---------------|
| Buttons | Button, ImageButton, clickable=true |
| Text input | EditText, TextInputEditText |
| Lists | RecyclerView, ListView items |

## Output Format

```
Screen: [App - Screen name]
State: [Normal/Loading/Error]

Key Elements:
- [description]: (x, y)

Available Actions:
- [action]: tap (x, y)

Blockers: [None / popup / permission / etc.]
```

## Tips

- Refresh before acting - UI changes
- Check element visibility - may be off-screen
- Account for language differences
- Wait after transitions before analyzing
