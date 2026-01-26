# TikTok UI Reference

Package: `com.zhiliaoapp.musically` (International), `com.ss.android.ugc.aweme` (Douyin/China)

## Navigation

Bottom tabs:
```
[Home] [Friends] [+] [Inbox] [Profile]
```

Top tabs (on Home):
```
[Following] [For You]
```

## Layout - Feed

Full-screen vertical video, swipe up/down to navigate:
```
+------------------------------------------+
|  [Following]  [For You]      [Search]    |  Top
+------------------------------------------+
|                                          |
|           [Full Screen Video]            |
|                                          |
|                         [Avatar+Follow]  |  Right side
|                         [Heart]          |  buttons
|                         [Comment]        |
|                         [Bookmark]       |
|                         [Share]          |
|                         [Music]          |
+------------------------------------------+
|  @username                               |
|  Caption #hashtag                        |
|  [Music ticker]                          |
+------------------------------------------+
|  [Home] [Friends] [+] [Inbox] [Profile]  |
+------------------------------------------+
```

## Interaction Buttons (right side)

| Position | Icon | Action |
|----------|------|--------|
| Top | Avatar + [+] | Follow creator |
| 2nd | Heart | Like |
| 3rd | Bubble | Comments |
| 4th | Bookmark | Save to Favorites |
| 5th | Arrow | Share |
| Bottom | Music disc | Sound/music page |

## Key Actions

### Like
- Tap heart icon (right side)
- Or double-tap video anywhere
- Verify: heart fills red

### Comment
1. Tap bubble icon
2. Comments panel slides up (bottom sheet)
3. Tap input field at bottom
4. Type comment → tap send

### Share
1. Tap share arrow
2. Options: Send to friends, Copy link, Save video, Share to other apps

### Follow
- Tap [+] on creator's avatar
- Or: profile → tap Follow button

### Save/Bookmark
- Tap bookmark icon
- Saved to Favorites collection

### Create Video
- Tap [+] in center of bottom nav
- Record or upload → edit → post

### Search
- Tap search icon (top-right on home)
- Or pull down on feed
- Filter: Videos, Users, Sounds, Hashtags, LIVE

### DM/Inbox
- Tap Inbox tab
- Select conversation or start new
- Type and send message

## Swipe Gestures

| Gesture | Action |
|---------|--------|
| Swipe UP | Next video |
| Swipe DOWN | Previous video |
| Swipe LEFT | Creator profile |
| Swipe RIGHT | (varies by region) |

## UX Notes

- Single-feed layout keeps focus on one video
- All interaction buttons in thumb-zone (right side)
- Bottom sheet for comments (stays in video context)
- Double-tap anywhere to like (most common method)

## contentDescription Keywords

- Like: "Like", "heart"
- Comment: "Comment", "comments"
- Share: "Share"
- Follow: "Follow"
- Bookmark: "Save", "Favorite", "Bookmark"
- Profile: "Profile"
- Search: "Search", "Discover"
