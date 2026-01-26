# Threads UI Reference

Package: `com.instagram.barcelona`

## Navigation

**Header (top bar):**
- Left: Menu (hamburger icon)
- Center: Threads logo
- Right: Search (magnifying glass icon)

**Bottom tabs:**
```
[Home] [Messages] [Create] [Activity] [Profile]
```

Icon appearances:
- Home: House/feed icon (filled when active)
- Messages: Envelope icon
- Create: Plus (+) icon
- Activity: Heart icon
- Profile: Person silhouette

**IMPORTANT:** Search is NOT in bottom navigation. It's in the top-right header area.

## Layout Structure

```
+------------------------------------------+
| [Menu ≡]      [Logo]        [Search 🔍]  |  Header
+------------------------------------------+
|                                          |
|  +------------------------------------+  |
|  |  [Avatar] @username • time         |  |
|  |   Post text content...             |  |
|  |   [Image/Video if any]             |  |
|  +------------------------------------+  |
|  [Heart] [Comment] [Repost] [Share]      |
|                                          |
+------------------------------------------+
| [Home] [Messages] [Create] [Activity] [Profile]
+------------------------------------------+
```

## Key Actions

### Search

**Location:** Top-right header (NOT bottom navigation)

1. **Find search icon** in top-right header area
   - Look for magnifying glass icon
   - Usually rightmost icon in header
   - May not appear in accessibility tree - use screenshot if needed

2. **Tap search icon** to open search page

3. **Search page layout:**
   - Back button (top-left)
   - "Search" title
   - Search input field with magnifying glass icon
   - Suggested accounts below

4. **Tap search input field** → type query → submit

### Like
- Tap heart icon below post
- State change: outline → filled red

### Reply/Comment
1. Tap bubble icon below post
2. Composer opens
3. Type text → tap send

### Repost
1. Tap circular arrows icon
2. Choose: "Repost" or "Quote"

### Share
1. Tap paper plane icon
2. Options: Copy link, Share to...

### Follow
1. Visit user profile
2. Tap "Follow" button
3. Verify: changes to "Following"

### Create Post
1. Tap (+) in bottom navigation (center)
2. Composer opens with text input
3. Add media options: Gallery, Camera, Text, GIF, Poll, Location
4. Tap "Post"

### Messages
1. Tap envelope icon in bottom navigation (2nd from left)
2. Opens direct messages

## Interaction Icons

| Action | Icon | Location |
|--------|------|----------|
| Like | Heart outline | Below post |
| Reply | Speech bubble | Below post |
| Repost | Circular arrows | Below post |
| Share | Paper plane | Below post |

## Element Finding Strategy

1. Use `mobile_list_elements_on_screen` first
2. Search icon may not appear in accessibility tree
3. If not found, use screenshot + visual coordinates
4. Search icon typically at: top-right corner, within header area
5. Avoid bottom nav when looking for search - that's Messages

## contentDescription Keywords

| Action | Keywords (multilingual) |
|--------|------------------------|
| Search | "Search", "搜索", "搜尋", "検索" |
| Home | "Home", "首頁", "动态", "ホーム" |
| Messages | "Messages", "消息", "Direct", "收件箱" |
| Create | "New thread", "Create", "Post", "發文", "创建" |
| Activity | "Activity", "Notifications", "动态", "通知" |
| Profile | "Profile", "個人資料", "主页" |
| Like | "Like", "heart", "赞", "喜歡" |
| Reply | "Reply", "Comment", "回复", "留言" |
| Repost | "Repost", "转发" |
| Share | "Share", "分享" |
| Back | "Back", "返回" |
| Follow | "Follow", "关注" |

## Common Mistakes

### Search vs Messages confusion

**Problem:** Agent taps Messages (bottom nav, 2nd position) when trying to search

**Solution:**
- Search is in TOP-RIGHT header, not bottom navigation
- Bottom nav 2nd position is Messages (envelope icon)
- Look for magnifying glass in header area

### Search icon not in element list

**Problem:** Search icon doesn't appear in `mobile_list_elements_on_screen`

**Solution:**
1. Take screenshot to visually locate
2. Search icon is typically in top-right header
3. Estimate coordinates based on screen width (usually x > 900 for 1080px width)

## Version Notes

- UI may vary by region and version
- Search location has been observed in top-right header
- Always verify with screenshot before acting
- Bottom navigation order: Home, Messages, Create, Activity, Profile
