# GEMINI.md

Project documentation for Gemini CLI and Gemini-based tools.

## Project Overview

MobileAgent: AI agents control Android devices via MCP and Python scripts. Agents observe screen state, make decisions, and execute actions to accomplish user tasks.

**Tech Stack:** Python 3.8+ | Node.js 18+ | ADB | Android device (USB debugging)

## Commands

```bash
# Unicode input (install both for full support)
adb install apk_tools/mobilenext-devicekit.apk  # Required for MCP Unicode
adb install apk_tools/ADBKeyBoard.apk           # Required for Python Unicode

# ADB troubleshooting
adb devices
adb kill-server && adb start-server
```

## Architecture

```
src/adb_helper.py    # ADB wrapper (tap, swipe, type_text, screenshot)
src/logger.py        # Logging -> temp/logs/mobile_agent_YYYYMMDD.log
apk_tools/           # DeviceKit (MCP), ADBKeyboard (Python) APKs
outputs/             # User-requested outputs only
mcp/                 # MCP server configs
web/                 # Web UI for device management
.skills/             # Agent skills for specific tasks
```

## Tool Selection

Prefer MCP tools for device interaction. Use Python (`src/adb_helper.py`) as fallback.

### Element-First Strategy (CRITICAL)

**ALWAYS use accessibility tree before screenshots. This is the #1 rule for speed and accuracy.**

```
CORRECT FLOW (fast, reliable):
1. mobile_list_elements_on_screen
2. Find target by text/type/identifier
3. Calculate center: (x + width/2, y + height/2)
4. mobile_click_on_screen_at_coordinates

WRONG FLOW (slow, error-prone):
1. mobile_take_screenshot
2. Visually guess coordinates
3. mobile_click_on_screen_at_coordinates
4. Misclick → repeat from step 1
```

### Why Element-First

| Aspect | Element List | Screenshot |
|--------|--------------|------------|
| Speed | ~100ms | 2-5s (+ vision analysis) |
| Accuracy | Pixel-perfect bounds | Guessing, often misses |
| Reliability | Stable identifiers | Position varies |

### Tool Priority

| Priority | Task | Tool |
|----------|------|------|
| 1 | Get UI elements/coordinates | `mobile_list_elements_on_screen` (MCP) |
| 2 | Click/tap elements | `mobile_click_on_screen_at_coordinates` (MCP) |
| 3 | Visual verification | `mobile_take_screenshot` (MCP) - LAST resort |
| 4 | Unicode text input | MCP: `mobile_type_keys` + DeviceKit |
| 5 | Unicode text (fallback) | Python: `adb.type_text()` + ADBKeyboard |
| 6 | File transfer, device info | Python only |

### When to Use Screenshot

- Element not in accessibility tree (custom UI, games, canvas)
- Visual verification after action
- Debugging when element tree doesn't match display

### Wait Before Acting

Many errors are timing issues, not coordinate issues:

| After... | Wait |
|----------|------|
| App launch | 2-3s for splash to complete |
| Navigation | 1-2s for screen transition |
| Typing | 1s for suggestions to appear |
| Scroll | 1s for content to load |

## MCP Tool Notes

```
mobile_list_available_devices requires: { "noParams": {} }
```

## Python API

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()
adb.tap(540, 1200)
adb.type_text("query")     # Unicode via ADBKeyboard
adb.screenshot(prefix="step1")

# All methods return (success, message) tuple
ok, msg = adb.tap(540, 1200)
```

## Code Style

- No type annotations
- English comments
- camelCase naming
- Return `(success, message)` tuples

## Output Rules

- Code/comments: English
- User-facing: Match user's language
- Files: Only when explicitly requested → `outputs/YYYY-MM-DD/`

## Agent Behavior

**For device operation tasks, follow AGENTS.md** - contains:
- Research mindset and minimum actions
- Cognitive loop (Observe → Decide → Act → Verify → Adapt)
- Decision principles and obstacle handling
- Content extraction and output format

## See Also

- `AGENTS.md` - Agent behavioral guidelines (MUST READ for device tasks)
- `.skills/` - Task-specific skills
- `README.md` - Full project documentation
