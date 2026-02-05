# MobileAgent - AI-Powered Mobile Automation Framework

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sheng1111/MobileAgent)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)

[中文版 README](docs/README_ZH.md)

An open-source automation framework for controlling **Android devices** through **AI Agents** and **MCP** (Model Context Protocol). Build intelligent mobile automation workflows with natural language commands.

## 🌟 Key Features

### Core Capabilities
- **🤖 AI Agent Compatible** - Works with Cursor, Claude Code, Gemini CLI, Codex, Windsurf, Roo Code
- **🔌 MCP Integration** - Supports mobile-mcp, filesystem, fetch, context7 MCP servers
- **📱 Multi-Device Support** - Control multiple Android devices simultaneously
- **🌐 Web UI** - Web-based control panel for device and task management (EN/zh-TW)
- **🎯 Skills System** - Unified skills source with auto-deployment to detected AI Agents
- **🔤 Unicode Input** - Chinese, Japanese, emoji support via ADBKeyboard

### Advanced Automation (New in v2.0)
- **⚡ MCP Macro Server** - High-level tools for faster, more reliable automation
- **🎯 uiautomator2 Integration** - Selector-based operations, no coordinate guessing
- **🔄 Platform Adapters** - Unified interface for Threads, Instagram, X, TikTok, YouTube, Facebook
- **🔍 Element-First Strategy** - Use accessibility tree before screenshots for speed & accuracy
- **✅ Click-Verify Protocol** - Every action is verified for reliability
- **🐛 Debug Artifacts** - Auto-save screenshot + element dump on failure

## 📋 Requirements

- Python 3.8+
- Node.js 18+
- Android SDK Platform Tools (ADB)
- Android device (USB debugging enabled)

### Optional (Recommended)
- [uiautomator2](https://github.com/openatx/uiautomator2) - For selector-based automation

## 🚀 Quick Start

### 1. Run Setup Script

```bash
chmod +x set.sh && ./set.sh
```

This will automatically:
- Check dependencies (Python 3.8+, Node.js 18+, ADB)
- Create Python virtual environment and install dependencies
- Install uiautomator2 (if device connected, also initializes ATX agent)
- Configure MCP settings for AI CLI tools (Gemini, Claude, Codex)
- Validate and deploy skills to detected AI Agents
- Create required directories (`outputs/`, `temp/logs/`)

### 2. Connect Device & Start Using

```bash
adb devices                    # Verify device connection
source .venv/bin/activate      # Activate virtual environment
```

That's it! You're ready to use MobileAgent with your AI Agent.

## 📁 Project Structure

```
MobileAgent/
├── AGENTS.md              # AI Agent behavioral guidelines (MUST READ)
├── GEMINI.md              # Gemini CLI quick reference
├── CLAUDE.md              # Claude Code quick reference
├── set.sh                 # Setup script (includes skills deployment)
│
├── src/                   # Python modules
│   ├── adb_helper.py      # ADB command wrapper
│   ├── executor.py        # Deterministic executor (Element-First enforcement)
│   ├── tool_router.py     # Unified MCP/ADB/u2 interface
│   ├── u2_driver.py       # uiautomator2 selector-based operations
│   ├── mcp_macro_server.py # High-level MCP macro tools
│   ├── platform_adapter.py # Multi-platform unified interface
│   ├── state_tracker.py   # Navigation state machine
│   ├── patrol.py          # Social media patrol automation
│   └── logger.py          # Logging module
│
├── .skills/               # Skills source directory
│   ├── app-explore/       # Main skill: app operations + research mindset
│   ├── app-action/        # Quick single-step operations
│   ├── patrol/            # Social media patrol (search & monitor keywords)
│   ├── content-extract/   # Full content extraction + NLP analysis
│   ├── device-check/      # Device connection verification
│   ├── screen-analyze/    # Screen state analysis
│   ├── troubleshoot/      # Diagnostics and fixes
│   └── unicode-setup/     # Unicode input configuration
│
├── web/                   # Web UI
│   ├── app.py             # Flask backend
│   ├── static/            # CSS/JS
│   └── templates/         # HTML templates
│
├── mcp/                   # MCP configuration
├── apk_tools/             # APK utilities (DeviceKit, ADBKeyboard)
├── tests/                 # Unit tests
├── outputs/               # Screenshots, downloads, patrol reports
└── temp/logs/             # Log files
```

## 🛠️ MCP Macro Server

The new **mobile-macro** MCP server provides high-level automation tools that combine multiple steps into single operations, reducing LLM round-trips and improving reliability.

### Available Tools

| Tool | Description |
|------|-------------|
| `find_and_click` | Element search + click + verify in one call |
| `type_and_submit` | Focus + type + submit in one call |
| `smart_wait` | Wait for element with native u2 wait |
| `scroll_and_find` | Auto-scroll until element found |
| `navigate_back` | Back + verify navigation |
| `dismiss_popup` | Dismiss common dialogs (OK, Cancel, Close, etc.) |
| `launch_and_wait` | Launch app + wait for ready indicator |
| `get_screen_summary` | Screen state overview with visible texts |
| `run_patrol` | Complete social media browsing automation |

### Configuration

Add to your MCP settings:

```json
{
  "mcpServers": {
    "mobile-macro": {
      "command": "python",
      "args": ["-m", "src.mcp_macro_server"],
      "cwd": "<PROJECT_PATH>"
    }
  }
}
```

## 🎯 uiautomator2 Integration

For the most reliable automation, install uiautomator2:

```bash
pip install uiautomator2
python -m uiautomator2 init
```

### Benefits

| Operation | Coordinate-Based | Selector-Based (u2) |
|-----------|-----------------|---------------------|
| Click button | `router.click(x=540, y=1200)` | `router.click(text="Search")` |
| Find element | Screenshot + vision | Direct selector lookup |
| Wait for element | Polling with screenshots | Native wait support |
| Stability | Screen-size dependent | Works across devices |

### Usage in Code

```python
from src.tool_router import ToolRouter

router = ToolRouter()  # Auto-detects u2

# Selector-based click (most reliable)
router.click(text="Search")
router.click_by_selector(resourceId="com.app:id/btn", clickable=True)

# Smart waiting
router.wait_for_element_u2(text="Loading", gone=True, timeout=10)

# Scroll to find
found, el = router.scroll_to_element(text="Settings", max_scrolls=5)
```

## 🎓 Skills System

MobileAgent uses the open [Agent Skills specification](https://agentskills.io) for AI agent capabilities. Skills are stored in `.skills/` and automatically deployed to detected AI Agents.

### Agent Skills Standard

Each skill follows the specification with proper frontmatter:

```yaml
---
name: skill-name
description: What it does and when to use it.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
---
```

### Supported AI Agents

| AI Agent | Skills Directory | MCP Config |
|----------|-----------------|------------|
| Cursor | `.cursor/skills/` | `.cursor/mcp.json` |
| Claude Code | `.claude/skills/` | `.mcp.json` |
| Gemini CLI | `.gemini/skills/` | `.gemini/settings.json` |
| Codex CLI | `.codex/skills/` | `.codex/config.toml` |
| Roo Code | `.roo/skills/` | `.roo/mcp.json` |
| Windsurf | `.windsurf/skills/` | Global only |

### Adding a Skill

1. Create a new directory under `.skills/`
2. Create a `SKILL.md` file with proper frontmatter
3. Run `./set.sh` to validate and deploy

See `.skills/README.md` for the complete Agent Skills specification and examples.

### 🏄 Patrol Skill (海巡)

Like a coast guard hunting for targets, the **patrol** skill enables AI Agents to:
- **Search** for a keyword on social media
- **Monitor** and browse related posts
- **Collect** opinions and sentiment about the topic
- **Report** findings back to user

Example:
```
User: "Search Threads for clawdbot and see what people think"

AI Agent will:
1. Launch Threads app
2. Search "clawdbot"
3. Browse 5+ posts mentioning it
4. Read comments and reactions
5. Report: "Here's what people are saying about clawdbot..."
```

### 📄 Content Extract Skill

Extract **full content** (not summaries) from articles and posts with structured NLP analysis:

- **Full text extraction**: Complete article content without truncation
- **NLP Analysis**: Who (people), What (events), When (time), Where (locations), Objects (things/products)
- **Keywords**: Key terms and topics with confidence scores
- **JSON Output**: Standardized schema for easy API integration
- **Save to file**: JSON (primary) and Markdown (secondary) in `outputs/` directory

Example JSON output structure:
```json
{
  "extraction_meta": {
    "version": "2.0",
    "extracted_at": "2024-01-29T10:30:00+08:00",
    "platform": "WeChat",
    "extraction_status": "success"
  },
  "articles": [{
    "title": "Article Title",
    "content": { "full_text": "...", "word_count": 342 },
    "nlp_analysis": {
      "who": [{ "value": "Person Name", "confidence": 0.95 }],
      "what": [{ "value": "Event description", "confidence": 0.90 }]
    },
    "keywords": ["AI", "technology"],
    "sentiment": "positive"
  }]
}
```

### 📱 App Explore Skill

Main skill for app operations with research mindset:

| Platform | Features |
|----------|----------|
| LINE, WeChat, Telegram, WhatsApp | Send messages, search contacts |
| Facebook, Instagram, Threads, X | Like, comment, share, follow |
| YouTube, TikTok | Like, comment, subscribe |
| Gmail, LinkedIn, Discord, Snapchat | Platform-specific operations |

Features:
- **Element-First Strategy**: Use accessibility tree before screenshots
- **Click-Verify Protocol**: Verify every action succeeded
- Separated UI reference files, load on-demand to save tokens
- Multi-language UI keywords (EN/zh/JP/KR)

## 🖥️ Web UI

Start the web control panel:

```bash
source .venv/bin/activate
pip install flask
python web/app.py
```

Open http://localhost:6443 in your browser.

### Features

- View connected devices
- Select CLI tool (Gemini/Claude/Codex) and model
- Real-time task output streaming
- Task history
- English/Traditional Chinese interface

### Screenshots

| Dashboard | New Task |
|:---------:|:--------:|
| ![Dashboard](docs/images/webui-dashboard.png) | ![New Task](docs/images/webui-new-task.png) |
| View connected devices and task history | Select CLI tool, model, and describe your task |

| Task Running | Task Completed |
|:------------:|:--------------:|
| ![Running](docs/images/webui-with-device.png) | ![Completed](docs/images/webui-task-completed.png) |
| Real-time output with device screen | View results and task summary |

## 💻 Usage Example

### Python API

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()
adb.screenshot(prefix="step1")
adb.tap(540, 1200)
adb.type_text("search query")
adb.press_enter()
```

### Deterministic Executor

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

# Auto-selects best tool (u2 > MCP > ADB)
router.click(text="Search")           # Find by text, then click
router.type_text("Hello 你好")         # Unicode supported
router.swipe("up", verify=True)       # Scroll with verification
router.wait_for_element(text="Results")
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

## ❓ FAQ

### Q: Cannot connect to device?

```bash
adb kill-server && adb start-server
adb devices
```

### Q: Text input fails?

```python
from src.adb_helper import setup_adbkeyboard
setup_adbkeyboard()
```

Or install DeviceKit APK for MCP:
```bash
adb install apk_tools/mobilenext-devicekit.apk
```

### Q: Where are the logs?

`temp/logs/mobile_agent_YYYYMMDD.log`

### Q: How to enable uiautomator2?

```bash
pip install uiautomator2
python -m uiautomator2 init
```

ToolRouter will automatically detect and use it.

## 📜 License

This project is licensed under the [MIT License](LICENSE).

### Dependency Licenses

| Tool/Package | License | Description |
|--------------|---------|-------------|
| MCP (Model Context Protocol) | Open Source (Linux Foundation) | Donated by Anthropic to Agentic AI Foundation |
| mobile-mcp | Apache-2.0 | MCP server for mobile automation |
| context7 | MIT | Documentation query MCP server |
| uiautomator2 | MIT | Android automation library |
| ADB (Android Debug Bridge) | Apache-2.0 | Android SDK Platform Tools |
| ADBKeyboard | GPL-2.0 | Unicode input support |
| Flask | BSD-3-Clause | Web UI framework |

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/sheng1111/MobileAgent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sheng1111/MobileAgent/discussions)

---

<p align="center">
  <strong>Built with ❤️ for the AI Agent community</strong>
</p>
