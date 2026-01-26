# Common UI Patterns

Universal UI patterns across social media platforms.

## Icon Recognition

### Like/Heart
```
Shapes: Heart (outline/filled), Thumbs up
States: outline/gray (not liked) -> filled/red/blue (liked)
Position: Below post content
```

Keywords by language:
| Lang | Keywords |
|------|----------|
| EN | like, heart, love, favorite |
| zh | zan, xihuan, aixin |
| JP | iine, haato |
| KR | joayo |

### Comment
```
Shapes: Speech bubble, Chat icon
Position: Next to like button
```

Keywords: comment, reply, pinglun, huifu, komento, daetgeul

### Share
```
Shapes: Paper plane, Loop arrow, Forward arrow, Upload arrow
Position: Right side of interaction row
```

Keywords: share, send, repost, forward, fenxiang, zhuanfa, shea, gongyu

### Send
```
Shapes: Paper plane, Arrow
Position: Right of input field
```

### Search
```
Shapes: Magnifying glass
Position: Top bar, Bottom tab, or floating
```

## Input Field Detection

Element types: EditText, TextInputEditText, focusable+editable

Common hints:
- EN: "Type a message...", "Add a comment...", "Search"
- zh: "shu ru xun xi", "liu yan", "sou suo"
- JP: "messeeji wo nyuuryoku", "kensaku"

Position by function:
| Function | Position |
|----------|----------|
| Search | Top of screen |
| Message | Bottom of screen |
| Comment | Bottom of popup/section |
| Post | Center or top |

## Dialog Handling

Structure:
```
+------------------+
|     [Title]      |
|     Message      |
| [Cancel]  [OK]   |
+------------------+
```

Button keywords:
| Lang | Close | Cancel | OK | Allow | Deny |
|------|-------|--------|-----|-------|------|
| EN | Close, X | Cancel | OK | Allow | Deny |
| zh | guanbi | quxiao | queding | yunxu | jujue |
| JP | tojiru | kyanseru | OK | kyoka | kyohi |
| KR | datgi | chwiso | hwaginl | heoyong | geobu |

## Common Obstacles

### Login Wall
- Detect: "Sign in", "Log in" prompts
- Action: Report to user, do not auto-login

### Ads
- Detect: "Sponsored", "Ad" labels
- Action: Find X/Close/Skip button

### Permissions
- Action: Allow if needed for task, deny otherwise

### Updates
- Action: Select "Later"/"Skip" if possible
