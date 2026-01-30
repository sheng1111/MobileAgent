#!/usr/bin/env python3
"""
MCP Macro Server - High-level automation tools for AI agents.

This server provides macro tools that combine multiple steps into single operations,
reducing LLM round-trips and improving reliability.

Key advantages:
- find_and_click: Element search + click + verify in one call
- type_and_submit: Focus + type + submit in one call
- smart_wait: Wait for element with built-in retry logic
- patrol: Complete social media browsing automation

Usage:
    # Start server
    python -m src.mcp_macro_server

    # Or via uvx
    uvx --from . mcp-macro-server

MCP Configuration:
    {
      "mcpServers": {
        "mobile-macro": {
          "command": "python",
          "args": ["-m", "src.mcp_macro_server"]
        }
      }
    }
"""
import os
import sys
import json
import asyncio
from typing import Optional, Dict, List, Any

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from logger import get_logger

logger = get_logger(__name__)

# Try to import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP SDK not installed. Run: pip install mcp")

# Import our modules
from tool_router import ToolRouter
from executor import DeterministicExecutor, ActionResult
from state_tracker import StateTracker

# Global instances (initialized on first use)
_router: Optional[ToolRouter] = None
_executor: Optional[DeterministicExecutor] = None


def get_router() -> ToolRouter:
    """Get or create ToolRouter instance"""
    global _router
    if _router is None:
        _router = ToolRouter()
    return _router


def get_executor() -> DeterministicExecutor:
    """Get or create DeterministicExecutor instance"""
    global _executor
    if _executor is None:
        _executor = DeterministicExecutor()
    return _executor


# =============================================================================
# Macro Tool Implementations
# =============================================================================

def find_and_click(
    text: str = None,
    resource_id: str = None,
    description: str = None,
    class_name: str = None,
    timeout: float = 5.0,
    verify: bool = True,
    retry: int = 2
) -> Dict[str, Any]:
    """
    Find element and click it in one operation.

    This combines: observe → find → click → verify into a single call.

    Args:
        text: Text to find (partial match)
        resource_id: Resource ID (e.g., "com.app:id/button")
        description: Content description
        class_name: Class name (e.g., "android.widget.Button")
        timeout: Wait timeout for element
        verify: Verify screen changed after click
        retry: Number of retries on failure

    Returns:
        {"success": bool, "message": str, "element": {...} or None}
    """
    router = get_router()

    for attempt in range(retry + 1):
        # Try U2 selector-based click first (most reliable)
        if router.u2_available:
            selector = {}
            if text:
                selector['textContains'] = text
            if resource_id:
                selector['resourceId'] = resource_id
            if description:
                selector['descriptionContains'] = description
            if class_name:
                selector['className'] = class_name

            if selector:
                ok, msg = router.click_by_selector(timeout=timeout, **selector)
                if ok:
                    return {
                        "success": True,
                        "message": f"Clicked via u2 selector: {msg}",
                        "method": "u2_selector"
                    }

        # Fallback to coordinate-based click
        ok, msg = router.click(
            text=text,
            identifier=resource_id,
            element_type=class_name,
            verify=verify
        )

        if ok:
            return {
                "success": True,
                "message": msg,
                "method": "coordinate"
            }

        if attempt < retry:
            logger.debug(f"Retry {attempt + 1}/{retry}: {msg}")
            import time
            time.sleep(0.5)

    return {
        "success": False,
        "message": f"Failed after {retry + 1} attempts: {msg}",
        "method": None
    }


def type_and_submit(
    text: str,
    input_text: str = None,
    input_id: str = None,
    clear_first: bool = True,
    submit: bool = True,
    submit_delay: float = 0.3
) -> Dict[str, Any]:
    """
    Type text into input field and optionally submit.

    This combines: find input → click → clear → type → submit

    Args:
        text: Text to type
        input_text: Text/hint of input field to find
        input_id: Resource ID of input field
        clear_first: Clear existing text before typing
        submit: Press Enter after typing
        submit_delay: Delay before submit (seconds)

    Returns:
        {"success": bool, "message": str}
    """
    router = get_router()
    import time

    # Find and click input field if specified
    if input_text or input_id:
        if router.u2_available:
            selector = {}
            if input_id:
                selector['resourceId'] = input_id
            elif input_text:
                selector['textContains'] = input_text

            ok, msg = router.type_into_element(text, clear_first=clear_first, **selector)
            if ok:
                if submit:
                    time.sleep(submit_delay)
                    router.u2.press_enter()
                return {"success": True, "message": "Typed and submitted via u2"}
        else:
            # Fallback: click then type
            ok, msg = router.click(text=input_text, identifier=input_id, verify=False)
            if not ok:
                return {"success": False, "message": f"Failed to find input: {msg}"}
            time.sleep(0.3)

    # Type text
    ok, msg = router.type_text(text, submit=submit)
    return {"success": ok, "message": msg}


def smart_wait(
    text: str = None,
    resource_id: str = None,
    gone: bool = False,
    timeout: float = 10.0
) -> Dict[str, Any]:
    """
    Wait for element to appear or disappear.

    Uses uiautomator2's native wait when available (more efficient than polling).

    Args:
        text: Text to wait for
        resource_id: Resource ID to wait for
        gone: If True, wait for element to disappear
        timeout: Maximum wait time

    Returns:
        {"success": bool, "found": bool, "message": str}
    """
    router = get_router()

    selector = {}
    if text:
        selector['textContains'] = text
    if resource_id:
        selector['resourceId'] = resource_id

    if not selector:
        return {"success": False, "found": False, "message": "No selector provided"}

    if router.u2_available:
        found, element = router.wait_for_element_u2(timeout=timeout, gone=gone, **selector)
    else:
        found, element = router.wait_for_element(timeout=timeout, **selector)

    action = "disappeared" if gone else "appeared"
    if found:
        return {
            "success": True,
            "found": not gone,
            "message": f"Element {action} within {timeout}s"
        }
    else:
        return {
            "success": False,
            "found": gone,
            "message": f"Timeout: element did not {action.replace('ed', '')} within {timeout}s"
        }


def scroll_and_find(
    text: str = None,
    resource_id: str = None,
    direction: str = "up",
    max_scrolls: int = 5
) -> Dict[str, Any]:
    """
    Scroll until element is found.

    Args:
        text: Text to find
        resource_id: Resource ID to find
        direction: Scroll direction ("up", "down")
        max_scrolls: Maximum scroll attempts

    Returns:
        {"success": bool, "scrolls": int, "element": {...} or None}
    """
    router = get_router()

    selector = {}
    if text:
        selector['text'] = text
    if resource_id:
        selector['resourceId'] = resource_id

    if router.u2_available:
        found, element = router.scroll_to_element(
            max_scrolls=max_scrolls,
            direction=direction,
            **selector
        )
        if found:
            return {
                "success": True,
                "message": f"Found element after scrolling",
                "element": {"text": element.text if element else text}
            }
    else:
        # Fallback: manual scroll loop
        for i in range(max_scrolls):
            if router.has_text(text or ""):
                return {
                    "success": True,
                    "scrolls": i,
                    "message": f"Found after {i} scrolls"
                }
            router.swipe(direction, verify=False)
            import time
            time.sleep(0.8)

        # Final check
        if router.has_text(text or ""):
            return {"success": True, "scrolls": max_scrolls, "message": "Found"}

    return {
        "success": False,
        "scrolls": max_scrolls,
        "message": f"Not found after {max_scrolls} scrolls"
    }


def navigate_back(
    expected_text: str = None,
    max_attempts: int = 3
) -> Dict[str, Any]:
    """
    Press back and verify navigation.

    Args:
        expected_text: Text expected on previous screen
        max_attempts: Maximum back press attempts

    Returns:
        {"success": bool, "attempts": int, "message": str}
    """
    router = get_router()
    executor = get_executor()
    import time

    for attempt in range(max_attempts):
        result = executor.back_and_verify(expected_text)

        if result.result == ActionResult.SUCCESS:
            return {
                "success": True,
                "attempts": attempt + 1,
                "message": "Back navigation verified"
            }

        if expected_text and router.has_text(expected_text):
            return {
                "success": True,
                "attempts": attempt + 1,
                "message": f"Found expected text: {expected_text}"
            }

        time.sleep(0.5)

    return {
        "success": False,
        "attempts": max_attempts,
        "message": "Back navigation failed"
    }


def dismiss_popup(
    button_texts: List[str] = None,
    timeout: float = 2.0
) -> Dict[str, Any]:
    """
    Dismiss popup/dialog by clicking common buttons.

    Args:
        button_texts: Button texts to try (default: common dismiss buttons)
        timeout: Timeout for each button search

    Returns:
        {"success": bool, "dismissed": bool, "button": str or None}
    """
    router = get_router()

    if button_texts is None:
        button_texts = [
            "OK", "Cancel", "Close", "Dismiss", "Got it", "Not now",
            "Skip", "Later", "No thanks", "Allow", "Deny",
            "確定", "取消", "關閉", "略過", "稍後", "允許", "拒絕"
        ]

    for btn_text in button_texts:
        if router.u2_available:
            if router.click_if_exists(timeout=timeout, text=btn_text):
                return {
                    "success": True,
                    "dismissed": True,
                    "button": btn_text
                }
        else:
            # Fallback: check if text exists then click
            if router.has_text(btn_text):
                ok, _ = router.click(text=btn_text, verify=False)
                if ok:
                    return {
                        "success": True,
                        "dismissed": True,
                        "button": btn_text
                    }

    return {
        "success": True,
        "dismissed": False,
        "button": None,
        "message": "No popup detected or no matching buttons found"
    }


def launch_and_wait(
    package: str,
    wait_text: str = None,
    timeout: float = 10.0
) -> Dict[str, Any]:
    """
    Launch app and wait for it to be ready.

    Args:
        package: App package name
        wait_text: Text to wait for after launch (indicates app ready)
        timeout: Maximum wait time

    Returns:
        {"success": bool, "message": str}
    """
    router = get_router()
    import time

    # Launch app
    ok, msg = router.launch_app(package, wait=2.0)
    if not ok:
        return {"success": False, "message": f"Launch failed: {msg}"}

    # Wait for ready indicator
    if wait_text:
        start = time.time()
        while time.time() - start < timeout:
            if router.has_text(wait_text):
                return {
                    "success": True,
                    "message": f"App ready (found: {wait_text})"
                }
            time.sleep(0.5)

        return {
            "success": False,
            "message": f"App launched but '{wait_text}' not found within {timeout}s"
        }

    return {"success": True, "message": f"Launched {package}"}


def get_screen_summary() -> Dict[str, Any]:
    """
    Get a summary of current screen state.

    Returns:
        {
            "success": bool,
            "package": str,
            "element_count": int,
            "clickable_count": int,
            "texts": [str],
            "buttons": [str]
        }
    """
    router = get_router()
    executor = get_executor()

    state = executor.observe()
    package = router.get_current_package()

    # Extract useful info
    texts = []
    buttons = []
    clickable_count = 0

    for el in state.elements:
        if el.text:
            texts.append(el.text)
        if el.clickable:
            clickable_count += 1
            if el.text:
                buttons.append(el.text)

    return {
        "success": True,
        "package": package,
        "element_count": len(state.elements),
        "clickable_count": clickable_count,
        "screen_hash": state.screen_hash,
        "texts": texts[:20],  # Limit to avoid huge responses
        "buttons": buttons[:15]
    }


def run_patrol(
    keyword: str,
    platform: str = "threads",
    max_posts: int = 5,
    max_scrolls: int = 3,
    max_time_minutes: int = 10
) -> Dict[str, Any]:
    """
    Run automated social media patrol.

    This executes the complete patrol flow:
    1. Launch app
    2. Search keyword
    3. Browse results
    4. Visit posts and collect data
    5. Return report

    Args:
        keyword: Search keyword
        platform: Platform name (threads, instagram, tiktok, x, youtube)
        max_posts: Maximum posts to visit
        max_scrolls: Maximum scroll rounds
        max_time_minutes: Time limit in minutes

    Returns:
        {
            "success": bool,
            "posts_visited": int,
            "summary": str,
            "errors": [str]
        }
    """
    try:
        from patrol import PatrolStateMachine, PatrolConfig

        config = PatrolConfig(
            max_posts=max_posts,
            max_scrolls=max_scrolls,
            max_time_minutes=max_time_minutes
        )

        patrol = PatrolStateMachine(platform=platform, config=config)
        report = patrol.run(keyword)

        return {
            "success": len(report.errors) == 0 or len(report.posts) > 0,
            "posts_visited": len(report.posts),
            "duration_seconds": report.duration,
            "summary": report.summary,
            "errors": report.errors[:5]  # Limit errors
        }

    except Exception as e:
        logger.error(f"Patrol failed: {e}")
        return {
            "success": False,
            "posts_visited": 0,
            "summary": "",
            "errors": [str(e)]
        }


# =============================================================================
# MCP Server Definition
# =============================================================================

TOOLS = [
    {
        "name": "find_and_click",
        "description": "Find element by text/id/description and click it. Combines observe→find→click→verify into one call. Most reliable click method.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to find (partial match)"},
                "resource_id": {"type": "string", "description": "Resource ID (e.g., com.app:id/button)"},
                "description": {"type": "string", "description": "Content description"},
                "class_name": {"type": "string", "description": "Class name (e.g., android.widget.Button)"},
                "timeout": {"type": "number", "default": 5.0, "description": "Wait timeout"},
                "verify": {"type": "boolean", "default": True, "description": "Verify screen changed"},
                "retry": {"type": "integer", "default": 2, "description": "Retry count"}
            }
        }
    },
    {
        "name": "type_and_submit",
        "description": "Type text into input field and optionally submit. Combines find→click→clear→type→enter.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to type"},
                "input_text": {"type": "string", "description": "Text/hint of input field"},
                "input_id": {"type": "string", "description": "Resource ID of input field"},
                "clear_first": {"type": "boolean", "default": True},
                "submit": {"type": "boolean", "default": True, "description": "Press Enter after typing"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "smart_wait",
        "description": "Wait for element to appear or disappear. More efficient than polling.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to wait for"},
                "resource_id": {"type": "string", "description": "Resource ID to wait for"},
                "gone": {"type": "boolean", "default": False, "description": "Wait for disappearance"},
                "timeout": {"type": "number", "default": 10.0}
            }
        }
    },
    {
        "name": "scroll_and_find",
        "description": "Scroll until element is found.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to find"},
                "resource_id": {"type": "string", "description": "Resource ID to find"},
                "direction": {"type": "string", "enum": ["up", "down"], "default": "up"},
                "max_scrolls": {"type": "integer", "default": 5}
            }
        }
    },
    {
        "name": "navigate_back",
        "description": "Press back and verify navigation succeeded.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expected_text": {"type": "string", "description": "Text expected on previous screen"},
                "max_attempts": {"type": "integer", "default": 3}
            }
        }
    },
    {
        "name": "dismiss_popup",
        "description": "Dismiss popup/dialog by clicking common buttons (OK, Cancel, Close, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "button_texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Button texts to try (uses defaults if not provided)"
                },
                "timeout": {"type": "number", "default": 2.0}
            }
        }
    },
    {
        "name": "launch_and_wait",
        "description": "Launch app and wait for it to be ready.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "package": {"type": "string", "description": "App package name"},
                "wait_text": {"type": "string", "description": "Text indicating app is ready"},
                "timeout": {"type": "number", "default": 10.0}
            },
            "required": ["package"]
        }
    },
    {
        "name": "get_screen_summary",
        "description": "Get summary of current screen: package, element count, visible texts, clickable buttons.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "run_patrol",
        "description": "Run automated social media patrol: search keyword, browse results, visit posts, collect data.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "Search keyword"},
                "platform": {
                    "type": "string",
                    "enum": ["threads", "instagram", "tiktok", "x", "youtube", "facebook"],
                    "default": "threads"
                },
                "max_posts": {"type": "integer", "default": 5},
                "max_scrolls": {"type": "integer", "default": 3},
                "max_time_minutes": {"type": "integer", "default": 10}
            },
            "required": ["keyword"]
        }
    }
]


def create_mcp_server():
    """Create and configure MCP server"""
    if not MCP_AVAILABLE:
        raise ImportError("MCP SDK not installed. Run: pip install mcp")

    server = Server("mobile-macro")

    @server.list_tools()
    async def list_tools():
        return [Tool(**t) for t in TOOLS]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        """Handle tool calls"""
        try:
            if name == "find_and_click":
                result = find_and_click(**arguments)
            elif name == "type_and_submit":
                result = type_and_submit(**arguments)
            elif name == "smart_wait":
                result = smart_wait(**arguments)
            elif name == "scroll_and_find":
                result = scroll_and_find(**arguments)
            elif name == "navigate_back":
                result = navigate_back(**arguments)
            elif name == "dismiss_popup":
                result = dismiss_popup(**arguments)
            elif name == "launch_and_wait":
                result = launch_and_wait(**arguments)
            elif name == "get_screen_summary":
                result = get_screen_summary()
            elif name == "run_patrol":
                result = run_patrol(**arguments)
            else:
                result = {"success": False, "message": f"Unknown tool: {name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.error(f"Tool {name} failed: {e}")
            return [TextContent(
                type="text",
                text=json.dumps({"success": False, "error": str(e)})
            )]

    return server


async def main():
    """Run the MCP server"""
    if not MCP_AVAILABLE:
        print("MCP SDK not installed. Run: pip install mcp")
        print("\nYou can still use the macro functions directly:")
        print("  from src.mcp_macro_server import find_and_click, type_and_submit")
        return

    server = create_mcp_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


# =============================================================================
# CLI Interface (for direct use without MCP)
# =============================================================================

def cli_main():
    """CLI interface for testing macro tools"""
    import argparse

    parser = argparse.ArgumentParser(description="MobileAgent Macro Tools")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # find_and_click
    p = subparsers.add_parser("click", help="Find and click element")
    p.add_argument("--text", "-t", help="Text to find")
    p.add_argument("--id", "-i", help="Resource ID")
    p.add_argument("--timeout", type=float, default=5.0)

    # type_and_submit
    p = subparsers.add_parser("type", help="Type text")
    p.add_argument("text", help="Text to type")
    p.add_argument("--input", "-i", help="Input field text/hint")
    p.add_argument("--no-submit", action="store_true")

    # smart_wait
    p = subparsers.add_parser("wait", help="Wait for element")
    p.add_argument("--text", "-t", help="Text to wait for")
    p.add_argument("--gone", action="store_true", help="Wait for disappearance")
    p.add_argument("--timeout", type=float, default=10.0)

    # get_screen_summary
    subparsers.add_parser("screen", help="Get screen summary")

    # patrol
    p = subparsers.add_parser("patrol", help="Run patrol")
    p.add_argument("keyword", help="Search keyword")
    p.add_argument("--platform", "-p", default="threads")
    p.add_argument("--posts", type=int, default=5)

    args = parser.parse_args()

    if args.command == "click":
        result = find_and_click(text=args.text, resource_id=args.id, timeout=args.timeout)
    elif args.command == "type":
        result = type_and_submit(args.text, input_text=args.input, submit=not args.no_submit)
    elif args.command == "wait":
        result = smart_wait(text=args.text, gone=args.gone, timeout=args.timeout)
    elif args.command == "screen":
        result = get_screen_summary()
    elif args.command == "patrol":
        result = run_patrol(args.keyword, platform=args.platform, max_posts=args.posts)
    else:
        parser.print_help()
        return

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] != "--mcp":
        cli_main()
    else:
        asyncio.run(main())
