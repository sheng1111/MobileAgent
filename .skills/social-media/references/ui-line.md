# LINE UI Reference

Package: `jp.naver.line.android`

## Navigation

Bottom tabs:
```
[Home] [Chats] [VOOM] [Wallet] [News]
```

Note: Tab names vary by region/language

## Layout - Main

```
+------------------------------------------+
|  LINE                           [Gear]   |
+------------------------------------------+
|  [Search bar]                            |
+------------------------------------------+
|  +------------------------------------+  |
|  |  Chat List                         |  |
|  |  O Contact 1      Message    Time  |  |
|  |  O Contact 2      Message    Time  |  |
|  |  O Group 1        Message    Time  |  |
|  +------------------------------------+  |
+------------------------------------------+
|  [Home] [Chats] [VOOM] [Wallet] [News]   |
+------------------------------------------+
```

## Layout - Chat Window

```
+------------------------------------------+
|  [<] Contact Name          [Call] [Menu] |
+------------------------------------------+
|                                          |
|  [Messages]                              |
|                                          |
+------------------------------------------+
|  [+] [Cam] [____Input____] [Sticker] [Mic]|
+------------------------------------------+
```

## Key Actions

### Send Message
1. Tap Chats tab
2. Select conversation (or search)
3. Tap input field
4. Type message
5. Tap send (or press Enter)

### Send Sticker
1. In chat, tap sticker icon
2. Select sticker
3. Tap to send

### Voice/Video Call
1. Open chat
2. Tap phone icon (top-right)
3. Select voice or video

### Add Friend
1. Go to Home tab
2. Tap Add Friend icon
3. Search by ID, QR, or phone

### VOOM (Timeline)
1. Tap VOOM tab
2. Like: tap heart
3. Comment: tap bubble

## Special Features

- Long-press message: recall, forward, copy
- Swipe left on chat: archive
- Notes/Albums in group chats
- Keep memo for self-notes

## contentDescription Keywords

- Send: "Send", "sousin"
- Sticker: "Sticker", "sutanpu"
- Call: "Call", "denwa"
- Video: "Video call"
