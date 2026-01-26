# Telegram UI Reference

Package: `org.telegram.messenger`

## Navigation

Uses hamburger menu + floating action button.

Main structure:
```
[Hamburger Menu] [Search] [...]
[Chat List]
[Floating Compose Button]
```

Menu items:
- New Group, New Channel, Contacts, Calls, People Nearby, Saved Messages, Settings

## Layout - Main

```
+------------------------------------------+
|  [=]  Telegram              [Search]     |
+------------------------------------------+
|  +------------------------------------+  |
|  |  Chat List                         |  |
|  |  O Contact 1      Message    Time  |  |
|  |  O Group          Message    Time  |  |
|  |  O Channel        Message    Time  |  |
|  +------------------------------------+  |
+------------------------------------------+
|                              [Compose +] |  Floating
+------------------------------------------+
```

## Layout - Chat Window

```
+------------------------------------------+
|  [<] Contact/Group Name    [Call] [...]  |
+------------------------------------------+
|                                          |
|  [Messages]                              |
|                                          |
+------------------------------------------+
|  [Attach] [____Input____] [Emoji] [Mic]  |
+------------------------------------------+
```

## Key Actions

### Send Message
1. Tap on conversation
2. Tap input field
3. Type message
4. Tap send button (paper plane) or press Enter

### Send Voice Message
1. In chat, hold mic button
2. Slide up to lock for hands-free
3. Release to send

### Reply to Message
1. Swipe right on message
2. Or long-press > Reply
3. Type reply

### Forward Message
1. Long-press message
2. Tap Forward
3. Select recipient(s)

### React to Message
1. Double-tap message for quick reaction
2. Or long-press > select reaction

### Start New Chat
1. Tap floating compose button
2. Select contact or search

### Create Group
1. Tap hamburger menu
2. Select New Group
3. Add members
4. Set name and create

### Search
1. Tap search icon (top)
2. Type query
3. Results show chats and messages

### Join Channel
1. Search for channel
2. Or use invite link
3. Tap Join

## Special Features

- Secret chats: end-to-end encrypted
- Self-destructing messages
- Edit sent messages
- Pin messages in chats
- Folders for chat organization
- Swipe left on chat: archive

## contentDescription Keywords

- Send: "Send"
- Attach: "Attach"
- Voice: "Voice message"
- Menu: "Open menu"
