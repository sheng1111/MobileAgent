#!/usr/bin/env python3
"""
Platform Adapter - Unified interface for different social media platforms.

This module abstracts platform-specific differences so the patrol logic
can work across Threads, Instagram, TikTok, X, YouTube, etc.

Each adapter provides:
- Element identification (search box, post cards, comments button)
- State detection (is this the results page? post detail? comments?)
- Content extraction (author, text, engagement metrics)
- Navigation patterns (how to open search, back to results)

Usage:
    from src.platform_adapter import get_adapter, PlatformAdapter

    adapter = get_adapter("threads")

    # Find search entry point
    search_el = adapter.find_search_entry(elements)

    # Extract visible posts
    posts = adapter.extract_post_cards(elements)

    # Check current state
    if adapter.is_post_detail(elements):
        comments_btn = adapter.find_comments_button(elements)
"""
import os
import sys
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from logger import get_logger

logger = get_logger(__name__)


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class PostCard:
    """Represents a post card in feed/results"""
    author: str = ""
    author_id: str = ""  # @username or user ID
    text: str = ""
    text_preview: str = ""  # First ~100 chars
    timestamp: str = ""
    likes: str = ""
    comments: str = ""
    shares: str = ""
    element: Any = None  # Original element reference
    bounds: Dict = field(default_factory=dict)
    index: int = 0  # Position in list

    @property
    def unique_id(self) -> str:
        """Generate unique ID for deduplication"""
        import hashlib
        data = f"{self.author_id}|{self.text_preview[:50]}|{self.index}"
        return hashlib.md5(data.encode()).hexdigest()[:16]


@dataclass
class PlatformConfig:
    """Platform-specific configuration"""
    package_name: str
    app_name: str
    search_patterns: List[str] = field(default_factory=list)
    post_indicators: List[str] = field(default_factory=list)
    comment_indicators: List[str] = field(default_factory=list)
    skip_texts: List[str] = field(default_factory=list)


# =============================================================================
# Abstract Base Adapter
# =============================================================================

class PlatformAdapter(ABC):
    """
    Abstract base class for platform adapters.

    Subclasses implement platform-specific element identification and extraction.
    """

    def __init__(self):
        self.config = self._get_config()

    @abstractmethod
    def _get_config(self) -> PlatformConfig:
        """Return platform configuration"""
        pass

    @property
    def package_name(self) -> str:
        return self.config.package_name

    @property
    def app_name(self) -> str:
        return self.config.app_name

    # =========================================================================
    # Element Finding
    # =========================================================================

    @abstractmethod
    def find_search_entry(self, elements: List[Any]) -> Optional[Any]:
        """
        Find the search entry point (icon, tab, or input field).

        Returns:
            Element to click to initiate search, or None
        """
        pass

    @abstractmethod
    def find_search_input(self, elements: List[Any]) -> Optional[Any]:
        """
        Find the search input field (EditText).

        Returns:
            Input element to type into, or None
        """
        pass

    @abstractmethod
    def find_comments_button(self, elements: List[Any]) -> Optional[Any]:
        """
        Find the comments/replies button on a post.

        Returns:
            Element to click to open comments, or None
        """
        pass

    def find_element_by_patterns(self, elements: List[Any],
                                  patterns: List[str],
                                  field: str = "text") -> Optional[Any]:
        """
        Find element matching any of the patterns.

        Args:
            elements: List of elements
            patterns: Text patterns to match
            field: Field to check ("text", "content_desc", "identifier")
        """
        for el in elements:
            value = ""
            if field == "text":
                value = getattr(el, 'text', '') or ''
            elif field == "content_desc":
                value = getattr(el, 'content_desc', '') or ''
            elif field == "identifier":
                value = getattr(el, 'identifier', '') or ''

            value_lower = value.lower()
            for pattern in patterns:
                if pattern.lower() in value_lower:
                    return el
        return None

    # =========================================================================
    # State Detection
    # =========================================================================

    @abstractmethod
    def is_search_results(self, elements: List[Any]) -> bool:
        """Check if current screen is search results"""
        pass

    @abstractmethod
    def is_post_detail(self, elements: List[Any]) -> bool:
        """Check if current screen is post detail view"""
        pass

    @abstractmethod
    def is_comments_view(self, elements: List[Any]) -> bool:
        """Check if current screen is comments view"""
        pass

    def is_home_feed(self, elements: List[Any]) -> bool:
        """Check if current screen is home feed"""
        # Default: look for feed indicators
        return self._has_any_text(elements, ["For You", "Following", "為你推薦", "正在追蹤"])

    def is_login_wall(self, elements: List[Any]) -> bool:
        """Check if login wall is blocking"""
        return self._has_any_text(elements, [
            "Log in", "Sign in", "登入", "Sign up", "註冊",
            "Create account", "建立帳號"
        ])

    def is_popup(self, elements: List[Any]) -> bool:
        """Check if a popup/dialog is showing"""
        # Look for dialog-like elements or common button patterns
        has_dialog = any(
            'dialog' in (getattr(el, 'element_type', '') or '').lower()
            for el in elements
        )
        has_dismiss = self._has_any_text(elements, [
            "OK", "Cancel", "Close", "Not now", "Later",
            "確定", "取消", "關閉", "稍後"
        ])
        return has_dialog or (has_dismiss and len(elements) < 20)

    def _has_any_text(self, elements: List[Any], patterns: List[str]) -> bool:
        """Check if any element contains any of the patterns"""
        for el in elements:
            text = (getattr(el, 'text', '') or '').lower()
            desc = (getattr(el, 'content_desc', '') or '').lower()
            combined = text + ' ' + desc
            for pattern in patterns:
                if pattern.lower() in combined:
                    return True
        return False

    def _count_matching(self, elements: List[Any], patterns: List[str]) -> int:
        """Count elements matching any pattern"""
        count = 0
        for el in elements:
            text = (getattr(el, 'text', '') or '').lower()
            for pattern in patterns:
                if pattern.lower() in text:
                    count += 1
                    break
        return count

    # =========================================================================
    # Content Extraction
    # =========================================================================

    @abstractmethod
    def extract_post_cards(self, elements: List[Any]) -> List[PostCard]:
        """
        Extract post cards from current screen.

        Returns:
            List of PostCard objects representing visible posts
        """
        pass

    def extract_author(self, text: str) -> Tuple[str, str]:
        """
        Extract author name and ID from text.

        Returns:
            (display_name, @username or ID)
        """
        # Common pattern: @username
        match = re.search(r'@[\w.]+', text)
        if match:
            username = match.group(0)
            # Try to find display name before @
            name_match = re.match(r'^([^@]+)\s*@', text)
            if name_match:
                return name_match.group(1).strip(), username
            return username, username

        # Fallback: first word/line as name
        lines = text.strip().split('\n')
        if lines:
            return lines[0][:30], ""
        return "", ""

    def extract_engagement(self, elements: List[Any]) -> Dict[str, str]:
        """
        Extract engagement metrics from post detail.

        Returns:
            {"likes": "123", "comments": "45", "shares": "6"}
        """
        engagement = {}
        for el in elements:
            text = (getattr(el, 'text', '') or '').lower()
            desc = (getattr(el, 'content_desc', '') or '').lower()
            combined = text + ' ' + desc

            # Look for number + label patterns
            if any(x in combined for x in ['like', '讚', '喜歡']):
                nums = re.findall(r'[\d,.]+[kmb]?', combined)
                if nums:
                    engagement['likes'] = nums[0]
            elif any(x in combined for x in ['comment', '留言', 'repl', '回覆']):
                nums = re.findall(r'[\d,.]+[kmb]?', combined)
                if nums:
                    engagement['comments'] = nums[0]
            elif any(x in combined for x in ['share', '分享', 'repost', '轉']):
                nums = re.findall(r'[\d,.]+[kmb]?', combined)
                if nums:
                    engagement['shares'] = nums[0]

        return engagement

    def is_skip_element(self, element: Any) -> bool:
        """Check if element should be skipped (navigation, system UI)"""
        text = (getattr(element, 'text', '') or '')
        identifier = (getattr(element, 'identifier', '') or '')

        # Skip navigation and system elements
        for skip in self.config.skip_texts:
            if skip.lower() in text.lower():
                return True

        # Skip elements with navigation-related IDs
        nav_ids = ['tab', 'nav', 'bottom_bar', 'toolbar', 'action_bar']
        for nav_id in nav_ids:
            if nav_id in identifier.lower():
                return True

        return False


# =============================================================================
# Threads Adapter
# =============================================================================

class ThreadsAdapter(PlatformAdapter):
    """Adapter for Threads (Instagram's text platform)"""

    def _get_config(self) -> PlatformConfig:
        return PlatformConfig(
            package_name="com.instagram.barcelona",
            app_name="Threads",
            search_patterns=["Search", "搜尋", "search_tab"],
            post_indicators=["Reply", "回覆", "Repost", "轉發"],
            comment_indicators=["replies", "則回覆", "comment", "留言"],
            skip_texts=[
                "Home", "Search", "Activity", "Profile",
                "首頁", "搜尋", "動態", "個人檔案",
                "For You", "Following", "為你推薦", "正在追蹤"
            ]
        )

    def find_search_entry(self, elements: List[Any]) -> Optional[Any]:
        # Threads: search icon in bottom bar or top
        el = self.find_element_by_patterns(elements, ["Search", "搜尋"])
        if el:
            return el
        # Try by identifier
        return self.find_element_by_patterns(
            elements, ["search"], field="identifier"
        )

    def find_search_input(self, elements: List[Any]) -> Optional[Any]:
        for el in elements:
            el_type = getattr(el, 'element_type', '') or ''
            if 'EditText' in el_type or 'TextField' in el_type:
                return el
        return None

    def find_comments_button(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements,
            ["replies", "回覆", "comment", "留言", "Reply"]
        )

    def is_search_results(self, elements: List[Any]) -> bool:
        # Has tab filters (Top, Recent, etc.) but no search input visible
        has_tabs = self._has_any_text(elements, ["Top", "Recent", "熱門", "最新"])
        has_input = self.find_search_input(elements) is not None
        return has_tabs and not has_input

    def is_post_detail(self, elements: List[Any]) -> bool:
        # Has reply button and post content
        has_reply = self._has_any_text(elements, ["Reply", "回覆"])
        has_repost = self._has_any_text(elements, ["Repost", "轉發", "Quote"])
        return has_reply and has_repost

    def is_comments_view(self, elements: List[Any]) -> bool:
        # Multiple reply elements visible
        reply_count = self._count_matching(elements, ["Reply", "回覆"])
        return reply_count >= 3

    def extract_post_cards(self, elements: List[Any]) -> List[PostCard]:
        posts = []
        current_post = None

        for i, el in enumerate(elements):
            if self.is_skip_element(el):
                continue

            text = getattr(el, 'text', '') or ''
            clickable = getattr(el, 'clickable', False)
            bounds = getattr(el, 'bounds', {})

            # Skip short texts
            if len(text) < 5:
                continue

            # Detect author line (usually has @ or is at top of card)
            if '@' in text or (clickable and len(text) < 50):
                name, username = self.extract_author(text)
                if current_post and current_post.text:
                    posts.append(current_post)
                current_post = PostCard(
                    author=name,
                    author_id=username,
                    element=el,
                    bounds=bounds,
                    index=len(posts)
                )
            elif current_post:
                # Add to current post content
                if not current_post.text:
                    current_post.text = text
                    current_post.text_preview = text[:100]

        if current_post and current_post.text:
            posts.append(current_post)

        return posts


# =============================================================================
# Instagram Adapter
# =============================================================================

class InstagramAdapter(PlatformAdapter):
    """Adapter for Instagram"""

    def _get_config(self) -> PlatformConfig:
        return PlatformConfig(
            package_name="com.instagram.android",
            app_name="Instagram",
            search_patterns=["Search", "搜尋", "search_tab", "Search and explore"],
            post_indicators=["Like", "Comment", "Share", "讚", "留言", "分享"],
            comment_indicators=["comments", "則留言", "View all", "查看全部"],
            skip_texts=[
                "Home", "Search", "Reels", "Shop", "Profile",
                "首頁", "搜尋", "Reels", "商店", "個人檔案"
            ]
        )

    def find_search_entry(self, elements: List[Any]) -> Optional[Any]:
        # Instagram: search tab in bottom bar
        return self.find_element_by_patterns(
            elements, ["Search", "搜尋", "Search and explore"]
        )

    def find_search_input(self, elements: List[Any]) -> Optional[Any]:
        for el in elements:
            el_type = getattr(el, 'element_type', '') or ''
            text = getattr(el, 'text', '') or ''
            if 'EditText' in el_type:
                return el
            if 'Search' in text and getattr(el, 'clickable', False):
                return el
        return None

    def find_comments_button(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements,
            ["View all", "查看全部", "comments", "留言"]
        )

    def is_search_results(self, elements: List[Any]) -> bool:
        has_tabs = self._has_any_text(elements, ["Accounts", "Tags", "Places", "帳號", "標籤"])
        return has_tabs

    def is_post_detail(self, elements: List[Any]) -> bool:
        has_like = self._has_any_text(elements, ["Like", "讚"])
        has_comment = self._has_any_text(elements, ["Comment", "留言"])
        has_share = self._has_any_text(elements, ["Share", "Send", "分享"])
        return has_like and has_comment and has_share

    def is_comments_view(self, elements: List[Any]) -> bool:
        comment_count = self._count_matching(elements, ["Reply", "回覆", "Like", "讚"])
        return comment_count >= 5

    def extract_post_cards(self, elements: List[Any]) -> List[PostCard]:
        posts = []

        for i, el in enumerate(elements):
            if self.is_skip_element(el):
                continue

            text = getattr(el, 'text', '') or ''
            desc = getattr(el, 'content_desc', '') or ''
            clickable = getattr(el, 'clickable', False)
            bounds = getattr(el, 'bounds', {})

            # Instagram posts often have descriptive content_desc
            if desc and len(desc) > 20:
                name, username = self.extract_author(desc)
                posts.append(PostCard(
                    author=name,
                    author_id=username,
                    text=desc,
                    text_preview=desc[:100],
                    element=el,
                    bounds=bounds,
                    index=len(posts)
                ))
            elif clickable and len(text) > 20:
                name, username = self.extract_author(text)
                posts.append(PostCard(
                    author=name,
                    author_id=username,
                    text=text,
                    text_preview=text[:100],
                    element=el,
                    bounds=bounds,
                    index=len(posts)
                ))

        return posts


# =============================================================================
# X (Twitter) Adapter
# =============================================================================

class XAdapter(PlatformAdapter):
    """Adapter for X (Twitter)"""

    def _get_config(self) -> PlatformConfig:
        return PlatformConfig(
            package_name="com.twitter.android",
            app_name="X",
            search_patterns=["Search", "搜尋", "Search X"],
            post_indicators=["Reply", "Repost", "Like", "回覆", "轉推", "喜歡"],
            comment_indicators=["replies", "回覆"],
            skip_texts=[
                "Home", "Search", "Notifications", "Messages", "Profile",
                "首頁", "搜尋", "通知", "訊息", "個人資料",
                "For you", "Following", "為你推薦", "正在追蹤"
            ]
        )

    def find_search_entry(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements, ["Search", "搜尋", "Search X"]
        )

    def find_search_input(self, elements: List[Any]) -> Optional[Any]:
        for el in elements:
            el_type = getattr(el, 'element_type', '') or ''
            if 'EditText' in el_type:
                return el
        return None

    def find_comments_button(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements, ["Reply", "回覆", "replies"]
        )

    def is_search_results(self, elements: List[Any]) -> bool:
        has_tabs = self._has_any_text(elements, ["Top", "Latest", "People", "熱門", "最新"])
        return has_tabs

    def is_post_detail(self, elements: List[Any]) -> bool:
        has_reply = self._has_any_text(elements, ["Reply", "回覆"])
        has_repost = self._has_any_text(elements, ["Repost", "轉推", "Quote"])
        has_like = self._has_any_text(elements, ["Like", "喜歡"])
        return has_reply and has_repost and has_like

    def is_comments_view(self, elements: List[Any]) -> bool:
        # X shows replies inline, so check for multiple reply indicators
        reply_count = self._count_matching(elements, ["Reply", "回覆"])
        return reply_count >= 3

    def extract_post_cards(self, elements: List[Any]) -> List[PostCard]:
        posts = []
        current_post = None

        for el in elements:
            if self.is_skip_element(el):
                continue

            text = getattr(el, 'text', '') or ''
            clickable = getattr(el, 'clickable', False)
            bounds = getattr(el, 'bounds', {})

            if len(text) < 3:
                continue

            # Author pattern: @username or name with @
            if '@' in text and len(text) < 50:
                name, username = self.extract_author(text)
                if current_post and current_post.text:
                    posts.append(current_post)
                current_post = PostCard(
                    author=name,
                    author_id=username,
                    element=el,
                    bounds=bounds,
                    index=len(posts)
                )
            elif current_post and not current_post.text and len(text) > 10:
                current_post.text = text
                current_post.text_preview = text[:100]

        if current_post and current_post.text:
            posts.append(current_post)

        return posts


# =============================================================================
# TikTok Adapter
# =============================================================================

class TikTokAdapter(PlatformAdapter):
    """Adapter for TikTok"""

    def _get_config(self) -> PlatformConfig:
        return PlatformConfig(
            package_name="com.zhiliaoapp.musically",
            app_name="TikTok",
            search_patterns=["Search", "搜尋", "Discover"],
            post_indicators=["Like", "Comment", "Share", "讚", "留言", "分享"],
            comment_indicators=["comments", "則留言"],
            skip_texts=[
                "Home", "Discover", "Inbox", "Profile",
                "首頁", "探索", "收件匣", "個人資料",
                "For You", "Following", "為你推薦", "關注"
            ]
        )

    def find_search_entry(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements, ["Search", "搜尋", "Discover", "探索"]
        )

    def find_search_input(self, elements: List[Any]) -> Optional[Any]:
        for el in elements:
            el_type = getattr(el, 'element_type', '') or ''
            if 'EditText' in el_type:
                return el
        return None

    def find_comments_button(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements, ["comments", "留言", "Comment"]
        )

    def is_search_results(self, elements: List[Any]) -> bool:
        has_tabs = self._has_any_text(elements, ["Top", "Users", "Videos", "Sounds", "熱門", "用戶"])
        return has_tabs

    def is_post_detail(self, elements: List[Any]) -> bool:
        # TikTok video view
        has_like = self._has_any_text(elements, ["Like", "讚"])
        has_comment = self._has_any_text(elements, ["Comment", "留言"])
        return has_like and has_comment

    def is_comments_view(self, elements: List[Any]) -> bool:
        comment_count = self._count_matching(elements, ["Reply", "回覆"])
        return comment_count >= 3

    def extract_post_cards(self, elements: List[Any]) -> List[PostCard]:
        posts = []

        for el in elements:
            if self.is_skip_element(el):
                continue

            text = getattr(el, 'text', '') or ''
            desc = getattr(el, 'content_desc', '') or ''
            clickable = getattr(el, 'clickable', False)
            bounds = getattr(el, 'bounds', {})

            content = desc if len(desc) > len(text) else text
            if len(content) < 10:
                continue

            if clickable:
                name, username = self.extract_author(content)
                posts.append(PostCard(
                    author=name,
                    author_id=username,
                    text=content,
                    text_preview=content[:100],
                    element=el,
                    bounds=bounds,
                    index=len(posts)
                ))

        return posts


# =============================================================================
# YouTube Adapter
# =============================================================================

class YouTubeAdapter(PlatformAdapter):
    """Adapter for YouTube"""

    def _get_config(self) -> PlatformConfig:
        return PlatformConfig(
            package_name="com.google.android.youtube",
            app_name="YouTube",
            search_patterns=["Search", "搜尋"],
            post_indicators=["Subscribe", "Like", "Dislike", "Share", "訂閱", "喜歡", "分享"],
            comment_indicators=["comments", "則留言", "Add a comment"],
            skip_texts=[
                "Home", "Shorts", "Subscriptions", "Library",
                "首頁", "Shorts", "訂閱內容", "媒體庫"
            ]
        )

    def find_search_entry(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements, ["Search", "搜尋"], field="content_desc"
        ) or self.find_element_by_patterns(
            elements, ["search"], field="identifier"
        )

    def find_search_input(self, elements: List[Any]) -> Optional[Any]:
        for el in elements:
            el_type = getattr(el, 'element_type', '') or ''
            identifier = getattr(el, 'identifier', '') or ''
            if 'EditText' in el_type or 'search_edit_text' in identifier:
                return el
        return None

    def find_comments_button(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements, ["comments", "留言", "Add a comment", "新增留言"]
        )

    def is_search_results(self, elements: List[Any]) -> bool:
        has_filter = self._has_any_text(elements, ["Filter", "篩選"])
        return has_filter

    def is_post_detail(self, elements: List[Any]) -> bool:
        # YouTube video player view
        has_subscribe = self._has_any_text(elements, ["Subscribe", "訂閱"])
        has_like = self._has_any_text(elements, ["Like", "喜歡", "Dislike"])
        return has_subscribe or has_like

    def is_comments_view(self, elements: List[Any]) -> bool:
        has_comments = self._has_any_text(elements, ["comments", "留言"])
        has_add = self._has_any_text(elements, ["Add a comment", "新增留言"])
        return has_comments or has_add

    def extract_post_cards(self, elements: List[Any]) -> List[PostCard]:
        posts = []

        for el in elements:
            if self.is_skip_element(el):
                continue

            desc = getattr(el, 'content_desc', '') or ''
            clickable = getattr(el, 'clickable', False)
            bounds = getattr(el, 'bounds', {})

            # YouTube video cards have detailed content_desc
            if clickable and len(desc) > 20:
                # Parse: "Title by Channel · views · time"
                parts = desc.split('·')
                title = parts[0].strip() if parts else desc

                # Extract channel name
                channel = ""
                if ' by ' in title:
                    title, channel = title.rsplit(' by ', 1)

                posts.append(PostCard(
                    author=channel,
                    author_id=channel,
                    text=title,
                    text_preview=title[:100],
                    element=el,
                    bounds=bounds,
                    index=len(posts)
                ))

        return posts


# =============================================================================
# Facebook Adapter
# =============================================================================

class FacebookAdapter(PlatformAdapter):
    """Adapter for Facebook"""

    def _get_config(self) -> PlatformConfig:
        return PlatformConfig(
            package_name="com.facebook.katana",
            app_name="Facebook",
            search_patterns=["Search", "搜尋"],
            post_indicators=["Like", "Comment", "Share", "讚", "留言", "分享"],
            comment_indicators=["comments", "則留言", "Write a comment"],
            skip_texts=[
                "Home", "Watch", "Marketplace", "Notifications", "Menu",
                "首頁", "Watch", "Marketplace", "通知", "選單"
            ]
        )

    def find_search_entry(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements, ["Search", "搜尋", "Search Facebook"]
        )

    def find_search_input(self, elements: List[Any]) -> Optional[Any]:
        for el in elements:
            el_type = getattr(el, 'element_type', '') or ''
            if 'EditText' in el_type:
                return el
        return None

    def find_comments_button(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(
            elements, ["Comment", "留言", "comments"]
        )

    def is_search_results(self, elements: List[Any]) -> bool:
        has_tabs = self._has_any_text(elements, ["All", "Posts", "People", "全部", "貼文", "用戶"])
        return has_tabs

    def is_post_detail(self, elements: List[Any]) -> bool:
        has_like = self._has_any_text(elements, ["Like", "讚"])
        has_comment = self._has_any_text(elements, ["Comment", "留言"])
        has_share = self._has_any_text(elements, ["Share", "分享"])
        return has_like and has_comment and has_share

    def is_comments_view(self, elements: List[Any]) -> bool:
        comment_count = self._count_matching(elements, ["Reply", "回覆", "Like", "讚"])
        return comment_count >= 5

    def extract_post_cards(self, elements: List[Any]) -> List[PostCard]:
        posts = []

        for el in elements:
            if self.is_skip_element(el):
                continue

            text = getattr(el, 'text', '') or ''
            desc = getattr(el, 'content_desc', '') or ''
            clickable = getattr(el, 'clickable', False)
            bounds = getattr(el, 'bounds', {})

            content = desc if len(desc) > len(text) else text
            if clickable and len(content) > 20:
                name, username = self.extract_author(content)
                posts.append(PostCard(
                    author=name,
                    author_id=username or name,
                    text=content,
                    text_preview=content[:100],
                    element=el,
                    bounds=bounds,
                    index=len(posts)
                ))

        return posts


# =============================================================================
# Generic Adapter (Fallback)
# =============================================================================

class GenericAdapter(PlatformAdapter):
    """Generic adapter for unknown platforms"""

    def __init__(self, package_name: str = ""):
        self._package = package_name
        super().__init__()

    def _get_config(self) -> PlatformConfig:
        return PlatformConfig(
            package_name=self._package,
            app_name="App",
            search_patterns=["Search", "搜尋", "検索"],
            post_indicators=["Like", "Comment", "Share", "Reply", "讚", "留言", "分享", "回覆"],
            comment_indicators=["comments", "replies", "留言", "回覆"],
            skip_texts=["Home", "Back", "首頁", "返回"]
        )

    def find_search_entry(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(elements, self.config.search_patterns)

    def find_search_input(self, elements: List[Any]) -> Optional[Any]:
        for el in elements:
            el_type = getattr(el, 'element_type', '') or ''
            if 'EditText' in el_type or 'TextField' in el_type:
                return el
        return None

    def find_comments_button(self, elements: List[Any]) -> Optional[Any]:
        return self.find_element_by_patterns(elements, self.config.comment_indicators)

    def is_search_results(self, elements: List[Any]) -> bool:
        return self._has_any_text(elements, ["Top", "Recent", "All", "熱門", "最新", "全部"])

    def is_post_detail(self, elements: List[Any]) -> bool:
        indicator_count = self._count_matching(elements, self.config.post_indicators)
        return indicator_count >= 2

    def is_comments_view(self, elements: List[Any]) -> bool:
        return self._count_matching(elements, self.config.comment_indicators) >= 2

    def extract_post_cards(self, elements: List[Any]) -> List[PostCard]:
        posts = []

        for el in elements:
            if self.is_skip_element(el):
                continue

            text = getattr(el, 'text', '') or ''
            desc = getattr(el, 'content_desc', '') or ''
            clickable = getattr(el, 'clickable', False)
            bounds = getattr(el, 'bounds', {})

            content = desc if len(desc) > len(text) else text
            if clickable and len(content) > 15:
                name, username = self.extract_author(content)
                posts.append(PostCard(
                    author=name,
                    author_id=username or name,
                    text=content,
                    text_preview=content[:100],
                    element=el,
                    bounds=bounds,
                    index=len(posts)
                ))

        return posts


# =============================================================================
# Factory Function
# =============================================================================

# Adapter registry
ADAPTERS: Dict[str, type] = {
    "threads": ThreadsAdapter,
    "instagram": InstagramAdapter,
    "x": XAdapter,
    "twitter": XAdapter,
    "tiktok": TikTokAdapter,
    "youtube": YouTubeAdapter,
    "facebook": FacebookAdapter,
}

# Package to platform mapping
PACKAGE_MAP: Dict[str, str] = {
    "com.instagram.barcelona": "threads",
    "com.instagram.android": "instagram",
    "com.twitter.android": "x",
    "com.zhiliaoapp.musically": "tiktok",
    "com.google.android.youtube": "youtube",
    "com.facebook.katana": "facebook",
}


def get_adapter(platform: str = None, package: str = None) -> PlatformAdapter:
    """
    Get adapter for platform.

    Args:
        platform: Platform name (threads, instagram, x, tiktok, youtube, facebook)
        package: Package name (auto-detect platform)

    Returns:
        PlatformAdapter instance
    """
    # Resolve platform from package
    if package and not platform:
        platform = PACKAGE_MAP.get(package)

    if platform:
        platform = platform.lower()
        if platform in ADAPTERS:
            return ADAPTERS[platform]()

    # Fallback to generic
    logger.warning(f"Unknown platform '{platform}', using generic adapter")
    return GenericAdapter(package or "")


def list_supported_platforms() -> List[str]:
    """List supported platform names"""
    return list(ADAPTERS.keys())


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    print("=== Platform Adapter Test ===\n")

    print("1. Supported platforms:")
    for p in list_supported_platforms():
        adapter = get_adapter(p)
        print(f"   - {p}: {adapter.package_name} ({adapter.app_name})")

    print("\n2. Testing Threads adapter...")
    adapter = get_adapter("threads")

    # Mock elements
    class MockElement:
        def __init__(self, text="", content_desc="", element_type="",
                     identifier="", clickable=False, bounds=None):
            self.text = text
            self.content_desc = content_desc
            self.element_type = element_type
            self.identifier = identifier
            self.clickable = clickable
            self.bounds = bounds or {}

    mock_elements = [
        MockElement(text="Search", clickable=True),
        MockElement(text="@user1", clickable=True),
        MockElement(text="This is a test post content that is long enough"),
        MockElement(text="Reply", clickable=True),
        MockElement(text="Repost", clickable=True),
        MockElement(text="@user2", clickable=True),
        MockElement(text="Another post here"),
    ]

    print(f"   find_search_entry: {adapter.find_search_entry(mock_elements) is not None}")
    print(f"   is_post_detail: {adapter.is_post_detail(mock_elements)}")

    posts = adapter.extract_post_cards(mock_elements)
    print(f"   extracted posts: {len(posts)}")
    for p in posts:
        print(f"      - {p.author_id}: {p.text_preview[:30]}...")

    print("\n=== Test Complete ===")
