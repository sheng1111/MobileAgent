# Dating Apps UI Reference

Package names and UI patterns for dating/social apps.

## Package Names

| App | Package Name | Region |
|-----|-------------|--------|
| Tantan (探探) | `com.p1.mobile.putong` | China/Asia |
| Tinder | `com.tinder` | Global |
| Bumble | `com.bumble.app` | Global |
| Hinge | `co.hinge.app` | Global |
| OkCupid | `com.okcupid.okcupid` | Global |
| Pairs | `jp.eure.android.pairs` | Japan/Taiwan |
| Soul | `cn.soulapp.android` | China |
| Momo (陌陌) | `com.immomo.momo` | China |
| Badoo | `com.badoo.mobile` | Global |
| Coffee Meets Bagel | `com.coffeemeetsbagel.android` | Global |

---

## Common Dating App Patterns

### Swipe-Based Matching

Most dating apps use swipe gestures:
```
Swipe Right = Like
Swipe Left = Pass/Skip
Swipe Up = Super Like (some apps)
Tap buttons = Alternative to swipe
```

### Core UI Elements

```
+------------------------------------------+
|  [Logo]              [Profile] [Settings]|
+------------------------------------------+
|                                          |
|         [Profile Card]                   |
|         - Photo                          |
|         - Name, Age                      |
|         - Bio/Info                       |
|                                          |
+------------------------------------------+
|  [X/Pass]  [Super]  [Heart/Like]         |
+------------------------------------------+
|  [Cards] [Matches] [Messages] [Profile]  |
+------------------------------------------+
```

---

## Tantan (探探)

Package: `com.p1.mobile.putong`

### Layout

```
+------------------------------------------+
|  [Logo]                    [VIP] [Gear]  |
+------------------------------------------+
|                                          |
|         [Profile Card]                   |
|         - Main photo                     |
|         - Name, Age, Distance            |
|         - Verification badge             |
|                                          |
+------------------------------------------+
|     [X]      [Super]      [Heart]        |
+------------------------------------------+
|  [Discover] [Matches] [Chat] [Profile]   |
+------------------------------------------+
```

### Key Actions

**Like Someone:**
1. Swipe right on profile card
2. Or tap heart button

**Pass:**
1. Swipe left
2. Or tap X button

**Super Like:**
1. Swipe up
2. Or tap star/super button (VIP feature)

**Chat with Match:**
1. Go to Chat tab
2. Select matched user
3. Type message and send

**View Profile Details:**
1. Tap on profile card
2. Scroll to see more photos/info
3. Tap heart to like from detail view

### contentDescription Keywords
- Like: "like", "xihuan", "heart"
- Pass: "pass", "X", "skip"
- Chat: "chat", "liaotian", "message"

---

## Tinder

Package: `com.tinder`

### Layout

```
+------------------------------------------+
|  [Fire Logo]           [Shield] [Profile]|
+------------------------------------------+
|                                          |
|         [Profile Card Stack]             |
|         - Photo carousel                 |
|         - Name, Age                      |
|         - Distance, Bio                  |
|                                          |
+------------------------------------------+
|  [Undo] [X] [Star] [Heart] [Boost]       |
+------------------------------------------+
|  [Fire] [Search] [Gold] [Chat] [Profile] |
+------------------------------------------+
```

### Key Actions

**Like:**
1. Swipe right
2. Or tap green heart

**Pass:**
1. Swipe left
2. Or tap red X

**Super Like:**
1. Swipe up
2. Or tap blue star

**View More Photos:**
1. Tap photo to see next
2. Or swipe up on card for full profile

**Message Match:**
1. Tap chat bubble (bottom nav)
2. Select match
3. Type and send

### contentDescription Keywords
- Like: "Like"
- Nope: "Nope", "Pass"
- Super Like: "Super Like"
- Rewind: "Rewind"

---

## Bumble

Package: `com.bumble.app`

### Layout

```
+------------------------------------------+
|  [Bumble Logo]               [Filters]   |
+------------------------------------------+
|                                          |
|         [Profile Card]                   |
|         - Photo                          |
|         - Name, Age, Verified            |
|         - Prompts/Answers                |
|                                          |
+------------------------------------------+
|        [X]              [Heart]          |
+------------------------------------------+
|  [Cards] [Hive] [Chats] [Profile]        |
+------------------------------------------+
```

### Key Features

- Women message first (in Date mode) - OR can enable "let him make first move" (2025 update)
- Three modes: Date, BFF, Bizz
- 24-hour match expiry
- Check match bubbles for text-entry box (indicates who can message first)

### Key Actions

**Like:**
1. Swipe right
2. Or tap yellow heart

**Pass:**
1. Swipe left
2. Or tap X

**SuperSwipe:**
1. Tap SuperSwipe badge on card

**Message (women first):**
1. Go to Chats
2. Select match (within 24 hours)
3. Send first message

---

## Hinge

Package: `co.hinge.app`

### Layout

```
+------------------------------------------+
|  [H Logo]                     [Profile]  |
+------------------------------------------+
|  +------------------------------------+  |
|  |  [Photo]                           |  |
|  |  [Prompt/Answer]                   |  |
|  |  [Photo]                           |  |
|  |  [Prompt/Answer]                   |  |
|  +------------------------------------+  |
+------------------------------------------+
|  [X]                    [Like/Comment]   |
+------------------------------------------+
|  [Discover] [Standouts] [Likes] [Inbox]  |
+------------------------------------------+
```

### Key Features

- Like specific photos or prompts
- Add comment when liking
- "Designed to be deleted"

### Key Actions

**Like with Comment:**
1. Tap heart on specific photo/prompt
2. Add comment (optional)
3. Send

**Skip:**
1. Tap X button
2. Or scroll past without liking

**Message:**
1. Go to Inbox
2. Select conversation
3. Type and send

---

## Soul

Package: `cn.soulapp.android`

### Layout

```
+------------------------------------------+
|  [Soul Logo]              [Search]       |
+------------------------------------------+
|  [Soul Test] [Planet] [Match]            |
+------------------------------------------+
|                                          |
|  [Content Feed / Discovery]              |
|                                          |
+------------------------------------------+
|  [Planet] [Square] [+] [Chat] [Me]       |
+------------------------------------------+
```

### Key Features

- Soul Test for personality matching
- 3D avatars
- Anonymous social features
- Planet exploration (nearby users)

### Key Actions

**Match:**
1. Complete Soul Test
2. System suggests matches
3. Tap to chat

**Explore Planet:**
1. Tap Planet tab
2. Navigate 3D world
3. Tap users to view/chat

---

## Momo (陌陌)

Package: `com.immomo.momo`

### Layout

```
+------------------------------------------+
|  [Momo Logo]           [Search] [...]    |
+------------------------------------------+
|  [Nearby] [Follow] [Recommend]           |
+------------------------------------------+
|                                          |
|  [User Cards / Live Streams]             |
|                                          |
+------------------------------------------+
|  [Nearby] [Live] [Msg] [Contacts] [Me]   |
+------------------------------------------+
```

### Key Features

- Nearby people discovery
- Live streaming
- Flash chat (random video/text matching)
- Groups by interest

### Key Actions

**View Nearby:**
1. Tap Nearby tab
2. Browse user list
3. Tap user to view profile

**Start Chat:**
1. View profile
2. Tap message button
3. Send message

**Watch Live:**
1. Tap Live tab
2. Select stream
3. Interact via comments/gifts

---

## Pairs

Package: `jp.eure.android.pairs`

### Layout

```
+------------------------------------------+
|  [Pairs Logo]           [Search] [Coin]  |
+------------------------------------------+
|  [Today's Picks] [Search] [Community]    |
+------------------------------------------+
|                                          |
|  [Profile Cards]                         |
|                                          |
+------------------------------------------+
|  [Home] [Search] [Skip] [Like] [Message] |
+------------------------------------------+
```

### Key Features

- Serious dating/marriage focus
- Community groups by interest
- Profile verification

### Key Actions

**Like:**
1. Tap heart on profile
2. Or use like button

**Skip:**
1. Tap skip/X button

**Message Match:**
1. Go to Message tab
2. Select match
3. Send message

---

## Common Actions Summary

| Action | Gesture | Button |
|--------|---------|--------|
| Like | Swipe Right | Heart/Check |
| Pass | Swipe Left | X/Cross |
| Super Like | Swipe Up | Star/Lightning |
| View Details | Tap Card | - |
| Next Photo | Tap Photo | - |
| Message | - | Chat bubble |

## Error Handling

### No More Profiles
- Wait for new users
- Expand distance/age filters
- Some apps show "out of profiles" message

### Match Expired
- Bumble: 24-hour limit
- Some apps: rematch feature

### Message Failed
- Check internet connection
- Verify match still exists
- Some require mutual match first
