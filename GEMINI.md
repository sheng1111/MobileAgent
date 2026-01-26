# GEMINI.md

This file provides guidance to Gemini Code (gemini.ai/code) when working with code in this repository.

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
```

## Web UI

Features:
- View connected devices
- Create and monitor agent tasks
- Real-time task output streaming
- Task history

**Agent behavior is defined in AGENTS.md** - read it for cognitive loop, decision principles, and adaptive strategies.

## Tool Selection

Prefer MCP tools for device interaction. Use Python (`src/adb_helper.py`) as fallback or for features MCP lacks.

| Task | Tool |
|------|------|
| Get UI elements/coordinates | `mobile_list_elements_on_screen` (MCP) |
| Visual screen state | `mobile_take_screenshot` (MCP) |
| Unicode text input | MCP: `mobile_type_keys` + DeviceKit |
| Unicode text (fallback) | Python: `adb.type_text()` + ADBKeyboard |
| File transfer, device info, list packages | Python only |

## Python API

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()
adb.tap(540, 1200)
adb.type_text("query")     # Unicode via ADBKeyboard
adb.screenshot(prefix="step1")

# All methods return (success, message) tuple
ok, msg = adb.tap(540, 1200)
if not ok:
    # Handle failure
```

## Code Style

- No type annotations
- English comments
- camelCase naming
- Return `(success, message)` tuples

## Output Rules

- Code/comments: English
- User-facing: Match user's language
- Files: Only save when user explicitly requests ("save", "download", "record")
- Format: `outputs/YYYY-MM-DD/{task}_{HHMMSS}_step{N}.png`

## See Also

- `AGENTS.md` - Agent behavior guidelines, cognitive loop, decision principles
- `README.md` - Full project documentation
- `web/README.md` - Web UI documentation and API reference
