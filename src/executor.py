#!/usr/bin/env python3
"""
Deterministic Executor - Enforces Element-First strategy for device automation.

This module provides a structured execution layer that ensures:
1. Every click is preceded by element discovery
2. Every action is followed by verification
3. Proper waiting and retry mechanisms

Usage:
    from src.executor import DeterministicExecutor, ScreenState

    executor = DeterministicExecutor()
    state = executor.observe()
    element = executor.find_element(state, text="Search")
    if element:
        ok, new_state = executor.click_and_verify(element)
"""
import os
import sys
import json
import time
import hashlib
import re
import subprocess
import xml.etree.ElementTree as ET
from typing import Optional, Dict, List, Tuple, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from logger import get_logger
from adb_helper import ADBHelper, run_adb, tap, swipe, press_back

logger = get_logger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================

def _to_bool(value) -> bool:
    """Convert various representations to bool.

    Handles: bool, "true"/"false", "True"/"False", 1/0, "1"/"0", None
    """
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in ('true', '1', 'yes')
    return bool(value)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Element:
    """Represents a UI element on screen"""
    text: str = ""
    content_desc: str = ""
    element_type: str = ""
    identifier: str = ""
    bounds: Dict[str, int] = field(default_factory=dict)
    clickable: bool = False
    scrollable: bool = False
    focusable: bool = False
    enabled: bool = True
    raw: Dict = field(default_factory=dict)

    @property
    def center(self) -> Tuple[int, int]:
        """Calculate center point of element"""
        if not self.bounds:
            return (0, 0)
        x = self.bounds.get('x', 0)
        y = self.bounds.get('y', 0)
        w = self.bounds.get('width', 0)
        h = self.bounds.get('height', 0)
        return (x + w // 2, y + h // 2)

    @property
    def label(self) -> str:
        """Get display label (text or content description)"""
        return self.text or self.content_desc or self.element_type

    def matches(self, **criteria) -> bool:
        """Check if element matches given criteria"""
        for key, value in criteria.items():
            if value is None:
                continue

            if key == 'text':
                if value.lower() not in self.text.lower():
                    return False
            elif key == 'text_exact':
                if value != self.text:
                    return False
            elif key == 'type':
                if value.lower() not in self.element_type.lower():
                    return False
            elif key == 'identifier':
                if value.lower() not in self.identifier.lower():
                    return False
            elif key == 'content_desc':
                if value.lower() not in self.content_desc.lower():
                    return False
            elif key == 'clickable':
                if self.clickable != value:
                    return False
            elif key == 'scrollable':
                if self.scrollable != value:
                    return False
        return True


@dataclass
class ScreenState:
    """Represents the current screen state"""
    elements: List[Element]
    timestamp: float
    screen_hash: str
    package: str = ""
    activity: str = ""
    raw_data: Any = None

    @classmethod
    def from_elements(cls, elements: List[Dict], package: str = "", activity: str = "") -> 'ScreenState':
        """Create ScreenState from element list (MCP format)"""
        parsed = []
        for el in elements:
            bounds = cls._parse_bounds(el)
            parsed.append(Element(
                text=el.get('text', el.get('label', '')),
                content_desc=el.get('contentDescription', el.get('content_desc', '')),
                element_type=el.get('type', el.get('class', el.get('className', ''))),
                identifier=el.get('identifier', el.get('resourceId', el.get('resource-id', ''))),
                bounds=bounds,
                clickable=_to_bool(el.get('clickable')),
                scrollable=_to_bool(el.get('scrollable')),
                focusable=_to_bool(el.get('focusable')),
                enabled=_to_bool(el.get('enabled', True)),
                raw=el
            ))

        # Generate hash for comparison
        hash_input = json.dumps(
            [(e.text, e.element_type, e.identifier, str(e.bounds)) for e in parsed],
            sort_keys=True
        )
        screen_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]

        return cls(
            elements=parsed,
            timestamp=time.time(),
            screen_hash=screen_hash,
            package=package,
            activity=activity,
            raw_data=elements
        )

    @classmethod
    def from_xml(cls, xml_content: str) -> 'ScreenState':
        """Create ScreenState from uiautomator XML dump"""
        elements = []
        try:
            root = ET.fromstring(xml_content)
            for node in root.iter('node'):
                bounds = cls._parse_bounds_string(node.get('bounds', ''))
                elements.append(Element(
                    text=node.get('text', ''),
                    content_desc=node.get('content-desc', ''),
                    element_type=node.get('class', ''),
                    identifier=node.get('resource-id', ''),
                    bounds=bounds,
                    clickable=node.get('clickable') == 'true',
                    scrollable=node.get('scrollable') == 'true',
                    focusable=node.get('focusable') == 'true',
                    enabled=node.get('enabled') == 'true',
                    raw=dict(node.attrib)
                ))
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")

        # Generate hash
        hash_input = json.dumps(
            [(e.text, e.element_type, e.identifier) for e in elements],
            sort_keys=True
        )
        screen_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]

        return cls(
            elements=elements,
            timestamp=time.time(),
            screen_hash=screen_hash,
            raw_data=xml_content
        )

    @staticmethod
    def _parse_bounds(el: Dict) -> Dict[str, int]:
        """Parse bounds from MCP element format"""
        # Format: {x, y, width, height}
        if 'x' in el and 'y' in el:
            return {
                'x': int(el.get('x', 0)),
                'y': int(el.get('y', 0)),
                'width': int(el.get('width', 0)),
                'height': int(el.get('height', 0))
            }
        # Format: "[x1,y1][x2,y2]"
        bounds_str = el.get('bounds', '')
        if bounds_str:
            return ScreenState._parse_bounds_string(str(bounds_str))
        return {}

    @staticmethod
    def _parse_bounds_string(bounds_str: str) -> Dict[str, int]:
        """Parse bounds from string format [x1,y1][x2,y2]"""
        if not bounds_str:
            return {}
        match = re.findall(r'\[(\d+),(\d+)\]', bounds_str)
        if len(match) == 2:
            x1, y1 = int(match[0][0]), int(match[0][1])
            x2, y2 = int(match[1][0]), int(match[1][1])
            return {'x': x1, 'y': y1, 'width': x2-x1, 'height': y2-y1}
        return {}

    def find(self, **criteria) -> Optional[Element]:
        """Find first element matching criteria"""
        for el in self.elements:
            if el.matches(**criteria):
                return el
        return None

    def find_all(self, **criteria) -> List[Element]:
        """Find all elements matching criteria"""
        return [el for el in self.elements if el.matches(**criteria)]

    def has_text(self, text: str) -> bool:
        """Check if any element contains the text"""
        text_lower = text.lower()
        return any(text_lower in e.text.lower() or text_lower in e.content_desc.lower()
                   for e in self.elements)


class ActionResult(Enum):
    """Result of an action"""
    SUCCESS = "success"           # Action succeeded, screen changed as expected
    PARTIAL = "partial"           # Screen changed but not as expected
    NO_CHANGE = "no_change"       # Screen did not change
    TIMEOUT = "timeout"           # Action timed out
    ERROR = "error"               # Action failed with error


@dataclass
class ExecutionResult:
    """Result of an execution"""
    result: ActionResult
    before_state: Optional[ScreenState] = None
    after_state: Optional[ScreenState] = None
    message: str = ""
    duration: float = 0.0


# =============================================================================
# Deterministic Executor
# =============================================================================

class DeterministicExecutor:
    """
    Deterministic executor that enforces Element-First strategy.

    Core principle: observe → find → act → verify

    Every action must be preceded by observation and followed by verification.
    This ensures reliable automation without coordinate guessing.
    """

    def __init__(self, device_id: str = None, max_retries: int = 3,
                 verify_timeout: float = 3.0, action_delay: float = 0.5,
                 save_debug_on_failure: bool = True):
        """
        Initialize executor.

        Args:
            device_id: Device serial (auto-detect if None)
            max_retries: Maximum retries for failed actions
            verify_timeout: Timeout for verification (seconds)
            action_delay: Delay between action and verification (seconds)
            save_debug_on_failure: Save screenshot + element dump on action failure
        """
        self.adb = ADBHelper(device_id)
        self.device_id = device_id or self.adb.device_id
        self.max_retries = max_retries
        self.verify_timeout = verify_timeout
        self.action_delay = action_delay
        self.save_debug_on_failure = save_debug_on_failure

        self.last_state: Optional[ScreenState] = None
        self.state_history: List[ScreenState] = []
        self._mcp_callback: Optional[Callable] = None

        # Debug artifacts directory
        self.debug_dir = os.path.join(PROJECT_ROOT, "temp", "debug")
        os.makedirs(self.debug_dir, exist_ok=True)

        logger.info(f"Executor initialized for device: {self.device_id}")

    def set_mcp_callback(self, callback: Callable):
        """
        Set MCP callback for element listing.

        This allows the executor to use MCP's mobile_list_elements_on_screen
        when available, which is faster and more reliable.

        Args:
            callback: Function that returns element list
        """
        self._mcp_callback = callback

    # =========================================================================
    # Observation Methods
    # =========================================================================

    def observe(self, use_mcp: bool = True) -> ScreenState:
        """
        Get current screen state via element tree.

        This is the REQUIRED first step before any action.

        Args:
            use_mcp: Whether to try MCP callback first

        Returns:
            ScreenState with all visible elements
        """
        logger.debug("Observing screen state...")

        # Try MCP callback first (if available)
        if use_mcp and self._mcp_callback:
            try:
                elements = self._mcp_callback()
                if elements:
                    state = ScreenState.from_elements(elements)
                    self._update_state(state)
                    logger.debug(f"Observed {len(state.elements)} elements via MCP")
                    return state
            except Exception as e:
                logger.warning(f"MCP callback failed: {e}, falling back to ADB")

        # Fallback: uiautomator dump
        state = self._observe_via_uiautomator()
        self._update_state(state)
        return state

    def _observe_via_uiautomator(self) -> ScreenState:
        """Get screen state via uiautomator dump (ADB fallback)"""
        dump_path = "/sdcard/window_dump.xml"
        local_path = os.path.join(PROJECT_ROOT, "temp", "window_dump.xml")

        # Dump UI hierarchy
        args = ["shell", "uiautomator", "dump", dump_path]
        if self.device_id:
            args = ["-s", self.device_id] + args

        ok, output = run_adb(args)
        if not ok:
            logger.error(f"uiautomator dump failed: {output}")
            return ScreenState(elements=[], timestamp=time.time(), screen_hash="error")

        # Pull dump file
        pull_args = ["pull", dump_path, local_path]
        if self.device_id:
            pull_args = ["-s", self.device_id] + pull_args
        ok, _ = run_adb(pull_args)
        if not ok or not os.path.exists(local_path):
            logger.error("Failed to pull dump file")
            return ScreenState(elements=[], timestamp=time.time(), screen_hash="error")

        # Parse XML
        with open(local_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()

        state = ScreenState.from_xml(xml_content)
        logger.debug(f"Observed {len(state.elements)} elements via uiautomator")
        return state

    def _update_state(self, state: ScreenState):
        """Update state tracking"""
        self.last_state = state
        self.state_history.append(state)
        # Keep only last 20 states
        if len(self.state_history) > 20:
            self.state_history = self.state_history[-20:]

    def _save_debug_artifacts(self, action: str, error_msg: str,
                               state: ScreenState = None, target: Any = None):
        """
        Save debug artifacts on action failure.

        Saves:
        - screenshot.png: Current screen capture
        - elements.json: Element tree dump
        - info.json: Action details and error info

        Args:
            action: Action name (click, swipe, back, etc.)
            error_msg: Error message
            state: ScreenState at time of failure
            target: Target element or coordinates
        """
        if not self.save_debug_on_failure:
            return

        try:
            # Create timestamped directory
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            artifact_dir = os.path.join(self.debug_dir, f"{timestamp}_{action}_failed")
            os.makedirs(artifact_dir, exist_ok=True)

            # Save screenshot
            screenshot_path = os.path.join(artifact_dir, "screenshot.png")
            self.adb.screenshot(screenshot_path)

            # Save elements
            elements_path = os.path.join(artifact_dir, "elements.json")
            if state is None:
                state = self.last_state
            if state:
                elements_data = []
                for el in state.elements:
                    elements_data.append({
                        "text": el.text,
                        "content_desc": el.content_desc,
                        "type": el.element_type,
                        "identifier": el.identifier,
                        "bounds": el.bounds,
                        "center": el.center,
                        "clickable": el.clickable,
                        "scrollable": el.scrollable,
                    })
                with open(elements_path, 'w', encoding='utf-8') as f:
                    json.dump(elements_data, f, ensure_ascii=False, indent=2)

            # Save info
            info_path = os.path.join(artifact_dir, "info.json")
            target_info = None
            if target:
                if isinstance(target, Element):
                    target_info = {
                        "type": "element",
                        "text": target.text,
                        "center": target.center,
                        "identifier": target.identifier
                    }
                elif isinstance(target, tuple) and len(target) == 2:
                    target_info = {"type": "coordinates", "x": target[0], "y": target[1]}

            info_data = {
                "timestamp": timestamp,
                "action": action,
                "error": error_msg,
                "device_id": self.device_id,
                "target": target_info,
                "screen_hash": state.screen_hash if state else None,
                "element_count": len(state.elements) if state else 0,
            }
            with open(info_path, 'w', encoding='utf-8') as f:
                json.dump(info_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Debug artifacts saved: {artifact_dir}")

        except Exception as e:
            logger.warning(f"Failed to save debug artifacts: {e}")

    # =========================================================================
    # Element Finding Methods
    # =========================================================================

    def find_element(self, state: ScreenState = None, **criteria) -> Optional[Element]:
        """
        Find element by criteria.

        Args:
            state: ScreenState to search (uses last_state if None)
            **criteria: Search criteria (text, type, identifier, etc.)

        Returns:
            Element if found, None otherwise

        Example:
            element = executor.find_element(text="Search")
            element = executor.find_element(type="EditText", clickable=True)
            element = executor.find_element(identifier="com.app:id/search")
        """
        if state is None:
            state = self.last_state
        if state is None:
            logger.warning("No state available, call observe() first")
            return None

        return state.find(**criteria)

    def find_elements(self, state: ScreenState = None, **criteria) -> List[Element]:
        """Find all elements matching criteria"""
        if state is None:
            state = self.last_state
        if state is None:
            return []
        return state.find_all(**criteria)

    def find_by_text(self, text: str, state: ScreenState = None) -> Optional[Element]:
        """Convenience method to find by text"""
        return self.find_element(state, text=text)

    def find_by_type(self, element_type: str, state: ScreenState = None) -> Optional[Element]:
        """Convenience method to find by type"""
        return self.find_element(state, type=element_type)

    def find_by_id(self, identifier: str, state: ScreenState = None) -> Optional[Element]:
        """Convenience method to find by resource ID"""
        return self.find_element(state, identifier=identifier)

    # =========================================================================
    # Action Methods (with verification)
    # =========================================================================

    def click_and_verify(self, target: Union[Element, Tuple[int, int]],
                         expected_text: str = None,
                         expected_gone: str = None) -> ExecutionResult:
        """
        Click element and verify screen changed.

        This is the CORRECT way to click - always verify after action.

        Args:
            target: Element to click or (x, y) coordinates
            expected_text: Text expected to appear after click
            expected_gone: Text expected to disappear after click

        Returns:
            ExecutionResult with before/after states and result
        """
        start_time = time.time()

        # Get click coordinates
        if isinstance(target, Element):
            x, y = target.center
            logger.info(f"Click element '{target.label}' at ({x}, {y})")
        else:
            x, y = target
            logger.info(f"Click at ({x}, {y})")

        # Get before state
        before_state = self.last_state or self.observe()
        before_hash = before_state.screen_hash

        # Execute click
        ok, msg = tap(x, y, self.device_id)
        if not ok:
            self._save_debug_artifacts("click", f"tap failed: {msg}",
                                        before_state, target)
            return ExecutionResult(
                result=ActionResult.ERROR,
                before_state=before_state,
                message=f"Click failed: {msg}",
                duration=time.time() - start_time
            )

        # Wait and verify
        time.sleep(self.action_delay)

        for attempt in range(self.max_retries):
            after_state = self.observe()

            # Check if screen changed
            if after_state.screen_hash != before_hash:
                # Verify expected conditions
                if expected_text and not after_state.has_text(expected_text):
                    continue  # Screen changed but not as expected
                if expected_gone and after_state.has_text(expected_gone):
                    continue  # Old content still visible

                return ExecutionResult(
                    result=ActionResult.SUCCESS,
                    before_state=before_state,
                    after_state=after_state,
                    message="Click verified",
                    duration=time.time() - start_time
                )

            # Wait more before retry
            time.sleep(0.5 * (attempt + 1))

        # Screen didn't change after retries
        self._save_debug_artifacts("click", "screen did not change",
                                    self.last_state, target)
        return ExecutionResult(
            result=ActionResult.NO_CHANGE,
            before_state=before_state,
            after_state=self.last_state,
            message="Screen did not change after click",
            duration=time.time() - start_time
        )

    def click(self, target: Union[Element, Tuple[int, int]]) -> Tuple[bool, str]:
        """
        Simple click without full verification (for speed when not critical).
        Still updates state after action.
        """
        if isinstance(target, Element):
            x, y = target.center
        else:
            x, y = target

        ok, msg = tap(x, y, self.device_id)
        if ok:
            time.sleep(self.action_delay)
            self.observe()
        return ok, msg

    def swipe_and_verify(self, direction: str = "up",
                         distance: int = None,
                         start_point: Tuple[int, int] = None) -> ExecutionResult:
        """
        Swipe and verify content changed.

        Args:
            direction: "up", "down", "left", "right"
            distance: Swipe distance in pixels (auto-calculated if None)
            start_point: Starting point (screen center if None)

        Returns:
            ExecutionResult with before/after states
        """
        start_time = time.time()

        # Get screen size
        w, h = self.adb.get_screen_size()
        if not w or not h:
            return ExecutionResult(
                result=ActionResult.ERROR,
                message="Cannot get screen size",
                duration=time.time() - start_time
            )

        # Calculate swipe parameters
        if start_point:
            cx, cy = start_point
        else:
            cx, cy = w // 2, h // 2

        if distance is None:
            distance = h // 3 if direction in ("up", "down") else w // 3

        # Calculate end point
        if direction == "up":
            x1, y1, x2, y2 = cx, cy + distance // 2, cx, cy - distance // 2
        elif direction == "down":
            x1, y1, x2, y2 = cx, cy - distance // 2, cx, cy + distance // 2
        elif direction == "left":
            x1, y1, x2, y2 = cx + distance // 2, cy, cx - distance // 2, cy
        elif direction == "right":
            x1, y1, x2, y2 = cx - distance // 2, cy, cx + distance // 2, cy
        else:
            return ExecutionResult(
                result=ActionResult.ERROR,
                message=f"Invalid direction: {direction}",
                duration=time.time() - start_time
            )

        # Get before state
        before_state = self.last_state or self.observe()
        before_hash = before_state.screen_hash

        # Execute swipe
        logger.info(f"Swipe {direction}: ({x1},{y1}) -> ({x2},{y2})")
        ok, msg = swipe(x1, y1, x2, y2, 300, self.device_id)
        if not ok:
            self._save_debug_artifacts("swipe", f"swipe {direction} failed: {msg}",
                                        before_state, (x1, y1))
            return ExecutionResult(
                result=ActionResult.ERROR,
                before_state=before_state,
                message=f"Swipe failed: {msg}",
                duration=time.time() - start_time
            )

        # Wait and verify
        time.sleep(self.action_delay + 0.5)  # Extra wait for scroll animation

        for attempt in range(self.max_retries):
            after_state = self.observe()

            if after_state.screen_hash != before_hash:
                return ExecutionResult(
                    result=ActionResult.SUCCESS,
                    before_state=before_state,
                    after_state=after_state,
                    message="Swipe verified",
                    duration=time.time() - start_time
                )

            time.sleep(0.5 * (attempt + 1))

        # Content might not have changed (end of list)
        return ExecutionResult(
            result=ActionResult.NO_CHANGE,
            before_state=before_state,
            after_state=self.last_state,
            message="Content may have reached end",
            duration=time.time() - start_time
        )

    def back_and_verify(self, expected_text: str = None) -> ExecutionResult:
        """
        Press back and verify navigation.

        Args:
            expected_text: Text expected on previous screen

        Returns:
            ExecutionResult
        """
        start_time = time.time()
        before_state = self.last_state or self.observe()
        before_hash = before_state.screen_hash

        # Press back
        ok, msg = press_back(self.device_id)
        if not ok:
            self._save_debug_artifacts("back", f"press_back failed: {msg}",
                                        before_state)
            return ExecutionResult(
                result=ActionResult.ERROR,
                before_state=before_state,
                message=f"Back failed: {msg}",
                duration=time.time() - start_time
            )

        # Wait and verify
        time.sleep(self.action_delay)

        for attempt in range(self.max_retries):
            after_state = self.observe()

            if after_state.screen_hash != before_hash:
                if expected_text and not after_state.has_text(expected_text):
                    continue

                return ExecutionResult(
                    result=ActionResult.SUCCESS,
                    before_state=before_state,
                    after_state=after_state,
                    message="Back verified",
                    duration=time.time() - start_time
                )

            time.sleep(0.5 * (attempt + 1))

        self._save_debug_artifacts("back", "screen did not change after back",
                                    self.last_state)
        return ExecutionResult(
            result=ActionResult.NO_CHANGE,
            before_state=before_state,
            after_state=self.last_state,
            message="Screen did not change after back",
            duration=time.time() - start_time
        )

    # =========================================================================
    # Wait Methods
    # =========================================================================

    def wait_for_element(self, timeout: float = None, **criteria) -> Tuple[bool, Optional[Element]]:
        """
        Wait for element to appear.

        Args:
            timeout: Maximum wait time (uses verify_timeout if None)
            **criteria: Element criteria

        Returns:
            (found, element) tuple
        """
        timeout = timeout or self.verify_timeout
        start = time.time()

        while time.time() - start < timeout:
            state = self.observe()
            element = state.find(**criteria)
            if element:
                logger.debug(f"Found element matching {criteria}")
                return True, element
            time.sleep(0.5)

        logger.debug(f"Element not found within {timeout}s: {criteria}")
        return False, None

    def wait_for_text(self, text: str, timeout: float = None) -> bool:
        """Wait for text to appear on screen"""
        found, _ = self.wait_for_element(timeout, text=text)
        return found

    def wait_for_screen_change(self, timeout: float = None) -> bool:
        """Wait for screen to change from current state"""
        timeout = timeout or self.verify_timeout
        if not self.last_state:
            return False

        original_hash = self.last_state.screen_hash
        start = time.time()

        while time.time() - start < timeout:
            state = self.observe()
            if state.screen_hash != original_hash:
                return True
            time.sleep(0.3)

        return False

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def get_screen_text(self) -> List[str]:
        """Get all visible text on screen"""
        state = self.last_state or self.observe()
        texts = []
        for el in state.elements:
            if el.text:
                texts.append(el.text)
            if el.content_desc and el.content_desc != el.text:
                texts.append(el.content_desc)
        return texts

    def has_text(self, text: str) -> bool:
        """Check if text is visible on screen"""
        state = self.last_state or self.observe()
        return state.has_text(text)

    def clear_history(self):
        """Clear state history"""
        self.state_history = []
        self.last_state = None


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print("=== Deterministic Executor Test ===\n")

    executor = DeterministicExecutor()

    # Test observe
    print("1. Observing screen...")
    state = executor.observe()
    print(f"   Found {len(state.elements)} elements")
    print(f"   Screen hash: {state.screen_hash}")

    # Show first few elements
    print("\n2. First 5 elements:")
    for el in state.elements[:5]:
        print(f"   - {el.element_type}: '{el.label}' at {el.center}")

    # Test find
    print("\n3. Testing find_element...")
    edit_text = executor.find_element(type="EditText")
    if edit_text:
        print(f"   Found EditText: '{edit_text.text}' at {edit_text.center}")
    else:
        print("   No EditText found")

    # Test find clickable
    print("\n4. Finding clickable elements...")
    clickables = executor.find_elements(clickable=True)
    print(f"   Found {len(clickables)} clickable elements")
