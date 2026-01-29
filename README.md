# MobileAgent - AI-Powered Mobile Automation Framework

[中文版 README](docs/README_ZH.md)

An automation framework for controlling Android devices through AI Agents and MCP (Model Context Protocol).

## Features

- Web UI - Web-based control panel for device and task management (EN/zh-TW)
- MCP Integration - Supports mobile-mcp, filesystem, fetch, context7 MCP servers
- AI Agent Compatible - Works with Cursor, Claude Code, Gemini CLI, Codex, Windsurf, Roo Code
- Skills System - Unified skills source with auto-deployment to detected AI Agents
- Multi-model Support - Gemini, Claude, GPT and more
- ADB Helper Scripts - Fallback when MCP tools are restricted
- Unicode Input - Chinese and emoji support via ADBKeyboard

## Requirements

- Python 3.8+
- Node.js 18+
- Android SDK Platform Tools (ADB)
- Android device (USB debugging enabled)

## Quick Start

### 1. Run Setup Script

```bash
chmod +x set.sh && ./set.sh
```

This will automatically:
- Create Python virtual environment and install dependencies
- Configure MCP settings for AI CLI tools
- Validate and deploy skills to detected AI Agents

### 2. Verify Environment

```bash
python tests/test_environment.py
```

### 3. Configure AI Agent

Copy `mcp/mcp_setting.json` to your AI Agent settings.

### 4. Connect Device

```bash
adb devices
```

## Project Structure

```
MobileAgent/
├── AGENTS.md           # AI Agent guidelines (MUST READ)
├── CLAUDE.md           # Claude Code reference
├── GEMINI.md           # Gemini CLI reference
├── set.sh              # Setup script (includes skills deployment)
├── .skills/            # Skills source directory
│   ├── app-explore/    # Main skill: app operations + research mindset
│   ├── app-action/     # Quick single-step operations
│   ├── patrol/         # Social media patrol (search & monitor keywords)
│   ├── content-extract/# Full content extraction + NLP analysis
│   ├── device-check/   # Device connection verification
│   ├── screen-analyze/ # Screen state analysis
│   ├── troubleshoot/   # Diagnostics and fixes
│   └── unicode-setup/  # Unicode input configuration
├── src/                # Python modules
│   ├── adb_helper.py   # ADB command wrapper
│   ├── logger.py       # Logging module
│   ├── executor.py     # Deterministic executor (Element-First enforcement)
│   ├── tool_router.py  # Unified MCP/ADB interface
│   ├── state_tracker.py # Navigation state machine
│   └── patrol.py       # Patrol automation (programmatic use)
├── web/                # Web UI
│   ├── app.py          # Flask backend
│   ├── static/         # CSS/JS
│   └── templates/      # HTML
├── tests/              # Unit tests
├── mcp/                # MCP configuration
├── apk_tools/          # APK utilities
├── outputs/            # Screenshots, downloads, summaries
└── temp/logs/          # Log files
```

## Skills System

MobileAgent uses a unified skills source directory (`.skills/`). Running `set.sh` automatically detects installed AI Agents and deploys skills to their respective directories.

### Supported AI Agents

| AI Agent | Detection Method | Deploy Path |
|----------|-----------------|-------------|
| Cursor | `~/.cursor/` exists | `.cursor/skills/` |
| Claude Code | `claude` command or `~/.claude/` | `.claude/skills/` |
| Gemini CLI | `gemini` command or `~/.gemini/` | `.gemini/skills/` |
| Codex CLI | `codex` command or `~/.codex/` | `.codex/skills/` |
| Windsurf | `~/.codeium/` exists | `.windsurf/skills/` |
| Roo Code | `~/.roo/` exists | `.roo/skills/` |

### Adding a Skill

1. Create a new directory under `.skills/`
2. Create a `SKILL.md` file (with frontmatter)
3. Run `./set.sh` to validate and deploy

See `.skills/README.md` for details.

### Patrol Skill (海巡)

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

The AI Agent executes this autonomously using MCP tools, tracking visited posts internally.

### Content Extract Skill

Extract **full content** (not summaries) from articles and posts with structured NLP analysis:

- **Full text extraction**: Complete article content without truncation
- **NLP Analysis**: Who (people), What (events), When (time), Where (locations), Objects (things/products)
- **Keywords**: Key terms and topics
- **Save to file**: JSON and/or Markdown format in `outputs/` directory

Example:
```
User: "Read WeChat account 36氪's latest article, extract full content and analyze"

AI Agent will:
1. Navigate to WeChat Official Account
2. Find and open the article
3. Scroll and extract complete content
4. Perform NLP analysis (who/what/when/where/objects)
5. Save structured output to outputs/2024-01-29/wechat_36kr_article.json
```

### App Explore Skill

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

## Web UI

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

## Usage Example

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()
adb.screenshot(prefix="step1")
adb.tap(540, 1200)
adb.type_text("search query")
adb.press_enter()
```

## FAQ

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

### Q: Where are the logs?

`temp/logs/mobile_agent_YYYYMMDD.log`

## License

This project is licensed under the [MIT License](LICENSE).

### Dependency Licenses

| Tool/Package | License | Description |
|--------------|---------|-------------|
| MCP (Model Context Protocol) | Open Source (Linux Foundation) | Donated by Anthropic to Agentic AI Foundation |
| mobile-mcp | Apache-2.0 | MCP server for mobile automation |
| context7 | MIT | Documentation query MCP server |
| ADB (Android Debug Bridge) | Apache-2.0 | Android SDK Platform Tools |
| ADBKeyboard | GPL-2.0 | Unicode input support |
| Flask | BSD-3-Clause | Web UI framework |
