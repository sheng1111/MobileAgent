# Threads Reference

Package: `com.instagram.barcelona`

## App Traits

- Text-based social network (Instagram companion)
- Twitter/X-like post format
- Linked to Instagram account
- Public conversations and replies
- Bottom tab navigation

## Known Quirks

- **CRITICAL - Search is NOT in bottom nav**: Search icon (🔍) is in TOP-RIGHT header area only
- **Search NOT in accessibility tree**: Use screenshot to visually locate the magnifying glass icon
- **Search location strategy**: Take screenshot → find 🔍 in header row (same row as Threads logo) → rightmost icon
- **Bottom nav order**: Home, Messages, Create(+), Activity, Profile - NO SEARCH HERE
- **Common mistake**: Tapping Messages (2nd bottom tab, envelope icon) when trying to search
- **Create is center (+)**: Post composer

## Element Keywords

| Action | contentDescription patterns |
|--------|----------------------------|
| Search | "Search", "搜索", "搜尋", "検索" |
| Home | "Home", "首頁", "ホーム" |
| Messages | "Messages", "Direct", "收件箱" |
| Create | "New thread", "Create", "Post", "發文" |
| Activity | "Activity", "Notifications", "通知" |
| Profile | "Profile", "個人資料" |
| Like | "Like", "heart", "喜歡" |
| Reply | "Reply", "Comment", "留言" |
| Repost | "Repost", "转发" |
| Share | "Share", "分享" |
| Follow | "Follow", "关注" |
