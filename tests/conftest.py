#!/usr/bin/env python3
"""
Pytest configuration and fixtures for MobileAgent tests.
"""
import os
import sys
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict

# Add src to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))


# =============================================================================
# Mock Data
# =============================================================================

MOCK_SCREEN_ELEMENTS = [
    {
        "text": "Search",
        "type": "ImageButton",
        "identifier": "com.app:id/search_button",
        "x": 900, "y": 80, "width": 100, "height": 80,
        "clickable": True
    },
    {
        "text": "Home",
        "type": "Button",
        "identifier": "com.app:id/tab_home",
        "x": 50, "y": 2200, "width": 200, "height": 100,
        "clickable": True
    },
    {
        "text": "First Post Title",
        "type": "TextView",
        "identifier": "com.app:id/post_title",
        "x": 50, "y": 300, "width": 900, "height": 150,
        "clickable": True
    },
    {
        "text": "@user1",
        "type": "TextView",
        "identifier": "com.app:id/post_author",
        "x": 50, "y": 250, "width": 200, "height": 50,
        "clickable": False
    },
    {
        "text": "Second Post Title",
        "type": "TextView",
        "identifier": "com.app:id/post_title",
        "x": 50, "y": 550, "width": 900, "height": 150,
        "clickable": True
    },
    {
        "text": "Like",
        "type": "Button",
        "identifier": "com.app:id/like_button",
        "x": 100, "y": 700, "width": 100, "height": 80,
        "clickable": True
    },
    {
        "text": "Comment",
        "type": "Button",
        "identifier": "com.app:id/comment_button",
        "x": 300, "y": 700, "width": 100, "height": 80,
        "clickable": True
    },
]

MOCK_POST_DETAIL_ELEMENTS = [
    {
        "text": "Post Title Here",
        "type": "TextView",
        "identifier": "com.app:id/detail_title",
        "x": 50, "y": 200, "width": 900, "height": 100,
        "clickable": False
    },
    {
        "text": "@author_name",
        "type": "TextView",
        "identifier": "com.app:id/detail_author",
        "x": 50, "y": 150, "width": 200, "height": 50,
        "clickable": True
    },
    {
        "text": "This is the post content. It contains some interesting information.",
        "type": "TextView",
        "identifier": "com.app:id/detail_content",
        "x": 50, "y": 320, "width": 900, "height": 300,
        "clickable": False
    },
    {
        "text": "Like",
        "type": "Button",
        "identifier": "com.app:id/like_button",
        "x": 100, "y": 700, "width": 100, "height": 80,
        "clickable": True
    },
    {
        "text": "Comment",
        "type": "Button",
        "identifier": "com.app:id/comment_button",
        "x": 300, "y": 700, "width": 100, "height": 80,
        "clickable": True
    },
    {
        "text": "Share",
        "type": "Button",
        "identifier": "com.app:id/share_button",
        "x": 500, "y": 700, "width": 100, "height": 80,
        "clickable": True
    },
    {
        "text": "15 likes",
        "type": "TextView",
        "identifier": "com.app:id/like_count",
        "x": 100, "y": 780, "width": 100, "height": 40,
        "clickable": False
    },
]


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_elements():
    """Return mock screen elements (deep copy to avoid mutation)"""
    import copy
    return copy.deepcopy(MOCK_SCREEN_ELEMENTS)


@pytest.fixture
def mock_post_detail_elements():
    """Return mock post detail elements"""
    return MOCK_POST_DETAIL_ELEMENTS.copy()


@pytest.fixture
def mock_adb():
    """Create mock ADB helper"""
    mock = Mock()
    mock.device_id = "emulator-5554"
    mock.tap.return_value = (True, "Tap successful")
    mock.swipe.return_value = (True, "Swipe successful")
    mock.type_text.return_value = (True, "Text input successful")
    mock.press_back.return_value = (True, "Back pressed")
    mock.press_home.return_value = (True, "Home pressed")
    mock.launch_app.return_value = (True, "App launched")
    mock.get_screen_size.return_value = (1080, 2400)
    mock.screenshot.return_value = "/tmp/screenshot.png"
    return mock


@pytest.fixture
def mock_mcp_callback(mock_elements):
    """Create mock MCP callback that returns elements"""
    def callback():
        return mock_elements
    return callback


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create temporary data directory"""
    data_dir = tmp_path / "state_data"
    data_dir.mkdir()
    return data_dir


# =============================================================================
# Mock ADB Functions
# =============================================================================

@pytest.fixture(autouse=True)
def mock_adb_functions():
    """Mock ADB functions for all tests"""
    with patch('src.executor.run_adb') as mock_run, \
         patch('src.executor.tap') as mock_tap, \
         patch('src.executor.swipe') as mock_swipe, \
         patch('src.executor.press_back') as mock_back:

        mock_run.return_value = (True, "OK")
        mock_tap.return_value = (True, "Tap successful")
        mock_swipe.return_value = (True, "Swipe successful")
        mock_back.return_value = (True, "Back pressed")

        yield {
            'run_adb': mock_run,
            'tap': mock_tap,
            'swipe': mock_swipe,
            'press_back': mock_back
        }
