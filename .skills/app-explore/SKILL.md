---
name: app-explore
description: Operate Android apps via MCP tools and ADB. Research mindset - browse multiple sources before concluding. Supports action reasoning with Observe-Think-Act-Verify loop.
---

# App Explore Skill

## CRITICAL: Execute Real Actions

**You control a real device. You MUST actually execute MCP tools.**

```
WRONG: "I searched Threads and found..." (without calling any tools)
RIGHT: mobile_launch_app → mobile_click → mobile_type_keys → mobile_swipe → Report
```

If you report findings without executing tools, **you are failing the task**.

## Be Human-Like

Think like a curious human exploring an app:

```
Human behavior:
1. Open app, look around (screenshot/list_elements)
2. Find search, tap it (click)
3. Type query, wait for results (type_keys)
4. Scroll through results, see what looks interesting (swipe)
5. Tap a post that catches attention (click)
6. Read the content, check comments (list_elements)
7. Go back, find another interesting post (back, click)
8. Repeat until satisfied with understanding
9. Form opinion based on what was seen
```

**A human doesn't stop after seeing 2 posts.** Neither should you.

## Mindset

```
You are a RESEARCHER with device control, not a script runner.

OBSERVE → THINK → ACT → VERIFY → ADAPT

Never assume UI state. Always observe first.
When finding information, browse multiple sources before concluding.
```

## Action Reasoning Format

Use this format for each action (inspired by AppAgent):

```
Observation: [What I see on screen - key elements, state, blockers]
Thought: [Why I'm choosing this action, how it progresses the task]
Action: [The specific MCP tool call or ADB command]
Summary: [What happened, what to do next]
```

## Element-First Strategy (CRITICAL)

**The #1 cause of slow and unreliable automation: using screenshots to guess coordinates.**

### The Correct Flow

```
FAST & RELIABLE:
1. mobile_list_elements_on_screen
2. Find target by text/type/identifier (NOT by visual position)
3. Calculate click point: (x + width/2, y + height/2)
4. mobile_click_on_screen_at_coordinates

SLOW & ERROR-PRONE (avoid):
1. mobile_take_screenshot
2. LLM analyzes image, guesses coordinates
3. mobile_click_on_screen_at_coordinates
4. Misclick → repeat entire cycle
```

### Element Selection Priority

1. **identifier/resourceId** - Most stable across app versions
2. **text content** - Match label text
3. **element type** - Button, EditText, etc.
4. **accessibility description** - contentDescription

### When to Use Screenshot

| Situation | Use Screenshot |
|-----------|----------------|
| Element in tree | NO - use element bounds |
| Custom/game UI | YES - no accessibility data |
| Visual verification | YES - confirm state |
| Debug mismatches | YES - compare tree vs display |

## MANDATORY: Click-Verify Protocol

**Every click MUST be verified.** This prevents the "phantom click" problem where you think you clicked but nothing happened.

### The Protocol

```
FOR EVERY CLICK:
1. BEFORE: mobile_list_elements_on_screen → record element count and key texts
2. CLICK:  mobile_click_on_screen_at_coordinates
3. WAIT:   Pause 0.5-1s for screen to update
4. VERIFY: mobile_list_elements_on_screen again → check screen changed
5. DECIDE: If changed → proceed. If not changed → retry or report failure.
```

### Verification Checks

| Check | How | Pass Condition |
|-------|-----|----------------|
| Screen changed | Compare element lists | Different elements OR different count |
| Expected state | Look for expected text | Target text/element now visible |
| No error | Check for error messages | No "error", "failed", "not found" |

### NEVER Do This

```
WRONG (no verification):
1. mobile_click_on_screen_at_coordinates(500, 1200)
2. "I clicked the post and now I'm viewing it..." ← ASSUMPTION!
3. Continue with next action ← May be operating on wrong screen

RIGHT (with verification):
1. mobile_click_on_screen_at_coordinates(500, 1200)
2. [wait 1s]
3. mobile_list_elements_on_screen
4. Check: Does element list contain expected content? (e.g., "comments", "reply")
5. If YES → Continue
6. If NO → Retry click or try alternative target
```

### Retry Protocol

```
Attempt 1: Click target → Verify → Failed
Attempt 2: Wait 1s → Click again → Verify → Failed
Attempt 3: Scroll slightly → Find target again → Click → Verify → Failed
STOP: Report "Unable to enter post after 3 attempts"
```

### State Verification Examples

| After Action | Expected Change |
|--------------|-----------------|
| Click post | See "comment", "like", "share" elements |
| Click search | See EditText focused, keyboard visible |
| Submit search | See results list, post cards |
| Press back | Return to previous screen (different elements) |
| Scroll | Different elements in view |

### Why This Matters

Without verification:
- 30-50% of clicks may have no effect (timing, overlay, wrong coords)
- You continue on wrong screen
- Entire task fails due to compounding errors

With verification:
- Catch failures immediately
- Retry or adapt
- Reliable multi-step automation

## Tool Priority

| Priority | Tool | Use When |
|----------|------|----------|
| 1 | `mobile_list_elements_on_screen` | BEFORE any click/tap |
| 2 | `mobile_click_on_screen_at_coordinates` | Click element center |
| 3 | `mobile_type_keys` | Text input |
| 4 | `mobile_swipe_on_screen` | Scroll/navigate |
| 5 | `mobile_press_button` | BACK, HOME, ENTER |
| 6 | `mobile_launch_app` | Start app |
| 7 | `mobile_take_screenshot` | ONLY when element not in tree |

### Timing: Wait Before Acting

Many errors are timing issues, not coordinate issues:

| After... | Wait |
|----------|------|
| App launch | 2-3s for splash to complete |
| Navigation | 1-2s for screen transition |
| Typing | 1s for suggestions to appear |
| Scroll | 1s for content to load |
| Click | Verify state changed before next action |

## Research Protocol

### Don't Stop at First Result

```
BAD:  Search → Skim 2 posts → Report
GOOD: Search → Scroll 3+ screens → Open 5+ items → Read content → Report
```

### Minimum Actions (Research Tasks)

| Action | Minimum | Rationale |
|--------|---------|-----------|
| Scroll | 3+ screens | Discover more content |
| Open items | 5+ posts | Get actual content, not titles |
| Read comments | 3+ threads | Understand context |

**Quality Gate Before Reporting**:
- [ ] Scrolled 3+ screens
- [ ] Opened 5+ items
- [ ] Captured author/source for each
- [ ] Got diverse viewpoints

### Research Loop

```
1. SEARCH  - Enter query, get results
   a. Find search icon/input → Tap to focus
   b. Type keyword → MUST verify text entered
   c. Submit (tap search/enter) → Wait for results
   
2. SCAN    - Scroll, note interesting items
3. DIVE    - Open 3-5 promising items
4. EXTRACT - Key info from each (title, points, source, date)
5. BACK    - Return to list
6. REPEAT  - Until sufficient coverage
7. SYNTHESIZE - Patterns, themes, varying opinions
8. REPORT  - Summary with multiple perspectives
```

### CRITICAL: Complete the Search Flow

**Common failure**: Opening search UI but abandoning before typing keyword.

```
1. Find search icon/input → Tap to focus
2. Verify input focused (keyboard visible or cursor blinking)
3. Use mobile_type_keys with submit: true
4. Wait 2-3s for results to load
5. Use mobile_list_elements_on_screen to confirm results appeared
6. If no results, try alternative search (hashtag vs direct search)
```

**DO NOT abandon when**:
- Search UI opened but keyword not yet typed
- Keyword typed but search not submitted
- Results still loading

## Element Discovery

### Find by Identifier, Not Position

```
BAD:  Screenshot → Guess tap (540, 1200) for search
GOOD: List elements → Find by resourceId/text/type → Click center
```

### Selection Priority

1. **resourceId/identifier** - e.g., `com.app:id/search_button`
2. **text/label** - e.g., "Search", "搜尋"
3. **type + position** - e.g., "EditText at top"
4. **accessibility description** - contentDescription field

### Common Patterns

| Element | Look For |
|---------|----------|
| Search | magnifying glass, "Search" text, EditText at top |
| Submit | "OK"/"Send"/"Done", confirm text, bottom-right |
| Close | X icon, "Cancel", top corners |
| Back | arrow top-left, BACK button |
| Menu | hamburger (☰), three dots (⋮) |
| Like | heart (♥), thumbs up (👍) |
| Comment | bubble (💬), chat icon |
| Share | paper plane, arrow (↗) |
| Save/Bookmark | bookmark icon, star |
| More options | three dots vertical/horizontal |

### Element Types

| Looking for | Element types |
|-------------|---------------|
| Buttons | Button, ImageButton, clickable=true |
| Text input | EditText, TextInputEditText |
| Lists | RecyclerView, ListView items |
| Scrollable | ScrollView, RecyclerView |

## Action Self-Reflection

After each action, evaluate result (inspired by AppAgent reflection):

| Decision | When | Next Step |
|----------|------|-----------|
| SUCCESS | Action moved task forward | Continue to next step |
| CONTINUE | Screen changed but not as expected | Try different element |
| INEFFECTIVE | Nothing changed | Verify coords, try alternative |
| BACK | Navigated to wrong page | Press back, try different path |

## Task Decomposition

Break complex tasks into subgoals. Each: observe → think → act → verify

```
Task: "Research topic X on YouTube"
  1. Launch YouTube
  2. Find and tap search icon
  3. Type query and submit
  4. Scroll and scan results (note interesting videos)
  5. Open video 1 → Watch intro → Note key points → Back
  6. Open video 2 → Watch intro → Note key points → Back
  7. Open video 3 → Watch intro → Note key points → Back
  8. Continue (5-10 for research)
  9. Synthesize findings
  10. Report comprehensive answer
```

## Obstacle Handling

| Obstacle | Detection | Action |
|----------|-----------|--------|
| Popup/Dialog | Overlay, modal | Find dismiss (X, OK, Skip, Cancel) |
| Permission | "Allow"/"Deny" buttons | Allow if needed, else Deny |
| Login wall | Login form, "Sign in" | STOP, report to user |
| Ad | "Ad"/"Sponsored" label | Find Skip/X, wait countdown |
| Loading | Spinner, progress | Wait 2-3s, re-observe |
| CAPTCHA | Image puzzle, checkbox | STOP, report to user |
| Rate limit | Error message | Wait, slow down |
| Keyboard | On screen | Use for text input, dismiss if blocking |

## Swipe Patterns

| Goal | Direction | Distance |
|------|-----------|----------|
| Scroll down | up | medium |
| Scroll up | down | medium |
| Next item (horizontal) | left | short |
| Previous item | right | short |
| Refresh (pull down) | down | long |
| Dismiss bottom sheet | down | medium |

## Natural Browsing Behavior


Think like a curious human:

- **Be curious** - "What else is there?" Keep scrolling to discover more
- **Be thorough** - "Let me check this one too" Open multiple posts
- **Be skeptical** - "Is this the full picture?" Look for different opinions
- **Be observant** - "What are people saying?" Read comments, not just posts
- **Skip ads** - Look for "Sponsored"/"Ad" labels
- **Skip irrelevant** - Stay focused on query topic
- **Note patterns** - What themes/opinions keep appearing?
- **Capture diversity** - Different viewpoints = better research
- **Check dates** - Prefer recent content when relevant

**Ask yourself**: "Would a human stop here, or keep exploring?"

## Content Extraction

When reading posts/articles/videos:

```
1. Title      - Main topic
2. Key points - Important facts/claims  
3. Source     - Author/channel (credibility)
4. Date       - Recency check
5. Engagement - Likes/views (popularity)
6. Comments   - Additional perspectives (sample top 3-5)
```

## Platform Categories

### Feed-Based (Instagram, Facebook, X, Threads)
- Scroll feed for trending topics
- Search by hashtag for specific topics
- Check comments for context

**Threads quirks** (see `references/ui-threads.md`):
- Search icon is in TOP-RIGHT header, NOT in bottom tab bar
- Bottom tabs: Home, Messages, Create(+), Activity, Profile - NO search
- Search icon may not appear in accessibility tree - use screenshot to locate

### Video-Based (YouTube, TikTok, Bilibili)
- Watch first 30s to understand content
- Read description for details
- Check comment section

### Discussion-Based (Reddit, PTT)
- Read original post + top comments
- Sort by "Top" or "Best"
- Check reply threads for debates

### Messaging (LINE, WhatsApp, Telegram, WeChat)
- Navigate to contacts/chats
- Use search for specific conversations
- Handle different message types

### Dating (Tinder, Bumble, Tantan)
- Right swipe / Heart = Like
- Left swipe / X = Pass
- Handle match popup

### E-commerce (Amazon, Shopee, Momo)
- Search product → Compare prices/reviews
- Check seller ratings
- Read negative reviews for issues

### Maps/Navigation (Google Maps, Apple Maps)
- Search location → Check reviews
- Get directions, check traffic
- Save/share locations

## Output Format for Research

```
## Summary
[2-3 sentence overview]

## Key Findings
- Finding 1 (from source A)
- Finding 2 (from source B)
- Finding 3 (from source C)

## Observations
- Common themes: ...
- Varying opinions: ...
- Notable trends: ...

## Sources Reviewed
- [X] items examined
- Platforms: [list]
```

## Cross-App Tasks

For tasks spanning multiple apps:

```
1. Note key information before switching
2. Use clipboard for transferring data when possible
3. Keep track of progress across apps
4. Return to complete partially finished steps
```

## Error Recovery

```
Element not found → Scroll, wait 2s, screenshot, try pattern match
Action no effect  → Verify coords, check overlay, retry once
Unexpected screen → Screenshot, assess state, recover or report
App crashed       → Relaunch, resume from last known state
3+ failures       → STOP, report current state to user
```

### Element Not in Accessibility Tree

Some apps (e.g., Threads) have UI elements not visible to `mobile_list_elements_on_screen`.

Strategy:
```
1. Try mobile_list_elements_on_screen first
2. If target not found, use mobile_take_screenshot for visual location
3. Estimate coordinates from screenshot
4. Common positions:
   - Top-right search: ~(screen_width - 100, 100)
   - Top-right menu: ~(screen_width - 50, 100)
   - Top-left back: ~(50, 100)
```

## References

Load when needed for app-specific patterns:
- `references/package-names.md` - App package names for launching
- `references/ui-common.md` - Common UI patterns
- `references/ui-{platform}.md` - Platform-specific patterns
