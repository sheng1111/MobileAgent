#!/usr/bin/env python3
"""
State Tracker - Navigation state machine and visited tracking for patrol automation.

This module provides:
1. Navigation state detection (SEARCH_RESULTS, POST_DETAIL, COMMENTS, etc.)
2. Visited tracking with persistence
3. Post deduplication via hashing
4. Navigation history for reliable back navigation

Usage:
    from src.state_tracker import StateTracker, NavigationState

    tracker = StateTracker(platform="threads")

    # Check current state
    state = tracker.detect_state(screen_elements)

    # Track visited posts
    tracker.mark_visited(post_id)
    if tracker.is_visited(post_id):
        skip_this_post()

    # Persist to disk
    tracker.save()
"""
import os
import sys
import json
import time
import hashlib
from typing import Optional, Dict, List, Set, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from logger import get_logger

logger = get_logger(__name__)

# Data directory
DATA_DIR = os.path.join(PROJECT_ROOT, "temp", "state_data")
os.makedirs(DATA_DIR, exist_ok=True)


# =============================================================================
# Navigation States
# =============================================================================

class NavigationState(Enum):
    """Navigation states for social media browsing"""
    UNKNOWN = "unknown"
    HOME_FEED = "home_feed"
    SEARCH_INPUT = "search_input"
    SEARCH_RESULTS = "search_results"
    POST_DETAIL = "post_detail"
    COMMENTS = "comments"
    PROFILE = "profile"
    SETTINGS = "settings"
    POPUP = "popup"
    LOGIN_WALL = "login_wall"
    ERROR = "error"


@dataclass
class StateSignal:
    """Signals that indicate a particular state"""
    texts: List[str] = field(default_factory=list)  # Text patterns to match
    element_types: List[str] = field(default_factory=list)  # Required element types
    identifiers: List[str] = field(default_factory=list)  # Resource ID patterns
    exclude_texts: List[str] = field(default_factory=list)  # Text that should NOT appear


# Platform-specific state detection rules
STATE_SIGNALS: Dict[str, Dict[NavigationState, StateSignal]] = {
    "threads": {
        NavigationState.SEARCH_INPUT: StateSignal(
            texts=["Search", "搜尋"],
            element_types=["EditText"],
        ),
        NavigationState.SEARCH_RESULTS: StateSignal(
            texts=["Top", "Recent", "Accounts", "熱門", "最新", "帳號"],
            exclude_texts=["Search", "搜尋"],  # Search input should not be visible
        ),
        NavigationState.POST_DETAIL: StateSignal(
            texts=["Reply", "回覆", "Like", "讚"],
            identifiers=["thread_view", "post_detail"],
        ),
        NavigationState.COMMENTS: StateSignal(
            texts=["replies", "則回覆"],
        ),
        NavigationState.HOME_FEED: StateSignal(
            element_types=["RecyclerView"],
            identifiers=["feed", "timeline"],
        ),
    },
    "instagram": {
        NavigationState.SEARCH_INPUT: StateSignal(
            texts=["Search", "搜尋"],
            element_types=["EditText"],
        ),
        NavigationState.SEARCH_RESULTS: StateSignal(
            texts=["Accounts", "Tags", "Places", "帳號", "標籤", "地點"],
        ),
        NavigationState.POST_DETAIL: StateSignal(
            texts=["Like", "Comment", "Share", "讚", "留言", "分享"],
            identifiers=["media_container"],
        ),
        NavigationState.PROFILE: StateSignal(
            texts=["posts", "followers", "following", "貼文", "粉絲", "追蹤中"],
        ),
    },
    "tiktok": {
        NavigationState.SEARCH_INPUT: StateSignal(
            texts=["Search", "搜尋"],
            element_types=["EditText"],
        ),
        NavigationState.SEARCH_RESULTS: StateSignal(
            texts=["Top", "Users", "Videos", "Sounds", "熱門", "用戶", "影片"],
        ),
        NavigationState.POST_DETAIL: StateSignal(
            identifiers=["video_container", "player"],
        ),
    },
    "x": {  # Twitter/X
        NavigationState.SEARCH_INPUT: StateSignal(
            texts=["Search", "搜尋"],
            element_types=["EditText"],
        ),
        NavigationState.SEARCH_RESULTS: StateSignal(
            texts=["Top", "Latest", "People", "Photos", "Videos", "熱門", "最新"],
        ),
        NavigationState.POST_DETAIL: StateSignal(
            texts=["Reply", "Repost", "Like", "回覆", "轉推", "喜歡"],
        ),
    },
    "facebook": {
        NavigationState.SEARCH_INPUT: StateSignal(
            texts=["Search", "搜尋"],
            element_types=["EditText"],
        ),
        NavigationState.SEARCH_RESULTS: StateSignal(
            texts=["All", "Posts", "People", "Photos", "全部", "貼文", "用戶"],
        ),
        NavigationState.POST_DETAIL: StateSignal(
            texts=["Like", "Comment", "Share", "讚", "留言", "分享"],
        ),
    },
    "youtube": {
        NavigationState.SEARCH_INPUT: StateSignal(
            element_types=["EditText"],
            identifiers=["search_edit_text"],
        ),
        NavigationState.SEARCH_RESULTS: StateSignal(
            texts=["Filter", "篩選"],
            identifiers=["results"],
        ),
        NavigationState.POST_DETAIL: StateSignal(
            identifiers=["player_view", "video_player"],
        ),
        NavigationState.COMMENTS: StateSignal(
            texts=["comments", "則留言", "Add a comment", "新增留言"],
        ),
    },
    # Default patterns (fallback)
    "default": {
        NavigationState.SEARCH_INPUT: StateSignal(
            texts=["Search", "搜尋", "検索"],
            element_types=["EditText", "TextField"],
        ),
        NavigationState.SEARCH_RESULTS: StateSignal(
            texts=["Top", "Recent", "All", "熱門", "最新", "全部"],
        ),
        NavigationState.POST_DETAIL: StateSignal(
            texts=["Like", "Comment", "Share", "Reply", "讚", "留言", "分享", "回覆"],
        ),
        NavigationState.LOGIN_WALL: StateSignal(
            texts=["Log in", "Sign in", "登入", "Sign up", "註冊"],
        ),
        NavigationState.POPUP: StateSignal(
            texts=["OK", "Cancel", "Allow", "Deny", "確定", "取消", "允許", "拒絕"],
            element_types=["AlertDialog", "Dialog"],
        ),
    }
}


# =============================================================================
# Visited Item
# =============================================================================

@dataclass
class VisitedItem:
    """Represents a visited post/item"""
    item_id: str
    title: str = ""
    author: str = ""
    platform: str = ""
    timestamp: float = field(default_factory=time.time)
    data: Dict = field(default_factory=dict)

    @classmethod
    def from_post(cls, title: str = "", author: str = "", index: int = 0,
                  platform: str = "", **extra) -> 'VisitedItem':
        """Create VisitedItem from post data"""
        # Generate unique ID from available data
        hash_input = f"{title}|{author}|{index}|{platform}"
        item_id = hashlib.md5(hash_input.encode()).hexdigest()[:16]

        return cls(
            item_id=item_id,
            title=title,
            author=author,
            platform=platform,
            data=extra
        )


# =============================================================================
# Navigation History Entry
# =============================================================================

@dataclass
class HistoryEntry:
    """Navigation history entry"""
    state: NavigationState
    screen_hash: str
    timestamp: float
    data: Dict = field(default_factory=dict)


# =============================================================================
# State Tracker
# =============================================================================

class StateTracker:
    """
    Tracks navigation state and visited items for patrol automation.

    Provides:
    - Navigation state detection
    - Visited tracking with deduplication
    - Navigation history for reliable back navigation
    - Persistence to JSON
    """

    def __init__(self, platform: str = "default", session_id: str = None,
                 auto_load: bool = True):
        """
        Initialize tracker.

        Args:
            platform: Platform name for state detection rules
            session_id: Session identifier (auto-generated if None)
            auto_load: Whether to load previous session data
        """
        self.platform = platform.lower()
        self.session_id = session_id or self._generate_session_id()

        # State tracking
        self.current_state = NavigationState.UNKNOWN
        self.history: List[HistoryEntry] = []

        # Visited tracking
        self.visited: Dict[str, VisitedItem] = {}

        # Statistics
        self.stats = {
            "posts_visited": 0,
            "scrolls": 0,
            "back_navigations": 0,
            "errors": 0,
            "start_time": time.time()
        }

        # Data file
        self.data_file = os.path.join(DATA_DIR, f"session_{self.session_id}.json")

        # Load previous data if exists
        if auto_load and os.path.exists(self.data_file):
            self.load()

        logger.info(f"StateTracker initialized: platform={platform}, session={self.session_id}")

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    # =========================================================================
    # State Detection
    # =========================================================================

    def detect_state(self, elements: List[Any]) -> NavigationState:
        """
        Detect current navigation state from screen elements.

        Args:
            elements: List of Element objects from screen

        Returns:
            Detected NavigationState
        """
        # Get signals for this platform (with default fallback)
        platform_signals = STATE_SIGNALS.get(self.platform, {})
        default_signals = STATE_SIGNALS.get("default", {})

        # Merge signals (platform-specific takes priority)
        signals = {**default_signals, **platform_signals}

        # Extract text and types from elements
        element_texts = set()
        element_types = set()
        element_ids = set()

        for el in elements:
            if hasattr(el, 'text') and el.text:
                element_texts.add(el.text.lower())
            if hasattr(el, 'content_desc') and el.content_desc:
                element_texts.add(el.content_desc.lower())
            if hasattr(el, 'element_type') and el.element_type:
                element_types.add(el.element_type)
            if hasattr(el, 'identifier') and el.identifier:
                element_ids.add(el.identifier.lower())

        # Check each possible state
        best_match = NavigationState.UNKNOWN
        best_score = 0

        for state, signal in signals.items():
            score = self._calculate_signal_score(signal, element_texts, element_types, element_ids)
            if score > best_score:
                best_score = score
                best_match = state

        # Update current state
        old_state = self.current_state
        self.current_state = best_match

        if old_state != best_match:
            logger.debug(f"State changed: {old_state.value} -> {best_match.value}")

        return best_match

    def _calculate_signal_score(self, signal: StateSignal, texts: Set[str],
                                 types: Set[str], ids: Set[str]) -> int:
        """Calculate match score for a signal"""
        score = 0

        # Check required texts
        for text in signal.texts:
            if any(text.lower() in t for t in texts):
                score += 2

        # Check element types
        for etype in signal.element_types:
            if any(etype in t for t in types):
                score += 1

        # Check identifiers
        for ident in signal.identifiers:
            if any(ident.lower() in i for i in ids):
                score += 2

        # Check exclusions (negative score)
        for text in signal.exclude_texts:
            if any(text.lower() in t for t in texts):
                score -= 3

        return max(0, score)

    def is_state(self, state: NavigationState) -> bool:
        """Check if current state matches"""
        return self.current_state == state

    def expect_state(self, state: NavigationState, timeout: float = 3.0,
                     observer: callable = None) -> bool:
        """
        Wait for expected state.

        Args:
            state: Expected state
            timeout: Maximum wait time
            observer: Function to call for re-observing screen

        Returns:
            True if state reached within timeout
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.current_state == state:
                return True
            if observer:
                elements = observer()
                self.detect_state(elements)
            time.sleep(0.5)
        return False

    # =========================================================================
    # Visited Tracking
    # =========================================================================

    def mark_visited(self, item: VisitedItem = None, **kwargs) -> str:
        """
        Mark item as visited.

        Args:
            item: VisitedItem to mark
            **kwargs: Alternative: create item from kwargs

        Returns:
            Item ID
        """
        if item is None:
            item = VisitedItem.from_post(platform=self.platform, **kwargs)

        self.visited[item.item_id] = item
        self.stats["posts_visited"] += 1

        logger.debug(f"Marked visited: {item.item_id[:8]} - {item.title[:30] if item.title else 'untitled'}")
        return item.item_id

    def is_visited(self, item_id: str = None, title: str = None,
                   author: str = None, index: int = 0) -> bool:
        """
        Check if item was visited.

        Can check by ID directly or by generating ID from fields.
        """
        if item_id:
            return item_id in self.visited

        # Generate ID from fields
        check_item = VisitedItem.from_post(
            title=title or "",
            author=author or "",
            index=index,
            platform=self.platform
        )
        return check_item.item_id in self.visited

    def get_visited_count(self) -> int:
        """Get number of visited items"""
        return len(self.visited)

    def get_visited_ids(self) -> Set[str]:
        """Get set of visited item IDs"""
        return set(self.visited.keys())

    def clear_visited(self):
        """Clear visited items"""
        self.visited.clear()
        self.stats["posts_visited"] = 0
        logger.info("Cleared visited items")

    # =========================================================================
    # Navigation History
    # =========================================================================

    def push_history(self, screen_hash: str, data: Dict = None):
        """
        Push current state to history.

        Called before navigation to enable reliable back navigation.
        """
        entry = HistoryEntry(
            state=self.current_state,
            screen_hash=screen_hash,
            timestamp=time.time(),
            data=data or {}
        )
        self.history.append(entry)

        # Limit history size
        if len(self.history) > 50:
            self.history = self.history[-50:]

    def pop_history(self) -> Optional[HistoryEntry]:
        """Pop and return last history entry"""
        if self.history:
            self.stats["back_navigations"] += 1
            return self.history.pop()
        return None

    def peek_history(self) -> Optional[HistoryEntry]:
        """Peek at last history entry without removing"""
        return self.history[-1] if self.history else None

    def get_expected_back_state(self) -> Optional[NavigationState]:
        """Get expected state after back navigation"""
        entry = self.peek_history()
        return entry.state if entry else None

    # =========================================================================
    # Statistics
    # =========================================================================

    def record_scroll(self):
        """Record a scroll action"""
        self.stats["scrolls"] += 1

    def record_error(self, error_type: str = "unknown"):
        """Record an error"""
        self.stats["errors"] += 1
        logger.warning(f"Error recorded: {error_type}")

    def get_stats(self) -> Dict:
        """Get current statistics"""
        stats = self.stats.copy()
        stats["duration"] = time.time() - stats["start_time"]
        stats["visited_count"] = len(self.visited)
        stats["history_depth"] = len(self.history)
        return stats

    # =========================================================================
    # Persistence
    # =========================================================================

    def save(self):
        """Save session data to disk"""
        data = {
            "session_id": self.session_id,
            "platform": self.platform,
            "current_state": self.current_state.value,
            "visited": {k: asdict(v) for k, v in self.visited.items()},
            "history": [
                {
                    "state": e.state.value,
                    "screen_hash": e.screen_hash,
                    "timestamp": e.timestamp,
                    "data": e.data
                }
                for e in self.history
            ],
            "stats": self.stats,
            "saved_at": time.time()
        }

        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.debug(f"Session saved: {self.data_file}")

    def load(self) -> bool:
        """Load session data from disk"""
        if not os.path.exists(self.data_file):
            return False

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.platform = data.get("platform", self.platform)
            self.current_state = NavigationState(data.get("current_state", "unknown"))

            # Load visited
            self.visited = {}
            for item_id, item_data in data.get("visited", {}).items():
                self.visited[item_id] = VisitedItem(**item_data)

            # Load history
            self.history = []
            for entry_data in data.get("history", []):
                self.history.append(HistoryEntry(
                    state=NavigationState(entry_data["state"]),
                    screen_hash=entry_data["screen_hash"],
                    timestamp=entry_data["timestamp"],
                    data=entry_data.get("data", {})
                ))

            self.stats = data.get("stats", self.stats)

            logger.info(f"Session loaded: {len(self.visited)} visited, {len(self.history)} history")
            return True

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            return False

    def reset(self):
        """Reset tracker to initial state"""
        self.current_state = NavigationState.UNKNOWN
        self.history.clear()
        self.visited.clear()
        self.stats = {
            "posts_visited": 0,
            "scrolls": 0,
            "back_navigations": 0,
            "errors": 0,
            "start_time": time.time()
        }
        logger.info("Tracker reset")


# =============================================================================
# Helper Functions
# =============================================================================

def generate_post_id(title: str = "", author: str = "", index: int = 0,
                     platform: str = "") -> str:
    """Generate unique post ID from available data"""
    hash_input = f"{title}|{author}|{index}|{platform}"
    return hashlib.md5(hash_input.encode()).hexdigest()[:16]


def create_tracker_for_platform(platform: str) -> StateTracker:
    """Create a StateTracker configured for specific platform"""
    return StateTracker(platform=platform)


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print("=== State Tracker Test ===\n")

    # Create tracker
    tracker = StateTracker(platform="threads")
    print(f"1. Created tracker: session={tracker.session_id}")

    # Test visited tracking
    print("\n2. Testing visited tracking...")
    id1 = tracker.mark_visited(title="Test Post 1", author="@user1")
    id2 = tracker.mark_visited(title="Test Post 2", author="@user2")

    print(f"   Marked 2 items visited")
    print(f"   Is id1 visited? {tracker.is_visited(item_id=id1)}")
    print(f"   Is new item visited? {tracker.is_visited(title='New Post', author='@new')}")

    # Test history
    print("\n3. Testing history...")
    tracker.push_history("hash1", {"screen": "search_results"})
    tracker.push_history("hash2", {"screen": "post_detail"})

    print(f"   History depth: {len(tracker.history)}")
    entry = tracker.pop_history()
    print(f"   Popped: state={entry.state.value}, hash={entry.screen_hash}")

    # Test stats
    print("\n4. Testing stats...")
    tracker.record_scroll()
    tracker.record_scroll()
    tracker.record_scroll()
    stats = tracker.get_stats()
    print(f"   Stats: {stats}")

    # Test save/load
    print("\n5. Testing persistence...")
    tracker.save()
    print(f"   Saved to: {tracker.data_file}")

    # Create new tracker and load
    tracker2 = StateTracker(platform="threads", session_id=tracker.session_id)
    print(f"   Loaded: {tracker2.get_visited_count()} visited items")

    print("\n=== Test Complete ===")
