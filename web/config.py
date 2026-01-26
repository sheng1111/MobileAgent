"""
MobileAgent Web UI - Configuration
Edit this file to customize settings.
"""

import os

# =============================================================================
# Paths
# =============================================================================

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database file path
DATABASE_PATH = os.path.join(PROJECT_ROOT, "web", "tasks.db")

# =============================================================================
# Server Settings
# =============================================================================

# Flask server host and port
HOST = "0.0.0.0"
PORT = 6443
DEBUG = True

# =============================================================================
# UI Settings
# =============================================================================

# Auto-refresh interval in seconds (default: 60 = 1 minute)
# Set to 0 to disable auto-refresh
AUTO_REFRESH_INTERVAL = 60

# Default language: "zh-TW" or "en"
DEFAULT_LANGUAGE = "zh-TW"

# =============================================================================
# Task Settings
# =============================================================================

# Maximum number of tasks to keep in history
MAX_TASK_HISTORY = 100

# Task output max length (characters) to store in database
MAX_OUTPUT_LENGTH = 100000
