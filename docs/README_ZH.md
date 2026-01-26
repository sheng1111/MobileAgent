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
├── AGENTS.md           # AI Agent guidelines
├── CLAUDE.md           # Claude Code reference
├── GEMINI.md           # Gemini CLI reference
├── set.sh              # Setup script (includes skills deployment)
├── .skills/            # Skills source directory
│   ├── app-action/     # App operation skill
│   ├── device-check/   # Device check skill
│   ├── screen-analyze/ # Screen analysis skill
│   ├── social-media/   # Social media skill (LINE/FB/IG/X/...)
│   ├── troubleshoot/   # Troubleshooting skill
│   └── unicode-setup/  # Unicode setup skill
├── src/                # Python scripts
│   ├── adb_helper.py   # ADB command wrapper
│   └── logger.py       # Logging module
├── web/                # Web UI
│   ├── app.py          # Flask backend
│   ├── static/         # CSS/JS
│   └── templates/      # HTML
├── tests/              # Test scripts
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

### Social Media Skill

Built-in customized skill for social media platform operations:

| Platform | Features |
|----------|----------|
| LINE, WeChat, Telegram, WhatsApp | Send messages, search contacts |
| Facebook, Instagram, Threads, X | Like, comment, share, follow |
| YouTube, TikTok | Like, comment, subscribe |
| Gmail, LinkedIn, Discord, Snapchat | Platform-specific operations |

Features:
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
