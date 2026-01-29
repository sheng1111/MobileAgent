#!/usr/bin/env python3
"""
Unit tests for src/patrol.py - Patrol State Machine
and src/state_tracker.py - State Tracker
"""
import os
import sys
import time
import json
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add src to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from state_tracker import (
    StateTracker, NavigationState, VisitedItem, HistoryEntry,
    generate_post_id, create_tracker_for_platform
)
from patrol import (
    PatrolStateMachine, PatrolConfig, PatrolState,
    PatrolReport, PostData, patrol
)


# =============================================================================
# StateTracker Tests
# =============================================================================

class TestNavigationState:
    """Tests for NavigationState enum"""

    def test_navigation_states(self):
        """Test NavigationState enum values"""
        assert NavigationState.UNKNOWN.value == "unknown"
        assert NavigationState.HOME_FEED.value == "home_feed"
        assert NavigationState.SEARCH_INPUT.value == "search_input"
        assert NavigationState.SEARCH_RESULTS.value == "search_results"
        assert NavigationState.POST_DETAIL.value == "post_detail"
        assert NavigationState.COMMENTS.value == "comments"


class TestVisitedItem:
    """Tests for VisitedItem class"""

    def test_visited_item_creation(self):
        """Test basic VisitedItem creation"""
        item = VisitedItem(
            item_id="abc123",
            title="Test Post",
            author="@testuser",
            platform="threads"
        )

        assert item.item_id == "abc123"
        assert item.title == "Test Post"
        assert item.author == "@testuser"
        assert item.platform == "threads"
        assert item.timestamp > 0

    def test_visited_item_from_post(self):
        """Test creating VisitedItem from post data"""
        item = VisitedItem.from_post(
            title="Post Title",
            author="@author",
            index=0,
            platform="instagram"
        )

        assert item.item_id is not None
        assert len(item.item_id) == 16
        assert item.title == "Post Title"
        assert item.author == "@author"

    def test_visited_item_id_uniqueness(self):
        """Test that different posts get different IDs"""
        item1 = VisitedItem.from_post(title="Post 1", author="@user1")
        item2 = VisitedItem.from_post(title="Post 2", author="@user1")
        item3 = VisitedItem.from_post(title="Post 1", author="@user2")

        assert item1.item_id != item2.item_id
        assert item1.item_id != item3.item_id

    def test_visited_item_id_consistency(self):
        """Test that same post data generates same ID"""
        item1 = VisitedItem.from_post(title="Post", author="@user", index=0, platform="x")
        item2 = VisitedItem.from_post(title="Post", author="@user", index=0, platform="x")

        assert item1.item_id == item2.item_id


class TestStateTracker:
    """Tests for StateTracker class"""

    @pytest.fixture
    def tracker(self, tmp_path):
        """Create tracker with temp data directory"""
        with patch('src.state_tracker.DATA_DIR', str(tmp_path)):
            return StateTracker(platform="threads")

    def test_tracker_init(self, tracker):
        """Test tracker initialization"""
        assert tracker.platform == "threads"
        assert tracker.current_state == NavigationState.UNKNOWN
        assert tracker.session_id is not None
        assert len(tracker.visited) == 0
        assert len(tracker.history) == 0

    def test_mark_visited(self, tracker):
        """Test marking item as visited"""
        item_id = tracker.mark_visited(title="Test Post", author="@test")

        assert item_id is not None
        assert len(tracker.visited) == 1
        assert tracker.stats["posts_visited"] == 1

    def test_is_visited(self, tracker):
        """Test checking if item is visited"""
        item_id = tracker.mark_visited(title="Test Post", author="@test")

        assert tracker.is_visited(item_id=item_id) is True
        assert tracker.is_visited(item_id="nonexistent") is False

    def test_is_visited_by_fields(self, tracker):
        """Test checking visited by fields"""
        tracker.mark_visited(title="Test Post", author="@test", index=0)

        assert tracker.is_visited(title="Test Post", author="@test", index=0) is True
        assert tracker.is_visited(title="Different", author="@test", index=0) is False

    def test_get_visited_count(self, tracker):
        """Test getting visited count"""
        assert tracker.get_visited_count() == 0

        tracker.mark_visited(title="Post 1")
        tracker.mark_visited(title="Post 2")

        assert tracker.get_visited_count() == 2

    def test_clear_visited(self, tracker):
        """Test clearing visited items"""
        tracker.mark_visited(title="Post 1")
        tracker.mark_visited(title="Post 2")
        tracker.clear_visited()

        assert tracker.get_visited_count() == 0
        assert tracker.stats["posts_visited"] == 0

    def test_push_pop_history(self, tracker):
        """Test navigation history"""
        tracker.push_history("hash1", {"screen": "results"})
        tracker.push_history("hash2", {"screen": "detail"})

        assert len(tracker.history) == 2

        entry = tracker.pop_history()
        assert entry.screen_hash == "hash2"
        assert len(tracker.history) == 1

    def test_peek_history(self, tracker):
        """Test peeking at history"""
        tracker.push_history("hash1")
        tracker.push_history("hash2")

        entry = tracker.peek_history()
        assert entry.screen_hash == "hash2"
        assert len(tracker.history) == 2  # Not removed

    def test_history_limit(self, tracker):
        """Test history size limit"""
        for i in range(60):
            tracker.push_history(f"hash{i}")

        assert len(tracker.history) <= 50

    def test_record_scroll(self, tracker):
        """Test recording scroll"""
        assert tracker.stats["scrolls"] == 0

        tracker.record_scroll()
        tracker.record_scroll()

        assert tracker.stats["scrolls"] == 2

    def test_record_error(self, tracker):
        """Test recording error"""
        assert tracker.stats["errors"] == 0

        tracker.record_error("click_failed")

        assert tracker.stats["errors"] == 1

    def test_get_stats(self, tracker):
        """Test getting stats"""
        tracker.mark_visited(title="Post")
        tracker.record_scroll()
        tracker.push_history("hash1")

        stats = tracker.get_stats()

        assert stats["posts_visited"] == 1
        assert stats["scrolls"] == 1
        assert stats["visited_count"] == 1
        assert stats["history_depth"] == 1
        assert "duration" in stats

    def test_save_and_load(self, tracker, tmp_path):
        """Test saving and loading session"""
        # Add some data
        tracker.mark_visited(title="Post 1", author="@user1")
        tracker.mark_visited(title="Post 2", author="@user2")
        tracker.push_history("hash1")
        tracker.current_state = NavigationState.SEARCH_RESULTS

        # Save
        tracker.save()
        assert os.path.exists(tracker.data_file)

        # Load into new tracker
        with patch('src.state_tracker.DATA_DIR', str(tmp_path)):
            tracker2 = StateTracker(platform="threads", session_id=tracker.session_id)

        assert tracker2.get_visited_count() == 2
        assert len(tracker2.history) == 1
        assert tracker2.current_state == NavigationState.SEARCH_RESULTS

    def test_reset(self, tracker):
        """Test resetting tracker"""
        tracker.mark_visited(title="Post")
        tracker.push_history("hash1")
        tracker.current_state = NavigationState.POST_DETAIL

        tracker.reset()

        assert tracker.current_state == NavigationState.UNKNOWN
        assert len(tracker.history) == 0
        assert len(tracker.visited) == 0


class TestStateDetection:
    """Tests for state detection"""

    @pytest.fixture
    def tracker(self, tmp_path):
        with patch('src.state_tracker.DATA_DIR', str(tmp_path)):
            return StateTracker(platform="threads")

    def test_detect_search_results(self, tracker):
        """Test detecting search results state"""
        # Create mock elements with search results indicators
        from executor import Element
        elements = [
            Element(text="Top"),
            Element(text="Recent"),
            Element(element_type="RecyclerView")
        ]

        state = tracker.detect_state(elements)
        assert state == NavigationState.SEARCH_RESULTS

    def test_detect_post_detail(self, tracker):
        """Test detecting post detail state"""
        from executor import Element
        elements = [
            Element(text="Like"),
            Element(text="Comment"),
            Element(text="Share")
        ]

        state = tracker.detect_state(elements)
        assert state == NavigationState.POST_DETAIL


# =============================================================================
# PatrolConfig Tests
# =============================================================================

class TestPatrolConfig:
    """Tests for PatrolConfig class"""

    def test_default_config(self):
        """Test default configuration"""
        config = PatrolConfig()

        assert config.max_posts == 10
        assert config.max_scrolls == 5
        assert config.max_time_minutes == 30
        assert config.max_consecutive_errors == 3
        assert config.verify_actions is True

    def test_custom_config(self):
        """Test custom configuration"""
        config = PatrolConfig(
            max_posts=5,
            max_scrolls=3,
            comments_per_post=20
        )

        assert config.max_posts == 5
        assert config.max_scrolls == 3
        assert config.comments_per_post == 20


# =============================================================================
# PatrolState Tests
# =============================================================================

class TestPatrolState:
    """Tests for PatrolState enum"""

    def test_patrol_states(self):
        """Test PatrolState enum values"""
        assert PatrolState.INIT.value == "init"
        assert PatrolState.VIEWING_RESULTS.value == "viewing_results"
        assert PatrolState.ENTERING_POST.value == "entering_post"
        assert PatrolState.READING_COMMENTS.value == "reading_comments"
        assert PatrolState.COMPLETED.value == "completed"


# =============================================================================
# PostData Tests
# =============================================================================

class TestPostData:
    """Tests for PostData class"""

    def test_post_data_creation(self):
        """Test PostData creation"""
        post = PostData(
            title="Test Post",
            author="@testuser",
            content="This is content",
            engagement={"likes": 100, "comments": 10}
        )

        assert post.title == "Test Post"
        assert post.author == "@testuser"
        assert post.engagement["likes"] == 100


# =============================================================================
# PatrolReport Tests
# =============================================================================

class TestPatrolReport:
    """Tests for PatrolReport class"""

    def test_report_creation(self):
        """Test PatrolReport creation"""
        report = PatrolReport(
            keyword="test",
            platform="threads",
            start_time=time.time()
        )

        assert report.keyword == "test"
        assert report.platform == "threads"
        assert len(report.posts) == 0

    def test_report_duration(self):
        """Test duration calculation"""
        start = time.time()
        report = PatrolReport(
            keyword="test",
            platform="threads",
            start_time=start,
            end_time=start + 60
        )

        assert report.duration == 60

    def test_report_summary(self):
        """Test summary generation"""
        report = PatrolReport(
            keyword="test",
            platform="threads",
            start_time=time.time(),
            end_time=time.time() + 30,
            posts=[
                PostData(title="Post 1", author="@user1"),
                PostData(title="Post 2", author="@user2")
            ]
        )

        summary = report.summary
        assert "Patrol Report: test" in summary
        assert "@user1" in summary


# =============================================================================
# PatrolStateMachine Tests
# =============================================================================

class TestPatrolStateMachine:
    """Tests for PatrolStateMachine class"""

    @pytest.fixture
    def patrol_machine(self, tmp_path):
        """Create patrol machine with mocked dependencies"""
        with patch('src.patrol.DeterministicExecutor'), \
             patch('src.patrol.ToolRouter'), \
             patch('src.state_tracker.DATA_DIR', str(tmp_path)):

            config = PatrolConfig(max_posts=3, max_scrolls=2)
            machine = PatrolStateMachine(
                platform="threads",
                config=config,
                device_id="test-device"
            )
            return machine

    def test_machine_init(self, patrol_machine):
        """Test machine initialization"""
        assert patrol_machine.platform == "threads"
        assert patrol_machine.state == PatrolState.INIT
        assert patrol_machine.config.max_posts == 3

    def test_should_continue_initial(self, patrol_machine):
        """Test should_continue in initial state"""
        patrol_machine.start_time = time.time()
        patrol_machine.posts_collected = []
        patrol_machine.error_count = 0

        assert patrol_machine._should_continue() is True

    def test_should_continue_max_posts(self, patrol_machine):
        """Test should_continue after reaching max posts"""
        patrol_machine.start_time = time.time()
        patrol_machine.posts_collected = [PostData() for _ in range(3)]

        assert patrol_machine._should_continue() is False

    def test_should_continue_max_errors(self, patrol_machine):
        """Test should_continue after max errors"""
        patrol_machine.start_time = time.time()
        patrol_machine.posts_collected = []
        patrol_machine.error_count = 3

        assert patrol_machine._should_continue() is False

    def test_should_continue_completed_state(self, patrol_machine):
        """Test should_continue in completed state"""
        patrol_machine.state = PatrolState.COMPLETED

        assert patrol_machine._should_continue() is False

    def test_get_progress(self, patrol_machine):
        """Test getting progress"""
        patrol_machine.start_time = time.time()
        patrol_machine.posts_collected = [PostData()]
        patrol_machine.scroll_count = 1

        progress = patrol_machine.get_progress()

        assert progress["posts_collected"] == 1
        assert progress["posts_target"] == 3
        assert progress["scrolls"] == 1
        assert progress["state"] == "init"

    def test_stop(self, patrol_machine):
        """Test stopping patrol"""
        patrol_machine.stop()

        assert patrol_machine.state == PatrolState.STOPPED

    def test_generate_post_id(self, patrol_machine):
        """Test post ID generation"""
        from executor import Element
        el = Element(
            text="Test Post",
            identifier="id1",
            bounds={"x": 0, "y": 0, "width": 100, "height": 100}
        )

        post_id = patrol_machine._generate_post_id(el)
        assert post_id is not None
        assert len(post_id) == 16


# =============================================================================
# Helper Functions Tests
# =============================================================================

class TestHelperFunctions:
    """Tests for helper functions"""

    def test_generate_post_id(self):
        """Test generate_post_id function"""
        id1 = generate_post_id(title="Post", author="@user", index=0)
        id2 = generate_post_id(title="Post", author="@user", index=0)
        id3 = generate_post_id(title="Different", author="@user", index=0)

        assert id1 == id2  # Same inputs = same ID
        assert id1 != id3  # Different inputs = different ID

    def test_create_tracker_for_platform(self, tmp_path):
        """Test create_tracker_for_platform function"""
        # Create a fresh temp directory for this test
        fresh_dir = tmp_path / "fresh_platform"
        fresh_dir.mkdir()
        with patch('src.state_tracker.DATA_DIR', str(fresh_dir)):
            # Create tracker directly with auto_load=False to avoid loading old sessions
            tracker = StateTracker(platform="instagram", auto_load=False)

        assert tracker.platform == "instagram"


# =============================================================================
# Integration Tests
# =============================================================================

class TestPatrolIntegration:
    """Integration tests for patrol workflow"""

    def test_full_visited_workflow(self, tmp_path):
        """Test complete visited tracking workflow"""
        with patch('src.state_tracker.DATA_DIR', str(tmp_path)):
            tracker = StateTracker(platform="threads")

            # Mark some posts as visited
            id1 = tracker.mark_visited(title="Post 1", author="@user1")
            id2 = tracker.mark_visited(title="Post 2", author="@user2")

            # Check visited status
            assert tracker.is_visited(item_id=id1) is True
            assert tracker.is_visited(item_id=id2) is True
            assert tracker.is_visited(item_id="nonexistent") is False

            # Save and reload
            tracker.save()

            tracker2 = StateTracker(platform="threads", session_id=tracker.session_id)
            assert tracker2.is_visited(item_id=id1) is True
            assert tracker2.is_visited(item_id=id2) is True

    def test_history_navigation(self, tmp_path):
        """Test navigation history workflow"""
        with patch('src.state_tracker.DATA_DIR', str(tmp_path)):
            tracker = StateTracker(platform="threads")

            # Simulate navigation
            tracker.current_state = NavigationState.SEARCH_RESULTS
            tracker.push_history("hash_results", {"state": "results"})

            tracker.current_state = NavigationState.POST_DETAIL
            tracker.push_history("hash_detail", {"state": "detail"})

            tracker.current_state = NavigationState.COMMENTS
            tracker.push_history("hash_comments", {"state": "comments"})

            # Go back
            entry = tracker.pop_history()
            assert entry.data["state"] == "comments"

            entry = tracker.pop_history()
            assert entry.data["state"] == "detail"

            entry = tracker.pop_history()
            assert entry.data["state"] == "results"
