#!/usr/bin/env python3
"""
Patrol State Machine - Automated social media browsing with state machine control.

This module implements a reliable "patrol" pattern for browsing social media:
1. Search keyword
2. Scan results
3. Open post → Read → Check comments → Back
4. Repeat until budget exhausted

Key features:
- State machine for reliable navigation
- Visited tracking to avoid duplicates
- Budget management (max posts, scrolls, time)
- Automatic recovery from errors

Usage:
    from src.patrol import PatrolStateMachine, PatrolConfig

    config = PatrolConfig(max_posts=10, max_scrolls=5)
    patrol = PatrolStateMachine(platform="threads", config=config)

    report = patrol.run(keyword="AI agents")
    print(report.summary)
"""
import os
import sys
import time
import json
from typing import Optional, Dict, List, Tuple, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from logger import get_logger
from executor import DeterministicExecutor, ScreenState, Element, ExecutionResult, ActionResult
from tool_router import ToolRouter
from state_tracker import StateTracker, NavigationState, VisitedItem
from platform_adapter import get_adapter, PlatformAdapter, PostCard

logger = get_logger(__name__)

# Output directory
REPORTS_DIR = os.path.join(PROJECT_ROOT, "outputs", "patrol_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class PatrolConfig:
    """Configuration for patrol behavior"""
    # Budget limits
    max_posts: int = 10          # Maximum posts to visit
    max_scrolls: int = 5         # Maximum scroll rounds
    max_time_minutes: int = 30   # Maximum time limit
    max_consecutive_errors: int = 3  # Errors before stopping

    # Per-post behavior
    comments_per_post: int = 10  # Comments to read per post
    comment_scrolls: int = 2     # Scroll times in comments

    # Timing
    wait_after_search: float = 2.0    # Wait after search submit
    wait_after_click: float = 1.0     # Wait after clicking post
    wait_after_scroll: float = 1.0    # Wait after scroll
    wait_after_back: float = 1.0      # Wait after back navigation

    # Behavior flags
    verify_actions: bool = True       # Verify each action
    skip_without_comments: bool = False  # Skip posts without comments
    save_screenshots: bool = False    # Save screenshots of each post
    auto_save_report: bool = True     # Auto-save report on completion


@dataclass
class PostData:
    """Data collected from a single post"""
    title: str = ""
    author: str = ""
    content: str = ""
    engagement: Dict = field(default_factory=dict)  # likes, comments, shares
    comments: List[Dict] = field(default_factory=list)
    timestamp: str = ""
    url: str = ""
    screenshot_path: str = ""
    metadata: Dict = field(default_factory=dict)


@dataclass
class PatrolReport:
    """Complete patrol report"""
    keyword: str
    platform: str
    start_time: float
    end_time: float = 0.0
    posts: List[PostData] = field(default_factory=list)
    stats: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time else 0.0

    @property
    def summary(self) -> str:
        """Generate summary text"""
        lines = [
            f"# Patrol Report: {self.keyword}",
            f"Platform: {self.platform}",
            f"Duration: {self.duration:.1f}s",
            f"Posts visited: {len(self.posts)}",
            "",
            "## Key Findings",
        ]

        for i, post in enumerate(self.posts[:5], 1):
            lines.append(f"\n### {i}. {post.author}")
            if post.content:
                lines.append(f"{post.content[:200]}...")
            if post.engagement:
                lines.append(f"Engagement: {post.engagement}")

        if self.errors:
            lines.append(f"\n## Errors ({len(self.errors)})")
            for err in self.errors[:5]:
                lines.append(f"- {err}")

        return "\n".join(lines)


# =============================================================================
# Patrol State
# =============================================================================

class PatrolState(Enum):
    """Internal patrol states"""
    INIT = "init"
    LAUNCHING_APP = "launching_app"
    FINDING_SEARCH = "finding_search"
    TYPING_QUERY = "typing_query"
    VIEWING_RESULTS = "viewing_results"
    ENTERING_POST = "entering_post"
    READING_POST = "reading_post"
    ENTERING_COMMENTS = "entering_comments"
    READING_COMMENTS = "reading_comments"
    RETURNING_TO_POST = "returning_to_post"
    RETURNING_TO_RESULTS = "returning_to_results"
    SCROLLING_RESULTS = "scrolling_results"
    COMPLETED = "completed"
    STOPPED = "stopped"
    ERROR = "error"


# =============================================================================
# Platform Patterns
# =============================================================================

# Search element patterns by platform
SEARCH_PATTERNS: Dict[str, Dict] = {
    "threads": {
        "search_icon": {"identifier": "search", "position": "top_right"},
        "search_input": {"type": "EditText", "text": "Search"},
        "search_submit": {"button": "ENTER"},
    },
    "instagram": {
        "search_tab": {"identifier": "search_tab", "text": "Search"},
        "search_input": {"type": "EditText"},
        "search_submit": {"button": "ENTER"},
    },
    "tiktok": {
        "search_icon": {"identifier": "search"},
        "search_input": {"type": "EditText"},
        "search_submit": {"button": "ENTER"},
    },
    "x": {
        "search_icon": {"identifier": "search"},
        "search_input": {"type": "EditText"},
        "search_submit": {"button": "ENTER"},
    },
    "youtube": {
        "search_icon": {"identifier": "search"},
        "search_input": {"type": "EditText"},
        "search_submit": {"button": "ENTER"},
    },
    "default": {
        "search_input": {"type": "EditText", "text": "search"},
        "search_submit": {"button": "ENTER"},
    }
}

# Package names
PACKAGE_NAMES: Dict[str, str] = {
    "threads": "com.instagram.barcelona",
    "instagram": "com.instagram.android",
    "tiktok": "com.zhiliaoapp.musically",
    "x": "com.twitter.android",
    "twitter": "com.twitter.android",
    "facebook": "com.facebook.katana",
    "youtube": "com.google.android.youtube",
}


# =============================================================================
# Patrol State Machine
# =============================================================================

class PatrolStateMachine:
    """
    State machine for automated social media patrol.

    Implements reliable browse-and-collect pattern:
    INIT → SEARCH → RESULTS → POST → COMMENTS → (back) → RESULTS → ...

    Features:
    - State-based navigation with verification
    - Visited tracking to avoid duplicates
    - Budget management (time, posts, scrolls)
    - Automatic error recovery
    """

    def __init__(self, platform: str = "threads", config: PatrolConfig = None,
                 device_id: str = None):
        """
        Initialize patrol state machine.

        Args:
            platform: Target platform (threads, instagram, tiktok, etc.)
            config: Patrol configuration
            device_id: Device serial (auto-detect if None)
        """
        self.platform = platform.lower()
        self.config = config or PatrolConfig()
        self.device_id = device_id

        # Core components
        self.executor = DeterministicExecutor(device_id)
        self.router = ToolRouter(device_id)
        self.tracker = StateTracker(platform=platform)

        # Platform adapter (unified interface for platform-specific logic)
        self.adapter = get_adapter(platform)

        # State
        self.state = PatrolState.INIT
        self.keyword = ""
        self.report = None

        # Tracking
        self.posts_collected: List[PostData] = []
        self.current_post: Optional[PostData] = None
        self.scroll_count = 0
        self.error_count = 0
        self.start_time = 0.0

        # Platform config (use adapter)
        self.package = self.adapter.package_name
        self.patterns = SEARCH_PATTERNS.get(platform, SEARCH_PATTERNS["default"])

        logger.info(f"Patrol initialized: platform={platform}, package={self.package}, adapter={type(self.adapter).__name__}")

    # =========================================================================
    # Main Entry Point
    # =========================================================================

    def run(self, keyword: str, package: str = None) -> PatrolReport:
        """
        Run the patrol.

        Args:
            keyword: Search keyword
            package: App package (uses platform default if None)

        Returns:
            PatrolReport with collected data
        """
        self.keyword = keyword
        self.package = package or self.package
        self.start_time = time.time()
        self.state = PatrolState.INIT

        # Initialize report
        self.report = PatrolReport(
            keyword=keyword,
            platform=self.platform,
            start_time=self.start_time
        )

        logger.info(f"Starting patrol: keyword='{keyword}', platform={self.platform}")

        try:
            # Launch app
            if not self._launch_app():
                return self._finalize_report("Failed to launch app")

            # Find and execute search
            if not self._do_search():
                return self._finalize_report("Failed to search")

            # Main patrol loop
            self._patrol_loop()

        except Exception as e:
            logger.error(f"Patrol error: {e}")
            self.report.errors.append(f"Fatal error: {str(e)}")
            self.state = PatrolState.ERROR

        return self._finalize_report()

    # =========================================================================
    # Launch and Search
    # =========================================================================

    def _launch_app(self) -> bool:
        """Launch target app"""
        if not self.package:
            self.report.errors.append("No package specified")
            return False

        self.state = PatrolState.LAUNCHING_APP
        logger.info(f"Launching {self.package}...")

        ok, msg = self.router.launch_app(self.package, wait=3.0)
        if not ok:
            self.report.errors.append(f"Launch failed: {msg}")
            return False

        # Verify app launched
        time.sleep(1)
        current = self.router.get_current_package()
        if current and self.package.split('.')[-1] in current:
            logger.info(f"App launched: {current}")
            return True

        # Try again
        time.sleep(2)
        return True  # Proceed anyway, might work

    def _do_search(self) -> bool:
        """Execute search flow using platform adapter"""
        self.state = PatrolState.FINDING_SEARCH

        # Find search icon/input using adapter
        search_found = False
        for attempt in range(3):
            state = self.executor.observe()

            # Use adapter to find search input directly
            search_input = self.adapter.find_search_input(state.elements)
            if search_input:
                logger.info(f"Found search input via {type(self.adapter).__name__}")
                ok, _ = self.router.click(element=search_input)
                if ok:
                    search_found = True
                    break

            # Use adapter to find search entry (icon/tab)
            search_entry = self.adapter.find_search_entry(state.elements)
            if search_entry:
                logger.info(f"Found search entry via {type(self.adapter).__name__}")
                ok, _ = self.router.click(element=search_entry)
                if ok:
                    time.sleep(1)
                    # After clicking entry, look for input again
                    state = self.executor.observe()
                    search_input = self.adapter.find_search_input(state.elements)
                    if search_input:
                        self.router.click(element=search_input, verify=False)
                    search_found = True
                    break

            # Fallback: platform-specific hardcoded positions
            if self.platform == "threads":
                w, h = self.router.screen_size
                self.router.click(x=w - 80, y=120, verify=False)
                time.sleep(1)
                search_found = True
                break

            time.sleep(1)

        if not search_found:
            self.report.errors.append("Could not find search")
            return False

        # Type query
        self.state = PatrolState.TYPING_QUERY
        time.sleep(0.5)

        ok, _ = self.router.type_text(self.keyword, submit=True)
        if not ok:
            self.report.errors.append("Failed to type search query")
            return False

        # Wait for results
        time.sleep(self.config.wait_after_search)
        self.state = PatrolState.VIEWING_RESULTS

        # Verify results appeared using adapter
        state = self.executor.observe()
        if self.adapter.is_search_results(state.elements):
            logger.info("Search results verified via adapter")
        else:
            logger.warning("Could not verify search results, continuing anyway")

        self.tracker.detect_state(state.elements)
        logger.info("Search completed, viewing results")
        return True

    # =========================================================================
    # Main Patrol Loop
    # =========================================================================

    def _patrol_loop(self):
        """Main patrol loop: scan results, visit posts, collect data"""
        while self._should_continue():
            try:
                # Scan current results
                posts = self._scan_visible_posts()

                if not posts:
                    # No posts found, try scrolling
                    if self.scroll_count < self.config.max_scrolls:
                        self._scroll_results()
                        continue
                    else:
                        logger.info("No more posts to visit, stopping")
                        break

                # Find unvisited post
                unvisited = self._find_unvisited_post(posts)

                if unvisited:
                    # Visit the post
                    self._visit_post(unvisited)
                else:
                    # All visible posts visited, scroll for more
                    if self.scroll_count < self.config.max_scrolls:
                        self._scroll_results()
                    else:
                        logger.info("All posts visited, stopping")
                        break

            except Exception as e:
                logger.error(f"Loop error: {e}")
                self.error_count += 1
                if self.error_count >= self.config.max_consecutive_errors:
                    self.report.errors.append(f"Too many errors: {e}")
                    break

        self.state = PatrolState.COMPLETED

    def _should_continue(self) -> bool:
        """Check if patrol should continue"""
        # Budget checks
        if len(self.posts_collected) >= self.config.max_posts:
            logger.info(f"Reached max posts: {self.config.max_posts}")
            return False

        elapsed = (time.time() - self.start_time) / 60
        if elapsed >= self.config.max_time_minutes:
            logger.info(f"Reached time limit: {self.config.max_time_minutes}m")
            return False

        if self.error_count >= self.config.max_consecutive_errors:
            logger.warning("Too many consecutive errors")
            return False

        # State check
        if self.state in (PatrolState.COMPLETED, PatrolState.STOPPED, PatrolState.ERROR):
            return False

        return True

    # =========================================================================
    # Post Operations
    # =========================================================================

    def _scan_visible_posts(self) -> List[Dict]:
        """Scan visible posts from current screen using platform adapter"""
        state = self.executor.observe()

        # Use adapter for platform-specific post extraction
        post_cards = self.adapter.extract_post_cards(state.elements)

        # Convert PostCard to dict format (for backward compatibility)
        posts = []
        for card in post_cards:
            posts.append({
                "element": card.element,
                "text": card.text,
                "author": card.author_id or card.author,
                "bounds": card.bounds,
                "id": card.unique_id,
                "card": card  # Keep original PostCard for richer data
            })

        logger.debug(f"Found {len(posts)} potential posts via {type(self.adapter).__name__}")
        return posts

    def _extract_author(self, element: Element) -> str:
        """Extract author from element (heuristic)"""
        text = element.text or element.content_desc
        if '@' in text:
            # Find @username pattern
            import re
            match = re.search(r'@[\w.]+', text)
            if match:
                return match.group(0)
        return text[:30] if text else "unknown"

    def _generate_post_id(self, element: Element) -> str:
        """Generate unique ID for post element"""
        import hashlib
        data = f"{element.text}|{element.identifier}|{element.bounds}"
        return hashlib.md5(data.encode()).hexdigest()[:16]

    def _find_unvisited_post(self, posts: List[Dict]) -> Optional[Dict]:
        """Find first unvisited post"""
        for post in posts:
            if not self.tracker.is_visited(item_id=post["id"]):
                return post
        return None

    def _visit_post(self, post: Dict):
        """Visit a single post: click → read → comments → back"""
        post_id = post["id"]
        element = post["element"]

        logger.info(f"Visiting post: {post['text'][:50] if post['text'] else post_id[:8]}")
        self.state = PatrolState.ENTERING_POST

        # Save state before navigation
        current_state = self.executor.observe()
        self.tracker.push_history(current_state.screen_hash, {"state": "results"})

        # Click post
        result = self.executor.click_and_verify(element)
        if result.result == ActionResult.NO_CHANGE:
            logger.warning("Post click had no effect, skipping")
            self.tracker.mark_visited(item_id=post_id, title=post.get("text", ""))
            return

        time.sleep(self.config.wait_after_click)
        self.state = PatrolState.READING_POST

        # Collect post data
        self.current_post = self._collect_post_data(post)

        # Read comments if available
        if self.config.comments_per_post > 0:
            self._read_post_comments()

        # Mark as visited
        self.tracker.mark_visited(
            item_id=post_id,
            title=self.current_post.title,
            author=self.current_post.author
        )

        # Add to collected posts
        self.posts_collected.append(self.current_post)
        self.error_count = 0  # Reset error count on success

        # Back to results
        self._back_to_results()

    def _collect_post_data(self, post: Dict) -> PostData:
        """Collect data from current post view"""
        state = self.executor.observe()

        # Extract visible text
        all_text = []
        for el in state.elements:
            if el.text:
                all_text.append(el.text)

        # Find engagement (likes, comments, shares)
        engagement = {}
        for el in state.elements:
            text = (el.text or el.content_desc or "").lower()
            if 'like' in text or '讚' in text:
                engagement['likes'] = el.text
            elif 'comment' in text or '留言' in text or 'repl' in text:
                engagement['comments'] = el.text
            elif 'share' in text or '分享' in text:
                engagement['shares'] = el.text

        return PostData(
            title=post.get("text", "")[:200],
            author=post.get("author", ""),
            content="\n".join(all_text[:10]),
            engagement=engagement,
            timestamp=datetime.now().isoformat(),
            metadata={"post_id": post.get("id")}
        )

    def _read_post_comments(self):
        """Read comments on current post"""
        self.state = PatrolState.ENTERING_COMMENTS

        # Find comments section
        state = self.executor.observe()
        comments_el = (
            state.find(text="comment") or
            state.find(text="留言") or
            state.find(text="repl") or
            state.find(text="回覆")
        )

        if not comments_el:
            logger.debug("No comments section found")
            return

        # Click to open comments
        result = self.executor.click_and_verify(comments_el)
        if result.result == ActionResult.NO_CHANGE:
            logger.debug("Comments click had no effect")
            return

        time.sleep(self.config.wait_after_click)
        self.state = PatrolState.READING_COMMENTS

        # Save state for back navigation
        current = self.executor.observe()
        self.tracker.push_history(current.screen_hash, {"state": "post_detail"})

        # Scroll and collect comments
        comments = []
        for i in range(self.config.comment_scrolls):
            state = self.executor.observe()

            # Extract comment-like text
            for el in state.elements:
                if el.text and len(el.text) > 10:
                    comments.append({
                        "text": el.text,
                        "author": self._extract_author(el)
                    })

            # Scroll for more comments
            self.router.swipe("up", verify=False)
            time.sleep(self.config.wait_after_scroll)

            if len(comments) >= self.config.comments_per_post:
                break

        # Update current post data
        if self.current_post:
            self.current_post.comments = comments[:self.config.comments_per_post]

        # Back to post
        self.state = PatrolState.RETURNING_TO_POST
        self.router.back(verify=True)
        time.sleep(self.config.wait_after_back)
        self.tracker.pop_history()

    def _back_to_results(self):
        """Navigate back to results list"""
        self.state = PatrolState.RETURNING_TO_RESULTS

        # Try back navigation
        result = self.executor.back_and_verify()

        if result.result == ActionResult.NO_CHANGE:
            # Try again
            time.sleep(0.5)
            self.router.back(verify=False)

        time.sleep(self.config.wait_after_back)
        self.tracker.pop_history()
        self.state = PatrolState.VIEWING_RESULTS

        logger.debug("Returned to results")

    def _scroll_results(self):
        """Scroll to load more results"""
        self.state = PatrolState.SCROLLING_RESULTS
        logger.debug(f"Scrolling results (scroll #{self.scroll_count + 1})")

        self.router.swipe("up")
        self.scroll_count += 1
        self.tracker.record_scroll()

        time.sleep(self.config.wait_after_scroll)
        self.state = PatrolState.VIEWING_RESULTS

    # =========================================================================
    # Report Generation
    # =========================================================================

    def _finalize_report(self, error_msg: str = None) -> PatrolReport:
        """Finalize and optionally save report"""
        self.report.end_time = time.time()
        self.report.posts = self.posts_collected
        self.report.stats = {
            "posts_visited": len(self.posts_collected),
            "scrolls": self.scroll_count,
            "duration_seconds": self.report.duration,
            "errors": len(self.report.errors),
            **self.tracker.get_stats()
        }

        if error_msg:
            self.report.errors.append(error_msg)

        # Save report
        if self.config.auto_save_report:
            self._save_report()

        # Save tracker state
        self.tracker.save()

        logger.info(f"Patrol completed: {len(self.posts_collected)} posts, {self.scroll_count} scrolls")
        return self.report

    def _save_report(self):
        """Save report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"patrol_{self.platform}_{timestamp}.json"
        filepath = os.path.join(REPORTS_DIR, filename)

        data = {
            "keyword": self.report.keyword,
            "platform": self.report.platform,
            "start_time": self.report.start_time,
            "end_time": self.report.end_time,
            "duration": self.report.duration,
            "posts": [asdict(p) for p in self.report.posts],
            "stats": self.report.stats,
            "errors": self.report.errors
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Report saved: {filepath}")

    # =========================================================================
    # Control Methods
    # =========================================================================

    def stop(self):
        """Stop the patrol"""
        logger.info("Patrol stop requested")
        self.state = PatrolState.STOPPED

    def get_progress(self) -> Dict:
        """Get current progress"""
        return {
            "state": self.state.value,
            "posts_collected": len(self.posts_collected),
            "posts_target": self.config.max_posts,
            "scrolls": self.scroll_count,
            "scrolls_max": self.config.max_scrolls,
            "elapsed_seconds": time.time() - self.start_time if self.start_time else 0,
            "errors": self.error_count
        }


# =============================================================================
# Convenience Functions
# =============================================================================

def patrol(keyword: str, platform: str = "threads", max_posts: int = 10,
           max_scrolls: int = 5) -> PatrolReport:
    """
    Quick patrol function.

    Args:
        keyword: Search keyword
        platform: Target platform
        max_posts: Maximum posts to visit
        max_scrolls: Maximum scroll rounds

    Returns:
        PatrolReport with collected data
    """
    config = PatrolConfig(max_posts=max_posts, max_scrolls=max_scrolls)
    machine = PatrolStateMachine(platform=platform, config=config)
    return machine.run(keyword)


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print("=== Patrol State Machine Test ===\n")

    # Create config
    config = PatrolConfig(
        max_posts=3,
        max_scrolls=2,
        max_time_minutes=5
    )
    print(f"1. Config: max_posts={config.max_posts}, max_scrolls={config.max_scrolls}")

    # Create patrol machine (without running)
    machine = PatrolStateMachine(platform="threads", config=config)
    print(f"2. Created machine: state={machine.state.value}")

    # Test state transitions
    machine.state = PatrolState.VIEWING_RESULTS
    print(f"3. State transition: {machine.state.value}")

    # Test should_continue
    machine.start_time = time.time()
    machine.posts_collected = []
    print(f"4. Should continue: {machine._should_continue()}")

    # Test progress
    progress = machine.get_progress()
    print(f"5. Progress: {progress}")

    print("\n=== Test Complete ===")
    print("Note: Full patrol test requires connected device and app installed")
