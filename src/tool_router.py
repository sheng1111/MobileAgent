#!/usr/bin/env python3
"""
Tool Router - Unified interface for MCP and ADB tools.

This module provides intelligent tool selection:
1. MCP tools (fast, reliable) - preferred when available
2. Python ADB (full control) - fallback for unsupported operations

Usage:
    from src.tool_router import ToolRouter

    router = ToolRouter()

    # Click with automatic tool selection
    router.click(text="Search")  # Finds element by text, then clicks
    router.click(x=540, y=1200)  # Direct coordinate click

    # Type with Unicode support
    router.type_text("Hello 你好")

    # Swipe/scroll
    router.swipe("up")
"""
import os
import sys
import time
from typing import Optional, Dict, List, Tuple, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from logger import get_logger
from adb_helper import (
    ADBHelper, run_adb, tap, swipe, type_text as adb_type_text,
    press_key, press_back, press_home, press_enter, launch_app, stop_app,
    get_screen_size, screenshot
)
from executor import DeterministicExecutor, ScreenState, Element, ExecutionResult, ActionResult

logger = get_logger(__name__)


class ToolType(Enum):
    """Tool provider type"""
    MCP = "mcp"
    ADB = "adb"
    AUTO = "auto"


@dataclass
class ClickTarget:
    """Represents a click target"""
    x: int
    y: int
    source: str = "unknown"  # "element", "coordinate", "search"
    element: Optional[Element] = None


class ToolRouter:
    """
    Unified interface for MCP and ADB tools with intelligent routing.

    Priority:
    1. Element-based operations (most reliable)
    2. MCP tools (fast)
    3. ADB fallback (full control)
    """

    def __init__(self, device_id: str = None, prefer_mcp: bool = True):
        """
        Initialize router.

        Args:
            device_id: Device serial (auto-detect if None)
            prefer_mcp: Whether to prefer MCP tools when available
        """
        self.device_id = device_id
        self.prefer_mcp = prefer_mcp
        self.adb = ADBHelper(device_id)
        self.executor = DeterministicExecutor(device_id)

        # MCP callbacks (set by AI agent or external caller)
        self._mcp_list_elements: Optional[Callable] = None
        self._mcp_click: Optional[Callable[[int, int], bool]] = None
        self._mcp_type: Optional[Callable[[str, bool], bool]] = None
        self._mcp_swipe: Optional[Callable[[str, int, int, int], bool]] = None
        self._mcp_launch: Optional[Callable[[str], bool]] = None
        self._mcp_press: Optional[Callable[[str], bool]] = None
        self._mcp_screenshot: Optional[Callable[[], Any]] = None

        # Get device info
        if self.adb.device_id:
            self.screen_size = self.adb.get_screen_size()
            logger.info(f"ToolRouter initialized: device={self.adb.device_id}, screen={self.screen_size}")
        else:
            self.screen_size = (1080, 2400)  # Default
            logger.warning("No device connected, using default screen size")

    # =========================================================================
    # MCP Callback Registration
    # =========================================================================

    def set_mcp_callbacks(self,
                          list_elements: Callable = None,
                          click: Callable = None,
                          type_keys: Callable = None,
                          swipe: Callable = None,
                          launch_app: Callable = None,
                          press_button: Callable = None,
                          take_screenshot: Callable = None):
        """
        Register MCP tool callbacks.

        This allows the router to use MCP tools when available.
        AI agents should call this to integrate their tool access.
        """
        if list_elements:
            self._mcp_list_elements = list_elements
            self.executor.set_mcp_callback(list_elements)
        if click:
            self._mcp_click = click
        if type_keys:
            self._mcp_type = type_keys
        if swipe:
            self._mcp_swipe = swipe
        if launch_app:
            self._mcp_launch = launch_app
        if press_button:
            self._mcp_press = press_button
        if take_screenshot:
            self._mcp_screenshot = take_screenshot

        logger.info("MCP callbacks registered")

    # =========================================================================
    # Element Discovery
    # =========================================================================

    def list_elements(self) -> List[Element]:
        """
        Get all elements on screen.

        Returns list of Element objects with bounds and properties.
        """
        state = self.executor.observe()
        return state.elements

    def find_element(self, text: str = None, element_type: str = None,
                     identifier: str = None, **kwargs) -> Optional[Element]:
        """
        Find element by criteria.

        Args:
            text: Text content to match
            element_type: Element type (Button, EditText, etc.)
            identifier: Resource ID
            **kwargs: Additional criteria

        Returns:
            Element if found, None otherwise
        """
        criteria = {}
        if text:
            criteria['text'] = text
        if element_type:
            criteria['type'] = element_type
        if identifier:
            criteria['identifier'] = identifier
        criteria.update(kwargs)

        state = self.executor.observe()
        return state.find(**criteria)

    def find_elements(self, **criteria) -> List[Element]:
        """Find all elements matching criteria"""
        state = self.executor.observe()
        return state.find_all(**criteria)

    # =========================================================================
    # Click Operations
    # =========================================================================

    def click(self, x: int = None, y: int = None,
              text: str = None, element_type: str = None,
              identifier: str = None, element: Element = None,
              verify: bool = True) -> Tuple[bool, str]:
        """
        Click with automatic target resolution.

        Priority:
        1. element (if provided)
        2. text/type/identifier search
        3. x, y coordinates

        Args:
            x, y: Direct coordinates
            text: Find element by text
            element_type: Find element by type
            identifier: Find element by resource ID
            element: Click this element directly
            verify: Whether to verify click (slower but reliable)

        Returns:
            (success, message) tuple
        """
        # Resolve click target
        target = self._resolve_click_target(x, y, text, element_type, identifier, element)
        if not target:
            return False, "Could not resolve click target"

        logger.info(f"Click target: ({target.x}, {target.y}) source={target.source}")

        # Execute click
        if verify:
            result = self.executor.click_and_verify((target.x, target.y))
            if result.result == ActionResult.SUCCESS:
                return True, "Click verified"
            elif result.result == ActionResult.NO_CHANGE:
                return False, "Screen did not change after click"
            else:
                return False, result.message
        else:
            # Quick click without verification
            if self.prefer_mcp and self._mcp_click:
                try:
                    self._mcp_click(target.x, target.y)
                    return True, "Clicked via MCP"
                except Exception as e:
                    logger.warning(f"MCP click failed: {e}, falling back to ADB")

            return tap(target.x, target.y, self.device_id)

    def _resolve_click_target(self, x: int = None, y: int = None,
                               text: str = None, element_type: str = None,
                               identifier: str = None,
                               element: Element = None) -> Optional[ClickTarget]:
        """Resolve click target from various inputs"""

        # Direct element
        if element:
            cx, cy = element.center
            return ClickTarget(x=cx, y=cy, source="element", element=element)

        # Search by criteria
        if text or element_type or identifier:
            state = self.executor.observe()

            # Build search criteria
            criteria = {}
            if text:
                criteria['text'] = text
            if element_type:
                criteria['type'] = element_type
            if identifier:
                criteria['identifier'] = identifier

            found = state.find(**criteria)
            if found:
                cx, cy = found.center
                return ClickTarget(x=cx, y=cy, source="search", element=found)
            else:
                logger.warning(f"Element not found: {criteria}")
                return None

        # Direct coordinates
        if x is not None and y is not None:
            return ClickTarget(x=int(x), y=int(y), source="coordinate")

        return None

    def double_click(self, x: int = None, y: int = None,
                     text: str = None, interval_ms: int = 100) -> Tuple[bool, str]:
        """Double click at target"""
        target = self._resolve_click_target(x, y, text)
        if not target:
            return False, "Could not resolve target"

        ok1, _ = tap(target.x, target.y, self.device_id)
        time.sleep(interval_ms / 1000)
        ok2, msg = tap(target.x, target.y, self.device_id)

        return ok1 and ok2, msg

    def long_press(self, x: int = None, y: int = None,
                   text: str = None, duration_ms: int = 1000) -> Tuple[bool, str]:
        """Long press at target"""
        target = self._resolve_click_target(x, y, text)
        if not target:
            return False, "Could not resolve target"

        # Long press is implemented as swipe with same start/end
        args = ["shell", "input", "swipe",
                str(target.x), str(target.y), str(target.x), str(target.y),
                str(duration_ms)]
        if self.device_id:
            args = ["-s", self.device_id] + args

        return run_adb(args)

    # =========================================================================
    # Text Input Operations
    # =========================================================================

    def type_text(self, text: str, submit: bool = False) -> Tuple[bool, str]:
        """
        Type text into focused element.

        Supports Unicode via ADBKeyboard (Python) or DeviceKit (MCP).

        Args:
            text: Text to type
            submit: Whether to press Enter after typing

        Returns:
            (success, message) tuple
        """
        # Try MCP first (DeviceKit provides better Unicode support)
        if self.prefer_mcp and self._mcp_type:
            try:
                self._mcp_type(text, submit)
                return True, "Typed via MCP"
            except Exception as e:
                logger.warning(f"MCP type failed: {e}, falling back to ADB")

        # ADB fallback (ADBKeyboard for Unicode)
        ok, msg = adb_type_text(text, self.device_id)

        if ok and submit:
            time.sleep(0.3)
            press_enter(self.device_id)

        return ok, msg

    def tap_and_type(self, text: str, x: int = None, y: int = None,
                     element_text: str = None, submit: bool = False,
                     clear_first: bool = False) -> Tuple[bool, str]:
        """
        Tap input field and type text.

        Args:
            text: Text to type
            x, y: Input field coordinates
            element_text: Find input by text/hint
            submit: Press Enter after typing
            clear_first: Clear existing text first
        """
        # Find and click input
        if element_text:
            ok, msg = self.click(text=element_text)
        elif x is not None and y is not None:
            ok, msg = self.click(x=x, y=y)
        else:
            return False, "No target specified"

        if not ok:
            return False, f"Failed to tap input: {msg}"

        # Wait for keyboard
        time.sleep(0.5)

        # Clear if requested
        if clear_first:
            self.adb.clear_text(50)
            time.sleep(0.2)

        # Type
        return self.type_text(text, submit)

    # =========================================================================
    # Swipe/Scroll Operations
    # =========================================================================

    def swipe(self, direction: str = "up", distance: int = None,
              x: int = None, y: int = None, verify: bool = True) -> Tuple[bool, str]:
        """
        Swipe in direction.

        Args:
            direction: "up", "down", "left", "right"
            distance: Swipe distance (auto-calculated if None)
            x, y: Starting point (center if None)
            verify: Verify content changed

        Returns:
            (success, message) tuple
        """
        if verify:
            result = self.executor.swipe_and_verify(direction, distance, (x, y) if x and y else None)
            if result.result == ActionResult.SUCCESS:
                return True, "Swipe verified"
            elif result.result == ActionResult.NO_CHANGE:
                return True, "Swipe executed (content may have reached end)"
            else:
                return False, result.message

        # Quick swipe without verification
        if self.prefer_mcp and self._mcp_swipe:
            try:
                self._mcp_swipe(direction, distance, x, y)
                return True, f"Swiped {direction} via MCP"
            except Exception as e:
                logger.warning(f"MCP swipe failed: {e}, falling back to ADB")

        # ADB swipe
        w, h = self.screen_size
        cx, cy = x or w // 2, y or h // 2
        dist = distance or h // 3

        if direction == "up":
            return swipe(cx, cy + dist // 2, cx, cy - dist // 2, 300, self.device_id)
        elif direction == "down":
            return swipe(cx, cy - dist // 2, cx, cy + dist // 2, 300, self.device_id)
        elif direction == "left":
            return swipe(cx + dist // 2, cy, cx - dist // 2, cy, 300, self.device_id)
        elif direction == "right":
            return swipe(cx - dist // 2, cy, cx + dist // 2, cy, 300, self.device_id)
        else:
            return False, f"Invalid direction: {direction}"

    def scroll_up(self) -> Tuple[bool, str]:
        """Scroll up (swipe up)"""
        return self.swipe("up")

    def scroll_down(self) -> Tuple[bool, str]:
        """Scroll down (swipe down)"""
        return self.swipe("down")

    def scroll_to_text(self, text: str, max_scrolls: int = 5,
                       direction: str = "up") -> Tuple[bool, Element]:
        """
        Scroll until text is found.

        Args:
            text: Text to find
            max_scrolls: Maximum scroll attempts
            direction: Scroll direction

        Returns:
            (found, element) tuple
        """
        for i in range(max_scrolls):
            state = self.executor.observe()
            element = state.find(text=text)
            if element:
                logger.info(f"Found '{text}' after {i} scrolls")
                return True, element

            self.swipe(direction, verify=False)
            time.sleep(0.5)

        logger.warning(f"Text '{text}' not found after {max_scrolls} scrolls")
        return False, None

    # =========================================================================
    # Button/Key Operations
    # =========================================================================

    def press_button(self, button: str) -> Tuple[bool, str]:
        """
        Press hardware/soft button.

        Supported: BACK, HOME, ENTER, VOLUME_UP, VOLUME_DOWN
        """
        button = button.upper()

        if self.prefer_mcp and self._mcp_press:
            try:
                self._mcp_press(button)
                return True, f"Pressed {button} via MCP"
            except Exception as e:
                logger.warning(f"MCP press failed: {e}, falling back to ADB")

        # ADB fallback
        if button == "BACK":
            return press_back(self.device_id)
        elif button == "HOME":
            return press_home(self.device_id)
        elif button == "ENTER":
            return press_enter(self.device_id)
        else:
            from adb_helper import KEYCODE
            if button in KEYCODE:
                return press_key(KEYCODE[button], self.device_id)
            return False, f"Unknown button: {button}"

    def back(self, verify: bool = True) -> Tuple[bool, str]:
        """Press back button"""
        if verify:
            result = self.executor.back_and_verify()
            if result.result == ActionResult.SUCCESS:
                return True, "Back verified"
            return False, result.message

        return press_back(self.device_id)

    def home(self) -> Tuple[bool, str]:
        """Press home button"""
        return press_home(self.device_id)

    # =========================================================================
    # App Operations
    # =========================================================================

    def launch_app(self, package: str, wait: float = 2.0) -> Tuple[bool, str]:
        """
        Launch app by package name.

        Args:
            package: App package name
            wait: Time to wait for app to load

        Returns:
            (success, message) tuple
        """
        if self.prefer_mcp and self._mcp_launch:
            try:
                self._mcp_launch(package)
                time.sleep(wait)
                return True, f"Launched {package} via MCP"
            except Exception as e:
                logger.warning(f"MCP launch failed: {e}, falling back to ADB")

        ok, msg = launch_app(package, self.device_id)
        if ok:
            time.sleep(wait)
        return ok, msg

    def stop_app(self, package: str) -> Tuple[bool, str]:
        """Force stop app"""
        return stop_app(package, self.device_id)

    def restart_app(self, package: str, wait: float = 2.0) -> Tuple[bool, str]:
        """Stop and relaunch app"""
        self.stop_app(package)
        time.sleep(0.5)
        return self.launch_app(package, wait)

    # =========================================================================
    # Wait Operations
    # =========================================================================

    def wait_for_element(self, timeout: float = 5.0, **criteria) -> Tuple[bool, Optional[Element]]:
        """
        Wait for element to appear.

        Args:
            timeout: Maximum wait time
            **criteria: Element criteria (text, type, identifier)

        Returns:
            (found, element) tuple
        """
        return self.executor.wait_for_element(timeout, **criteria)

    def wait_for_text(self, text: str, timeout: float = 5.0) -> bool:
        """Wait for text to appear"""
        return self.executor.wait_for_text(text, timeout)

    def wait(self, seconds: float):
        """Simple wait"""
        time.sleep(seconds)

    # =========================================================================
    # Screenshot Operations
    # =========================================================================

    def take_screenshot(self, save_path: str = None, prefix: str = "screen") -> Optional[str]:
        """
        Take screenshot.

        Args:
            save_path: Path to save (auto-generated if None)
            prefix: Filename prefix

        Returns:
            Path to saved screenshot
        """
        if self.prefer_mcp and self._mcp_screenshot:
            try:
                # MCP screenshot returns image data
                result = self._mcp_screenshot()
                # Handle MCP result format
                return result
            except Exception as e:
                logger.warning(f"MCP screenshot failed: {e}, falling back to ADB")

        return screenshot(save_path, self.device_id, prefix)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_screen_state(self) -> ScreenState:
        """Get current screen state"""
        return self.executor.observe()

    def has_text(self, text: str) -> bool:
        """Check if text is visible"""
        return self.executor.has_text(text)

    def get_current_package(self) -> Optional[str]:
        """Get current foreground app package"""
        args = ["shell", "dumpsys", "window", "windows"]
        if self.device_id:
            args = ["-s", self.device_id] + args

        ok, output = run_adb(args)
        if ok:
            import re
            match = re.search(r'mCurrentFocus=.*?([a-zA-Z0-9_.]+)/[a-zA-Z0-9_.]+', output)
            if match:
                return match.group(1)
        return None


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print("=== Tool Router Test ===\n")

    router = ToolRouter()

    # Test element listing
    print("1. Listing elements...")
    elements = router.list_elements()
    print(f"   Found {len(elements)} elements")

    # Test find
    print("\n2. Finding clickable elements...")
    clickables = router.find_elements(clickable=True)
    print(f"   Found {len(clickables)} clickable elements")
    for el in clickables[:3]:
        print(f"   - {el.label} at {el.center}")

    # Test screen state
    print("\n3. Getting screen state...")
    state = router.get_screen_state()
    print(f"   Hash: {state.screen_hash}")
    print(f"   Elements: {len(state.elements)}")

    # Test current package
    print("\n4. Current app package...")
    package = router.get_current_package()
    print(f"   Package: {package}")
