# YouTube UI Reference

Package: `com.google.android.youtube`

## Navigation

Bottom tabs:
```
[Home] [Shorts] [+] [Subscriptions] [You]
```

## Layout - Home

```
+------------------------------------------+
|  [=]  [YouTube Logo]  [Cast] [Notif] [Search]|
+------------------------------------------+
|  [All] [Gaming] [Music] [News] [...]     |  Categories
+------------------------------------------+
|  +------------------------------------+  |
|  |  Video Thumbnail                   |  |
|  +------------------------------------+  |
|  [Channel] Title                   [:]   |
|  Views - Time ago                        |
+------------------------------------------+
|  [Home] [Shorts] [+] [Subs] [You]        |
+------------------------------------------+
```

## Layout - Video Player (2025 Update)

Portrait:
```
+------------------------------------------+
|  [Video Player]                          |
|  [Progress Bar]                          |
+------------------------------------------+
|  Title                                   |
|  Views - Date                            |
|  [Like] [Dislike] [Share] [Save] [...]   |
+------------------------------------------+
|  [Channel Avatar] Channel    [Subscribe] |
+------------------------------------------+
|  Comments section                        |
+------------------------------------------+
```

Landscape (redesigned):
```
+------------------------------------------+
|                                          |
|           [Video Content]                |
|                                          |
|  [Progress Bar]                          |
|  [Actions Pill]    [Play]    [CC][Gear]  |
+------------------------------------------+
```

Actions Pill contains: Like, Dislike, Comments, Save

## Interaction Buttons

| Icon | Action |
|------|--------|
| Thumbs up | Like |
| Thumbs down | Dislike |
| Arrow | Share |
| Bookmark/List | Save to playlist |
| Download | Download (Premium) |

## Key Actions

### Like Video
1. Find thumbs up icon below video
2. Tap to like (fills/highlights)

### Comment
1. Scroll to comments section
2. Tap "Add a comment..."
3. Type comment
4. Tap send arrow (red circle)

### Subscribe
1. Find Subscribe button next to channel
2. Tap to subscribe
3. Optionally tap bell for notifications

### Share
1. Tap share arrow
2. Select: Copy link, Share to app, etc.

### Save to Playlist
1. Tap Save/Bookmark icon
2. Select playlist or create new

### Search
1. Tap search icon (top-right)
2. Type query or use voice search
3. Select from suggestions

### Upload
1. Tap [+] in bottom nav
2. Select: Upload video, Create Short, Go live

## Special Features

- Picture-in-picture mode
- Background play (Premium)
- Offline downloads (Premium)
- Chapters navigation
- Playback speed control

## contentDescription Keywords

- Like: "like", "Like this video"
- Dislike: "dislike"
- Share: "Share"
- Save: "Save", "Add to playlist"
- Subscribe: "Subscribe"
- Comment: "Comments"
