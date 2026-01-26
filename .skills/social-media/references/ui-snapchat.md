# Snapchat UI Reference

Package: `com.snapchat.android`

## Navigation

Main screen is camera. Swipe to navigate:
```
          [Stories/Discover]
                 ^
[Chat] <--- [Camera] ---> [Spotlight]
                 v
            [Map]
```

Bottom bar:
```
[Map] [Chat] [Camera] [Stories] [Spotlight]
```

## Layout - Camera (Main)

```
+------------------------------------------+
|  [Avatar] [Search]       [Add] [...]     |
+------------------------------------------+
|                                          |
|                                          |
|           [Camera Viewfinder]            |
|                                          |
|                                          |
+------------------------------------------+
|  [Memories]              [Flip Camera]   |
|           [Capture Button]               |
+------------------------------------------+
|  [Map] [Chat] [Cam] [Stories] [Spotlight]|
+------------------------------------------+
```

## Layout - Chat

```
+------------------------------------------+
|  [<]  Chat              [New] [...]      |
+------------------------------------------+
|  +------------------------------------+  |
|  |  Friend List                       |  |
|  |  O Friend 1        Status    Time  |  |
|  |  O Friend 2        Status    Time  |  |
|  +------------------------------------+  |
+------------------------------------------+
```

## Layout - Chat Conversation

```
+------------------------------------------+
|  [<] [Avatar] Name      [Call] [Video]   |
+------------------------------------------+
|                                          |
|  [Snaps and Messages]                    |
|                                          |
+------------------------------------------+
|  [Cam] [____Input____]   [Mic] [Sticker] |
+------------------------------------------+
```

## Key Actions

### Take Snap
1. Open camera (default screen)
2. Tap capture button for photo
3. Hold for video
4. Add effects, text, stickers

### Send Snap
1. After capturing, tap Send To
2. Select friends, groups, or stories
3. Tap blue arrow to send

### Reply to Snap
1. While viewing snap, swipe up
2. Or tap chat icon
3. Type reply

### Send Chat Message
1. Go to Chat screen
2. Tap friend
3. Type in input field
4. Tap send or press Enter

### View Story
1. Go to Stories screen
2. Tap on story to view
3. Tap to skip, swipe for next

### Post to Story
1. Create snap
2. Tap Send To
3. Select My Story
4. Tap send

### Video/Voice Call
1. Open chat with friend
2. Tap phone (voice) or video icon

### Add Friend
1. Tap Add Friend icon
2. Search by username
3. Or scan Snapcode
4. Or from contacts

### Spotlight
1. Swipe to Spotlight
2. Vertical video feed
3. Double-tap to like

## Special Features

- Disappearing messages
- Snap streaks
- Bitmoji avatars
- AR lenses/filters
- Snap Map
- Memories archive

## contentDescription Keywords

- Capture: "Capture", "Take photo"
- Send: "Send"
- Chat: "Chat"
- Call: "Call"
- Stories: "Stories"
