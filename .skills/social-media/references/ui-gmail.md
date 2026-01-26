# Gmail UI Reference

Package: `com.google.android.gm`

## Navigation

Uses hamburger menu + bottom action bar.

```
[=]  [Search mail]              [Avatar]
[Inbox/Labels]
[Compose FAB]
```

## Layout - Inbox

```
+------------------------------------------+
|  [=]  Search in mail           [Avatar]  |
+------------------------------------------+
|  +------------------------------------+  |
|  |  Email List                        |  |
|  |  [*] Sender      Subject     Time  |  |
|  |  [*] Sender      Subject     Time  |  |
|  |  [*] Sender      Subject     Time  |  |
|  +------------------------------------+  |
+------------------------------------------+
|                              [Compose +] |  Floating
+------------------------------------------+
```

## Layout - Email View (2025 Update)

```
+------------------------------------------+
|  [<]  Subject                     [...]  |
+------------------------------------------+
|  [Avatar] Sender                  Time   |
|  To: recipient                           |
+------------------------------------------+
|                                          |
|  Email content                           |
|                                          |
+------------------------------------------+
|  [Reply] [Reply All] [Forward] [React]   |  Docked bar
+------------------------------------------+
```

New docked reply bar (2025):
- Stays visible while scrolling
- Quick access to Reply, Reply All, Forward
- Emoji reactions available

## Key Actions

### Compose Email
1. Tap floating compose button [+]
2. Fill To, Subject, Body
3. Tap send arrow (top-right)

### Reply
1. Open email
2. Tap Reply in docked bar (bottom)
3. Or scroll to bottom for reply box
4. Type reply
5. Tap send

### Reply All
1. Open email
2. Tap Reply All in docked bar

### Forward
1. Open email
2. Tap Forward in docked bar
3. Add recipient
4. Tap send

### Search
1. Tap search bar
2. Type query
3. Use filters: from:, to:, subject:, has:attachment

### Labels/Folders
1. Tap hamburger menu [=]
2. Select label: Primary, Social, Promotions, Updates
3. Or custom labels

### Archive
1. Swipe left or right on email
2. Or tap archive icon in toolbar

### Delete
1. Long-press to select
2. Tap delete icon
3. Or swipe (if configured)

### Star/Flag
1. Tap star icon on email row
2. Or in email view

### Attach File
1. In compose, tap attach icon (paperclip)
2. Select: Attach file, Insert from Drive

## Special Features

- Undo send (within time limit)
- Schedule send
- Confidential mode
- Smart compose suggestions
- Priority inbox

## contentDescription Keywords

- Compose: "Compose"
- Reply: "Reply"
- Forward: "Forward"
- Archive: "Archive"
- Delete: "Delete"
- Star: "Star", "Add star"
- Search: "Search"
