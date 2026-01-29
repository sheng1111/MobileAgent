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
src/
├── adb_helper.py    # ADB wrapper (tap, swipe, type_text, screenshot)
├── logger.py        # Logging -> temp/logs/mobile_agent_YYYYMMDD.log
├── executor.py      # Deterministic Executor (Element-First enforcement)
├── tool_router.py   # Unified MCP/ADB tool interface
├── state_tracker.py # Navigation state machine, visited tracking
└── patrol.py        # Social media patrol automation

apk_tools/           # DeviceKit (MCP), ADBKeyboard (Python) APKs
outputs/             # User-requested outputs only
mcp/                 # MCP server configs
web/                 # Web UI for device management
.skills/             # Agent skills for specific tasks
tests/               # Unit tests
```

## Tool Selection

Prefer MCP tools for device interaction. Use Python (`src/adb_helper.py`) as fallback.

### Element-First Strategy (CRITICAL)

**ALWAYS use accessibility tree before screenshots:**

```
CORRECT: list_elements → find by text/id → click center
WRONG:   screenshot → guess coordinates → click
```

### Tool Priority

| Priority | Task | Tool |
|----------|------|------|
| 1 | Get UI elements/coordinates | `mobile_list_elements_on_screen` (MCP) |
| 2 | Click/tap elements | `mobile_click_on_screen_at_coordinates` (MCP) |
| 3 | Visual verification | `mobile_take_screenshot` (MCP) - LAST resort |
| 4 | Unicode text input | MCP: `mobile_type_keys` + DeviceKit |
| 5 | Unicode text (fallback) | Python: `adb.type_text()` + ADBKeyboard |
| 6 | File transfer, device info | Python only |

### Why Element-First

- **Speed**: Element list ~100ms vs screenshot+vision 2-5s
- **Accuracy**: Element bounds are pixel-perfect
- **Reliability**: resourceId/identifier stable across runs

## MCP Tool Notes

```
mobile_list_available_devices requires: { "noParams": {} }
```

## Python API

### Basic ADB Operations

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()
adb.tap(540, 1200)
adb.type_text("query")     # Unicode via ADBKeyboard
adb.screenshot(prefix="step1")

# All methods return (success, message) tuple
ok, msg = adb.tap(540, 1200)
```

### Deterministic Executor (Click-Verify Enforcement)

```python
from src.executor import DeterministicExecutor

executor = DeterministicExecutor()

# Observe → Find → Click → Verify
state = executor.observe()
element = executor.find_element(text="Search")
if element:
    result = executor.click_and_verify(element)
    if result.result == ActionResult.SUCCESS:
        print("Click verified!")
```

### Tool Router (Unified Interface)

```python
from src.tool_router import ToolRouter

router = ToolRouter()

# Auto-selects best tool (MCP or ADB)
router.click(text="Search")           # Find by text, then click
router.type_text("Hello 你好")         # Unicode supported
router.swipe("up", verify=True)       # Scroll with verification
router.wait_for_element(text="Results")
```

### State Tracker (Visited Tracking)

```python
from src.state_tracker import StateTracker

tracker = StateTracker(platform="threads")
tracker.mark_visited(title="Post 1", author="@user")
if not tracker.is_visited(title="Post 2", author="@user"):
    # Visit this post
    pass
tracker.save()  # Persist to disk
```

### Patrol Automation

```python
from src.patrol import PatrolStateMachine, PatrolConfig

config = PatrolConfig(max_posts=10, max_scrolls=5)
patrol = PatrolStateMachine(platform="threads", config=config)
report = patrol.run(keyword="AI agents")

print(f"Visited {len(report.posts)} posts")
print(report.summary)
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
