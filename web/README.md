# MobileAgent Web UI

Web interface for managing Android devices and executing AI agent tasks.

## Quick Start

```bash
# From project root
source .venv/bin/activate
pip install flask
python web/app.py
```

Then open http://localhost:6443 in your browser.

## Features

- **Device List**: View all connected Android devices with status
- **Task Management**: Create, monitor, and cancel agent tasks
- **CLI Tool Selection**: Gemini CLI, Claude Code, OpenAI Codex
- **Model Selection**: Choose from latest AI models
- **Real-time Output**: Stream task output in real-time
- **Task History**: View completed/failed tasks
- **Multi-language**: Traditional Chinese and English support

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/devices` | List connected devices |
| GET | `/api/cli-options` | Get available CLI tools and models |
| GET | `/api/tasks` | List all tasks |
| POST | `/api/tasks` | Create new task |
| GET | `/api/tasks/<id>` | Get task details |
| DELETE | `/api/tasks/<id>` | Cancel task |
| GET | `/api/tasks/<id>/output` | Get task output |

## Create Task Request

```json
{
    "device_serial": "DEVICE_SERIAL",
    "prompt": "Open Chrome and search for news",
    "cli_tool": "gemini",
    "model": "gemini-2.5-flash"
}
```

## Project Structure

```
web/
├── app.py              # Flask backend
├── requirements.txt    # Dependencies
├── README.md           # This file
├── static/
│   ├── css/style.css   # Styles
│   └── js/main.js      # Frontend logic (i18n included)
└── templates/
    └── index.html      # Main page
```

## Development

Run tests:
```bash
python -m pytest tests/test_web_api.py -v
```
