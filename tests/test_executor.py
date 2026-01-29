#!/usr/bin/env python3
"""
Unit tests for src/executor.py - Deterministic Executor
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add src to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from executor import (
    Element, ScreenState, DeterministicExecutor,
    ActionResult, ExecutionResult
)


# =============================================================================
# Element Tests
# =============================================================================

class TestElement:
    """Tests for Element class"""

    def test_element_creation(self):
        """Test basic element creation"""
        el = Element(
            text="Search",
            element_type="Button",
            identifier="com.app:id/search",
            bounds={"x": 100, "y": 200, "width": 80, "height": 60},
            clickable=True
        )

        assert el.text == "Search"
        assert el.element_type == "Button"
        assert el.identifier == "com.app:id/search"
        assert el.clickable is True

    def test_element_center(self):
        """Test center point calculation"""
        el = Element(
            bounds={"x": 100, "y": 200, "width": 80, "height": 60}
        )

        cx, cy = el.center
        assert cx == 140  # 100 + 80/2
        assert cy == 230  # 200 + 60/2

    def test_element_center_empty_bounds(self):
        """Test center with empty bounds"""
        el = Element()
        assert el.center == (0, 0)

    def test_element_label(self):
        """Test label property"""
        el1 = Element(text="Hello")
        assert el1.label == "Hello"

        el2 = Element(content_desc="Description")
        assert el2.label == "Description"

        el3 = Element(element_type="Button")
        assert el3.label == "Button"

    def test_element_matches_text(self):
        """Test matching by text"""
        el = Element(text="Search Button")

        assert el.matches(text="Search") is True
        assert el.matches(text="search") is True  # Case insensitive
        assert el.matches(text="Button") is True
        assert el.matches(text="xyz") is False

    def test_element_matches_exact_text(self):
        """Test matching by exact text"""
        el = Element(text="Search")

        assert el.matches(text_exact="Search") is True
        assert el.matches(text_exact="search") is False
        assert el.matches(text_exact="Search Button") is False

    def test_element_matches_type(self):
        """Test matching by type"""
        el = Element(element_type="EditText")

        assert el.matches(type="EditText") is True
        assert el.matches(type="edit") is True
        assert el.matches(type="Button") is False

    def test_element_matches_identifier(self):
        """Test matching by identifier"""
        el = Element(identifier="com.app:id/search_button")

        assert el.matches(identifier="search") is True
        assert el.matches(identifier="button") is True
        assert el.matches(identifier="xyz") is False

    def test_element_matches_clickable(self):
        """Test matching by clickable"""
        el1 = Element(clickable=True)
        el2 = Element(clickable=False)

        assert el1.matches(clickable=True) is True
        assert el1.matches(clickable=False) is False
        assert el2.matches(clickable=False) is True

    def test_element_matches_multiple_criteria(self):
        """Test matching with multiple criteria"""
        el = Element(
            text="Search",
            element_type="Button",
            clickable=True
        )

        assert el.matches(text="Search", type="Button") is True
        assert el.matches(text="Search", type="EditText") is False
        assert el.matches(text="Search", clickable=True) is True


# =============================================================================
# ScreenState Tests
# =============================================================================

class TestScreenState:
    """Tests for ScreenState class"""

    def test_from_elements_mcp_format(self, mock_elements):
        """Test creating ScreenState from MCP element format"""
        state = ScreenState.from_elements(mock_elements)

        assert len(state.elements) == len(mock_elements)
        assert state.timestamp > 0
        assert len(state.screen_hash) > 0

    def test_from_elements_empty(self):
        """Test creating ScreenState from empty list"""
        state = ScreenState.from_elements([])

        assert len(state.elements) == 0
        assert state.screen_hash is not None

    def test_screen_hash_changes(self, mock_elements):
        """Test that screen hash changes with different elements"""
        state1 = ScreenState.from_elements(mock_elements)

        # Modify elements
        modified = mock_elements.copy()
        modified[0]["text"] = "Different Text"
        state2 = ScreenState.from_elements(modified)

        assert state1.screen_hash != state2.screen_hash

    def test_find_element(self, mock_elements):
        """Test finding element in state"""
        state = ScreenState.from_elements(mock_elements)

        # Find by text
        el = state.find(text="Search")
        assert el is not None
        assert "Search" in el.text

        # Find by type
        el = state.find(type="Button")
        assert el is not None

        # Find non-existent
        el = state.find(text="NonExistent")
        assert el is None

    def test_find_all_elements(self, mock_elements):
        """Test finding all matching elements"""
        state = ScreenState.from_elements(mock_elements)

        # Find all clickable
        clickables = state.find_all(clickable=True)
        assert len(clickables) > 0

        # Find all with specific type
        buttons = state.find_all(type="Button")
        assert len(buttons) >= 1

    def test_has_text(self, mock_elements):
        """Test checking for text presence"""
        state = ScreenState.from_elements(mock_elements)

        assert state.has_text("Search") is True
        assert state.has_text("search") is True  # Case insensitive
        assert state.has_text("NonExistent") is False

    def test_parse_bounds_mcp_format(self):
        """Test parsing bounds from MCP format"""
        el = {"x": 100, "y": 200, "width": 80, "height": 60}
        bounds = ScreenState._parse_bounds(el)

        assert bounds["x"] == 100
        assert bounds["y"] == 200
        assert bounds["width"] == 80
        assert bounds["height"] == 60

    def test_parse_bounds_string_format(self):
        """Test parsing bounds from string format [x1,y1][x2,y2]"""
        bounds = ScreenState._parse_bounds_string("[100,200][180,260]")

        assert bounds["x"] == 100
        assert bounds["y"] == 200
        assert bounds["width"] == 80
        assert bounds["height"] == 60


# =============================================================================
# DeterministicExecutor Tests
# =============================================================================

class TestDeterministicExecutor:
    """Tests for DeterministicExecutor class"""

    @pytest.fixture
    def executor(self, mock_adb):
        """Create executor with mocked ADB"""
        with patch('src.executor.ADBHelper', return_value=mock_adb):
            exec = DeterministicExecutor(device_id="test-device")
            return exec

    def test_init(self, executor):
        """Test executor initialization"""
        assert executor.device_id == "test-device"
        assert executor.max_retries == 3
        assert executor.last_state is None

    def test_set_mcp_callback(self, executor, mock_mcp_callback):
        """Test setting MCP callback"""
        executor.set_mcp_callback(mock_mcp_callback)
        assert executor._mcp_callback is not None

    def test_observe_via_mcp(self, executor, mock_mcp_callback, mock_elements):
        """Test observation via MCP callback"""
        executor.set_mcp_callback(mock_mcp_callback)
        state = executor.observe()

        assert state is not None
        assert len(state.elements) == len(mock_elements)
        assert executor.last_state == state

    def test_find_element(self, executor, mock_mcp_callback):
        """Test finding element after observation"""
        executor.set_mcp_callback(mock_mcp_callback)
        executor.observe()

        el = executor.find_element(text="Search")
        assert el is not None

        el = executor.find_element(type="Button")
        assert el is not None

    def test_find_element_no_state(self, executor):
        """Test finding element without observation"""
        el = executor.find_element(text="Search")
        assert el is None  # Should return None without state

    def test_find_by_text(self, executor, mock_mcp_callback):
        """Test find_by_text convenience method"""
        executor.set_mcp_callback(mock_mcp_callback)
        executor.observe()

        el = executor.find_by_text("Search")
        assert el is not None

    def test_find_by_type(self, executor, mock_mcp_callback):
        """Test find_by_type convenience method"""
        executor.set_mcp_callback(mock_mcp_callback)
        executor.observe()

        el = executor.find_by_type("Button")
        assert el is not None

    def test_state_history(self, executor, mock_mcp_callback):
        """Test state history tracking"""
        executor.set_mcp_callback(mock_mcp_callback)

        # Observe multiple times
        executor.observe()
        executor.observe()
        executor.observe()

        assert len(executor.state_history) == 3

    def test_state_history_limit(self, executor, mock_mcp_callback):
        """Test state history is limited"""
        executor.set_mcp_callback(mock_mcp_callback)

        # Observe many times
        for _ in range(25):
            executor.observe()

        assert len(executor.state_history) <= 20

    def test_clear_history(self, executor, mock_mcp_callback):
        """Test clearing history"""
        executor.set_mcp_callback(mock_mcp_callback)
        executor.observe()
        executor.observe()

        executor.clear_history()

        assert len(executor.state_history) == 0
        assert executor.last_state is None

    def test_get_screen_text(self, executor, mock_mcp_callback):
        """Test getting all screen text"""
        executor.set_mcp_callback(mock_mcp_callback)
        executor.observe()

        texts = executor.get_screen_text()
        assert isinstance(texts, list)
        assert "Search" in texts

    def test_has_text(self, executor, mock_mcp_callback):
        """Test checking for text"""
        executor.set_mcp_callback(mock_mcp_callback)
        executor.observe()

        assert executor.has_text("Search") is True
        assert executor.has_text("NonExistent") is False


# =============================================================================
# ActionResult Tests
# =============================================================================

class TestActionResult:
    """Tests for ActionResult enum"""

    def test_result_values(self):
        """Test ActionResult enum values"""
        assert ActionResult.SUCCESS.value == "success"
        assert ActionResult.NO_CHANGE.value == "no_change"
        assert ActionResult.TIMEOUT.value == "timeout"
        assert ActionResult.ERROR.value == "error"


class TestExecutionResult:
    """Tests for ExecutionResult dataclass"""

    def test_execution_result_creation(self):
        """Test ExecutionResult creation"""
        result = ExecutionResult(
            result=ActionResult.SUCCESS,
            message="Click verified",
            duration=0.5
        )

        assert result.result == ActionResult.SUCCESS
        assert result.message == "Click verified"
        assert result.duration == 0.5

    def test_execution_result_with_states(self, mock_elements):
        """Test ExecutionResult with states"""
        before = ScreenState.from_elements(mock_elements)
        after = ScreenState.from_elements(mock_elements)

        result = ExecutionResult(
            result=ActionResult.SUCCESS,
            before_state=before,
            after_state=after
        )

        assert result.before_state is not None
        assert result.after_state is not None


# =============================================================================
# Integration Tests
# =============================================================================

class TestExecutorIntegration:
    """Integration tests for executor workflow"""

    def test_observe_find_workflow(self, mock_elements):
        """Test observe → find workflow"""
        callback = lambda: mock_elements

        with patch('src.executor.ADBHelper') as mock_adb_class:
            mock_adb = Mock()
            mock_adb.device_id = "test"
            mock_adb_class.return_value = mock_adb

            executor = DeterministicExecutor()
            executor.set_mcp_callback(callback)

            # Observe
            state = executor.observe()
            assert state is not None

            # Find
            search = executor.find_element(text="Search")
            assert search is not None

            # Get center
            cx, cy = search.center
            assert cx > 0
            assert cy > 0
