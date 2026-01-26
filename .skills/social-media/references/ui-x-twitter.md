# X (Twitter) UI Reference

Package: `com.twitter.android`

## Navigation

Bottom tabs:
```
[Home] [Search] [Communities] [Notifications] [Messages]
```

## Layout

```
+------------------------------------------+
|  [Avatar]      [X Logo]           [Gear] |
+------------------------------------------+
|  [For You] [Following]                   |
+------------------------------------------+
|  [Avatar] Name @handle            [...]  |
|  Post content...                         |
|  +------------------------------------+  |
|  |         [Media]                    |  |
|  +------------------------------------+  |
|  [Reply] [Repost] [Like] [Views] [Share] |
+------------------------------------------+
|  [Compose +]                             |  Floating
+------------------------------------------+
|  [Home] [Search] [Comm] [Notif] [DM]     |
+------------------------------------------+
```

## Interaction Buttons (left to right)

| Icon | Action | Description |
|------|--------|-------------|
| Bubble | Reply | Comment on post |
| Loop arrows | Repost | Repost or Quote |
| Heart | Like | Like the post |
| Chart | Views | View analytics |
| Upload arrow | Share | Share options |
| Bookmark | Save | Save for later |

## Key Actions

### Like
1. Tap heart icon
2. Heart fills red when liked

### Reply
1. Tap bubble icon
2. Type reply
3. Tap Post button

### Repost
1. Tap loop arrows
2. Select: Repost (instant) or Quote (add comment)
3. For quote: type comment, tap Post

### Bookmark
1. Tap bookmark icon (or in share menu)
2. Access saved posts in profile > Bookmarks

### Send DM
1. Tap Messages tab
2. Select conversation or tap compose
3. Type message
4. Tap send (paper plane)

### Search
1. Tap Search tab
2. Type in search bar
3. Filter: Top, Latest, People, Media, Lists

### Follow
1. Go to profile
2. Tap Follow button
3. Changes to Following

### Compose Post
1. Tap floating [+] button
2. Type content
3. Add media if needed
4. Tap Post

## contentDescription Keywords

- Reply: "Reply"
- Repost: "Repost", "Retweet"
- Like: "Like"
- Share: "Share"
- Bookmark: "Bookmark"
