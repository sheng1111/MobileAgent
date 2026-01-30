#!/usr/bin/env python3
"""
U2Driver - uiautomator2 integration for precise element-based automation.

This module provides selector-based operations that are more reliable than
coordinate-based clicking. It uses uiautomator2 Python library directly.

Key advantages over coordinate-based approach:
- click_by_text("Search") - no coordinate guessing
- click_by_id("com.app:id/button") - stable across screen sizes
- wait_for_element(text="Loading", gone=True) - smart waiting
- scroll_to(text="Settings") - auto-scroll to find element

Usage:
    from src.u2_driver import U2Driver

    driver = U2Driver()
    driver.click_by_text("Search")
    driver.type_text("query", clear_first=True)
    driver.wait_for_element(text="Results", timeout=5)

Install:
    pip install uiautomator2
"""
import os
import sys
import time
from typing import Optional, Dict, List, Tuple, Any, Union
from dataclasses import dataclass

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from logger import get_logger

logger = get_logger(__name__)

# Try to import uiautomator2
try:
    import uiautomator2 as u2
    U2_AVAILABLE = True
except ImportError:
    U2_AVAILABLE = False
    logger.warning("uiautomator2 not installed. Run: pip install uiautomator2")


@dataclass
class U2Element:
    """Wrapper for uiautomator2 element info"""
    text: str = ""
    resource_id: str = ""
    description: str = ""
    class_name: str = ""
    bounds: Dict[str, int] = None
    clickable: bool = False
    enabled: bool = True

    @property
    def center(self) -> Tuple[int, int]:
        if not self.bounds:
            return (0, 0)
        x = (self.bounds['left'] + self.bounds['right']) // 2
        y = (self.bounds['top'] + self.bounds['bottom']) // 2
        return (x, y)


class U2Driver:
    """
    uiautomator2 driver for precise element-based automation.

    Provides selector-based operations that are more reliable than
    coordinate-based clicking.
    """

    def __init__(self, device_serial: str = None, auto_connect: bool = True):
        """
        Initialize U2Driver.

        Args:
            device_serial: Device serial (auto-detect if None)
            auto_connect: Whether to connect immediately
        """
        if not U2_AVAILABLE:
            raise ImportError("uiautomator2 not installed. Run: pip install uiautomator2")

        self.device_serial = device_serial
        self.device = None
        self._connected = False

        if auto_connect:
            self.connect()

    def connect(self, device_serial: str = None) -> bool:
        """
        Connect to device.

        Args:
            device_serial: Device serial (uses init value if None)

        Returns:
            True if connected successfully
        """
        serial = device_serial or self.device_serial
        try:
            if serial:
                self.device = u2.connect(serial)
            else:
                self.device = u2.connect()  # Auto-detect

            # Verify connection
            info = self.device.info
            self.device_serial = info.get('serial', serial)
            self._connected = True
            logger.info(f"U2Driver connected: {self.device_serial}")
            return True

        except Exception as e:
            logger.error(f"U2Driver connection failed: {e}")
            self._connected = False
            return False

    @property
    def connected(self) -> bool:
        return self._connected and self.device is not None

    def _ensure_connected(self):
        """Ensure device is connected"""
        if not self.connected:
            raise ConnectionError("Device not connected. Call connect() first.")

    # =========================================================================
    # Selector-Based Click Operations
    # =========================================================================

    def click_by_text(self, text: str, timeout: float = 5.0,
                      exact: bool = False) -> Tuple[bool, str]:
        """
        Click element by text.

        Args:
            text: Text to find
            timeout: Wait timeout
            exact: Exact match (default: contains)

        Returns:
            (success, message)
        """
        self._ensure_connected()
        try:
            if exact:
                el = self.device(text=text)
            else:
                el = self.device(textContains=text)

            if el.wait(timeout=timeout):
                el.click()
                logger.info(f"Clicked by text: '{text}'")
                return True, f"Clicked '{text}'"
            else:
                return False, f"Element not found: text='{text}'"

        except Exception as e:
            logger.error(f"click_by_text failed: {e}")
            return False, str(e)

    def click_by_id(self, resource_id: str, timeout: float = 5.0) -> Tuple[bool, str]:
        """
        Click element by resource ID.

        Args:
            resource_id: Resource ID (e.g., "com.app:id/button")
            timeout: Wait timeout

        Returns:
            (success, message)
        """
        self._ensure_connected()
        try:
            el = self.device(resourceId=resource_id)
            if el.wait(timeout=timeout):
                el.click()
                logger.info(f"Clicked by ID: '{resource_id}'")
                return True, f"Clicked '{resource_id}'"
            else:
                return False, f"Element not found: id='{resource_id}'"

        except Exception as e:
            logger.error(f"click_by_id failed: {e}")
            return False, str(e)

    def click_by_desc(self, description: str, timeout: float = 5.0) -> Tuple[bool, str]:
        """
        Click element by content description.

        Args:
            description: Content description
            timeout: Wait timeout

        Returns:
            (success, message)
        """
        self._ensure_connected()
        try:
            el = self.device(descriptionContains=description)
            if el.wait(timeout=timeout):
                el.click()
                logger.info(f"Clicked by description: '{description}'")
                return True, f"Clicked '{description}'"
            else:
                return False, f"Element not found: desc='{description}'"

        except Exception as e:
            logger.error(f"click_by_desc failed: {e}")
            return False, str(e)

    def click_by_selector(self, timeout: float = 5.0, **selector) -> Tuple[bool, str]:
        """
        Click element by flexible selector.

        Args:
            timeout: Wait timeout
            **selector: Selector kwargs (text, resourceId, className, etc.)

        Returns:
            (success, message)

        Example:
            click_by_selector(text="Login", className="android.widget.Button")
        """
        self._ensure_connected()
        try:
            el = self.device(**selector)
            if el.wait(timeout=timeout):
                el.click()
                logger.info(f"Clicked by selector: {selector}")
                return True, f"Clicked {selector}"
            else:
                return False, f"Element not found: {selector}"

        except Exception as e:
            logger.error(f"click_by_selector failed: {e}")
            return False, str(e)

    def click_if_exists(self, timeout: float = 3.0, **selector) -> bool:
        """
        Click element if it exists (no error if not found).

        Useful for dismissing optional popups/dialogs.

        Returns:
            True if clicked, False if not found
        """
        self._ensure_connected()
        try:
            el = self.device(**selector)
            return el.click_exists(timeout=timeout)
        except Exception:
            return False

    # =========================================================================
    # Wait Operations
    # =========================================================================

    def wait_for_element(self, timeout: float = 10.0, gone: bool = False,
                         **selector) -> Tuple[bool, Optional[U2Element]]:
        """
        Wait for element to appear or disappear.

        Args:
            timeout: Wait timeout
            gone: If True, wait for element to disappear
            **selector: Selector kwargs

        Returns:
            (found/gone, element_info)
        """
        self._ensure_connected()
        try:
            el = self.device(**selector)

            if gone:
                result = el.wait_gone(timeout=timeout)
                return result, None
            else:
                result = el.wait(timeout=timeout)
                if result:
                    info = el.info
                    return True, U2Element(
                        text=info.get('text', ''),
                        resource_id=info.get('resourceId', ''),
                        description=info.get('contentDescription', ''),
                        class_name=info.get('className', ''),
                        bounds=info.get('bounds'),
                        clickable=info.get('clickable', False),
                        enabled=info.get('enabled', True)
                    )
                return False, None

        except Exception as e:
            logger.error(f"wait_for_element failed: {e}")
            return False, None

    def wait_for_text(self, text: str, timeout: float = 10.0,
                      gone: bool = False) -> bool:
        """
        Wait for text to appear or disappear.

        Args:
            text: Text to wait for
            timeout: Wait timeout
            gone: If True, wait for text to disappear

        Returns:
            True if condition met
        """
        found, _ = self.wait_for_element(timeout=timeout, gone=gone, textContains=text)
        return found

    # =========================================================================
    # Text Input Operations
    # =========================================================================

    def type_text(self, text: str, clear_first: bool = False) -> Tuple[bool, str]:
        """
        Type text into focused element.

        Args:
            text: Text to type
            clear_first: Clear existing text first

        Returns:
            (success, message)
        """
        self._ensure_connected()
        try:
            if clear_first:
                self.device.clear_text()
                time.sleep(0.2)

            self.device.send_keys(text)
            logger.info(f"Typed text: '{text[:30]}...'")
            return True, "Text typed"

        except Exception as e:
            logger.error(f"type_text failed: {e}")
            return False, str(e)

    def type_into(self, text: str, clear_first: bool = True,
                  **selector) -> Tuple[bool, str]:
        """
        Find element, click it, and type text.

        Args:
            text: Text to type
            clear_first: Clear existing text first
            **selector: Element selector

        Returns:
            (success, message)
        """
        self._ensure_connected()
        try:
            el = self.device(**selector)
            if not el.wait(timeout=5):
                return False, f"Element not found: {selector}"

            el.click()
            time.sleep(0.3)

            if clear_first:
                el.clear_text()
                time.sleep(0.2)

            el.set_text(text)
            logger.info(f"Typed '{text[:30]}...' into {selector}")
            return True, "Text typed"

        except Exception as e:
            logger.error(f"type_into failed: {e}")
            return False, str(e)

    # =========================================================================
    # Scroll Operations
    # =========================================================================

    def scroll_to(self, direction: str = "down", max_scrolls: int = 10,
                  **selector) -> Tuple[bool, Optional[U2Element]]:
        """
        Scroll until element is found.

        Args:
            direction: "up", "down", "left", "right"
            max_scrolls: Maximum scroll attempts
            **selector: Element selector

        Returns:
            (found, element_info)
        """
        self._ensure_connected()
        try:
            el = self.device(**selector)

            # Check if already visible
            if el.exists:
                info = el.info
                return True, U2Element(
                    text=info.get('text', ''),
                    bounds=info.get('bounds')
                )

            # Scroll to find
            for i in range(max_scrolls):
                if direction == "down":
                    self.device(scrollable=True).scroll.toEnd(steps=20)
                elif direction == "up":
                    self.device(scrollable=True).scroll.toBeginning(steps=20)
                else:
                    # Horizontal scroll
                    self.device(scrollable=True).scroll.horiz.forward(steps=20)

                time.sleep(0.5)

                if el.exists:
                    info = el.info
                    return True, U2Element(
                        text=info.get('text', ''),
                        bounds=info.get('bounds')
                    )

            return False, None

        except Exception as e:
            logger.error(f"scroll_to failed: {e}")
            return False, None

    def swipe(self, direction: str = "up", scale: float = 0.5) -> Tuple[bool, str]:
        """
        Swipe in direction.

        Args:
            direction: "up", "down", "left", "right"
            scale: Swipe distance as fraction of screen (0.0-1.0)

        Returns:
            (success, message)
        """
        self._ensure_connected()
        try:
            if direction == "up":
                self.device.swipe_ext("up", scale=scale)
            elif direction == "down":
                self.device.swipe_ext("down", scale=scale)
            elif direction == "left":
                self.device.swipe_ext("left", scale=scale)
            elif direction == "right":
                self.device.swipe_ext("right", scale=scale)
            else:
                return False, f"Invalid direction: {direction}"

            return True, f"Swiped {direction}"

        except Exception as e:
            logger.error(f"swipe failed: {e}")
            return False, str(e)

    # =========================================================================
    # App Operations
    # =========================================================================

    def launch_app(self, package: str, activity: str = None,
                   wait: bool = True) -> Tuple[bool, str]:
        """
        Launch app.

        Args:
            package: Package name
            activity: Activity name (optional)
            wait: Wait for app to launch

        Returns:
            (success, message)
        """
        self._ensure_connected()
        try:
            if activity:
                self.device.app_start(package, activity, wait=wait)
            else:
                self.device.app_start(package, wait=wait)

            logger.info(f"Launched app: {package}")
            return True, f"Launched {package}"

        except Exception as e:
            logger.error(f"launch_app failed: {e}")
            return False, str(e)

    def stop_app(self, package: str) -> Tuple[bool, str]:
        """Stop app."""
        self._ensure_connected()
        try:
            self.device.app_stop(package)
            return True, f"Stopped {package}"
        except Exception as e:
            return False, str(e)

    def current_app(self) -> Optional[Dict]:
        """Get current foreground app info."""
        self._ensure_connected()
        try:
            return self.device.app_current()
        except Exception:
            return None

    # =========================================================================
    # Button Operations
    # =========================================================================

    def press_back(self) -> Tuple[bool, str]:
        """Press back button."""
        self._ensure_connected()
        try:
            self.device.press("back")
            return True, "Pressed back"
        except Exception as e:
            return False, str(e)

    def press_home(self) -> Tuple[bool, str]:
        """Press home button."""
        self._ensure_connected()
        try:
            self.device.press("home")
            return True, "Pressed home"
        except Exception as e:
            return False, str(e)

    def press_enter(self) -> Tuple[bool, str]:
        """Press enter key."""
        self._ensure_connected()
        try:
            self.device.press("enter")
            return True, "Pressed enter"
        except Exception as e:
            return False, str(e)

    # =========================================================================
    # Screen Operations
    # =========================================================================

    def screenshot(self, save_path: str = None) -> Optional[str]:
        """
        Take screenshot.

        Args:
            save_path: Path to save (auto-generated if None)

        Returns:
            Path to saved screenshot
        """
        self._ensure_connected()
        try:
            if save_path is None:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_dir = os.path.join(PROJECT_ROOT, "temp", "screenshots")
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"u2_{timestamp}.png")

            self.device.screenshot(save_path)
            logger.info(f"Screenshot saved: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"screenshot failed: {e}")
            return None

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size (width, height)."""
        self._ensure_connected()
        try:
            info = self.device.info
            return info['displayWidth'], info['displayHeight']
        except Exception:
            return (0, 0)

    # =========================================================================
    # Element Inspection
    # =========================================================================

    def dump_hierarchy(self, compressed: bool = True) -> Optional[str]:
        """
        Dump UI hierarchy XML.

        Returns:
            XML string of UI hierarchy
        """
        self._ensure_connected()
        try:
            return self.device.dump_hierarchy(compressed=compressed)
        except Exception as e:
            logger.error(f"dump_hierarchy failed: {e}")
            return None

    def find_elements(self, **selector) -> List[U2Element]:
        """
        Find all elements matching selector.

        Returns:
            List of U2Element
        """
        self._ensure_connected()
        elements = []
        try:
            for el in self.device(**selector):
                info = el.info
                elements.append(U2Element(
                    text=info.get('text', ''),
                    resource_id=info.get('resourceId', ''),
                    description=info.get('contentDescription', ''),
                    class_name=info.get('className', ''),
                    bounds=info.get('bounds'),
                    clickable=info.get('clickable', False),
                    enabled=info.get('enabled', True)
                ))
        except Exception as e:
            logger.error(f"find_elements failed: {e}")

        return elements

    def exists(self, **selector) -> bool:
        """Check if element exists."""
        self._ensure_connected()
        try:
            return self.device(**selector).exists
        except Exception:
            return False


# =============================================================================
# Factory Function
# =============================================================================

def get_u2_driver(device_serial: str = None) -> Optional[U2Driver]:
    """
    Get U2Driver instance (returns None if uiautomator2 not available).

    Usage:
        driver = get_u2_driver()
        if driver:
            driver.click_by_text("Search")
    """
    if not U2_AVAILABLE:
        return None
    try:
        return U2Driver(device_serial)
    except Exception as e:
        logger.error(f"Failed to create U2Driver: {e}")
        return None


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print("=== U2Driver Test ===\n")

    if not U2_AVAILABLE:
        print("uiautomator2 not installed. Run: pip install uiautomator2")
        sys.exit(1)

    driver = get_u2_driver()
    if not driver:
        print("Failed to connect to device")
        sys.exit(1)

    print(f"1. Connected: {driver.connected}")
    print(f"2. Device: {driver.device_serial}")
    print(f"3. Screen size: {driver.get_screen_size()}")

    # Test current app
    app = driver.current_app()
    print(f"4. Current app: {app}")

    # Test element finding
    print("\n5. Finding clickable elements...")
    elements = driver.find_elements(clickable=True)
    print(f"   Found {len(elements)} clickable elements")
    for el in elements[:3]:
        print(f"   - {el.text or el.resource_id or el.class_name}")

    print("\n=== Test Complete ===")
