# Instagram UI Reference

Package: `com.instagram.android`

## Navigation (2025-2026 Major Update)

**New bottom tabs (rolled out late 2025):**
```
[Home] [Reels] [DMs] [Search] [Profile]
```

Key changes:
- Post creation (+) moved to TOP-LEFT corner
- Reels and DMs prioritized (center positions)
- Horizontal swipe between tabs supported
- Some regions open to Reels tab by default

**Previous layout (may still exist on older versions):**
```
[Home] [Search] [Reels] [Shop] [Profile]
```

## Layout Structure

```
+------------------------------------------+
|  [+Post]  [Logo]           [Heart] [DM]  |  Header
+------------------------------------------+
|     O  O  O  O  O  +                     |  Stories
+------------------------------------------+
|  +------------------------------------+  |
|  |         [Post Image/Video]         |  |
|  +------------------------------------+  |
|  [Heart] [Comment] [Share]      [Save]   |  Interactions
|  xxx likes                               |
|  username: caption...                    |
|  View all XX comments                    |
+------------------------------------------+
|  [Home] [Reels] [DMs] [Search] [Profile] |  Bottom Nav
+------------------------------------------+
```

## Interaction Icons

| Action | Icon | Position | State Change |
|--------|------|----------|--------------|
| Like | Heart | Below post, left | Outline → Filled red |
| Comment | Bubble | Next to heart | Opens comment sheet |
| Share/Send | Paper plane | Next to comment | Opens share sheet |
| Save | Bookmark | Far right | Outline → Filled |

## Key Actions

### Like
- Tap heart icon below post
- Or double-tap post image/video
- Verify: heart fills red

### Comment
1. Tap bubble icon
2. Input field appears at bottom
3. Type text → tap "Post"

### Share/Send
1. Tap paper plane icon
2. Select: Send to user / Share to Story / Copy Link

### DM (Direct Message)
- New: Tap DM tab (center of bottom nav)
- Or: Top-right paper plane icon (header)
- Select conversation → type → send

### Search
- Tap Search tab (4th from left in new layout)
- Type in search bar
- Filter: Accounts, Tags, Places, Reels

### Post/Create
- NEW LOCATION: Top-left corner (+)
- No longer in bottom navigation

### Follow
1. Go to user profile
2. Tap "Follow" button
3. Verify: changes to "Following"

## contentDescription Keywords

| Action | Keywords |
|--------|----------|
| Like | "like", "Love", "heart" |
| Comment | "Comment", "comments" |
| Share | "Share", "Send", "Direct" |
| Save | "Save", "Bookmark" |
| DM | "Direct", "Message", "Inbox" |
| Search | "Search", "Explore" |
| Create | "New post", "Create", "Camera" |

## Regional Variations

- India/Korea: May open directly to Reels tab
- Some users: "Tune your algorithm" settings available
- A/B testing: UI may differ between accounts
