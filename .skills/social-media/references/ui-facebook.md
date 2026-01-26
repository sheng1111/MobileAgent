# Facebook UI Reference

Package: `com.facebook.katana` (main), `com.facebook.lite` (lite)

## Navigation

Bottom tabs:
```
[Home] [Video] [Marketplace] [Notifications] [Menu]
```

## Layout

```
+------------------------------------------+
|  [Search]                  [Messenger]   |
+------------------------------------------+
|  [Story] [+Create]                       |
+------------------------------------------+
|  [Avatar] Name              [...]        |
|  Post content text                       |
|  +------------------------------------+  |
|  |         [Media]                    |  |
|  +------------------------------------+  |
|  Reactions xxx           xx comments     |
|  ----------------------------------------|
|  [Like]  [Comment]  [Share]              |
+------------------------------------------+
|  [Home] [Video] [Market] [Notif] [Menu]  |
+------------------------------------------+
```

## Reactions (6 types)

Long-press Like to select:
1. Like (thumbs up)
2. Love (heart)
3. Haha (laughing)
4. Wow (surprised)
5. Sad (crying)
6. Angry (angry face)

## Key Actions

### React to Post
1. Tap Like for quick like
2. Long-press Like for reaction menu
3. Select reaction type

### Comment
1. Tap Comment button
2. Find input field
3. Type and tap Post

### Share
1. Tap Share button
2. Select: Share Now, Share to Story, Send in Messenger

### Send Message (Messenger)
1. Tap Messenger icon (top-right)
2. Or open Messenger app (`com.facebook.orca`)
3. Select conversation
4. Type and send

### Search
1. Tap search bar at top
2. Type query
3. Filter: All, Posts, People, Photos, Videos, Pages, Groups

## contentDescription Keywords

- Like: "Like", "React"
- Comment: "Comment"
- Share: "Share"
- More: "More options"
