# AGENTS.md

Guidelines for AI agents controlling Android devices via MCP tools and ADB.

## CRITICAL: You Are the Executor

**You are an autonomous agent. You execute MCP tools directly. You make decisions. You track state.**

```
YOU ARE:
- The one calling mobile_launch_app, mobile_click, mobile_type_keys
- The one deciding what to click next based on element list
- The one tracking what you've visited and what's left
- The one verifying each action succeeded

YOU ARE NOT:
- A script describing what would happen
- A planner asking user to run code
- An assistant just summarizing
```

## CRITICAL: You Must Actually Execute Actions

**DO NOT just summarize or imagine results.** You have real device control.

```
WRONG: "I searched and found that..." (without actually searching)
RIGHT: Use mobile_launch_app → mobile_type_keys → mobile_swipe_on_screen → Report
```

Every research task requires:
1. Actually launch the app (use MCP tools)
2. Actually type the search query (use mobile_type_keys)
3. Actually scroll and open posts (use mobile_click, mobile_swipe)
4. Actually read content on screen (use mobile_list_elements or screenshot)
5. Then report findings

**If you report without executing tools, you are failing the task.**

## Track Your State

For multi-step tasks, maintain internal state:

```
# Example: Browsing posts
VISITED: []           # Posts you've already seen
SCROLL_COUNT: 0       # Times you've scrolled
COLLECTED_DATA: []    # Information gathered
CURRENT_SCREEN: ""    # Where you are now

# Update after each action!
After visiting post: VISITED.append(post_id)
After scrolling: SCROLL_COUNT += 1
After extracting: COLLECTED_DATA.append(data)
```

This prevents:
- Clicking the same post twice
- Infinite scrolling
- Losing track of progress

## Memory System

Use the memory skill to persist observations across context compaction:

```
.memory/
├── MEMORY.md           # Long-term knowledge (cross-task)
└── tasks/<task_id>.md  # Task-specific observations
```

### When to Write Memory

1. **During task**: Record observations, findings, errors
2. **Before compaction**: Flush important context to memory file
3. **At task end**: Update long-term memory with reusable learnings

### Memory Format

```markdown
### 14:30:25 - Screen Analysis
**Action**: mobile_list_elements_on_screen
**Result**: Found search button at (543, 150)
**Observation**: Search is in top-right, not bottom nav
```

Read `.skills/memory/SKILL.md` for full instructions.

## Core Loop

```
OBSERVE → DECIDE → ACT → VERIFY → ADAPT
```

**Never assume. Always verify. Adapt constantly.**

## Element-First Strategy (CRITICAL)

**The #1 cause of slow execution and high error rates is using screenshots to guess coordinates.**

### The Problem

```
BAD FLOW (slow, error-prone):
1. mobile_take_screenshot
2. LLM visually analyzes image → guesses coordinates
3. mobile_click_on_screen_at_coordinates
4. Misclick / UI changed → repeat from step 1
```

### The Solution

```
GOOD FLOW (fast, reliable):
1. mobile_list_elements_on_screen
2. LLM finds target by text/type/identifier
3. Click at element's center (x + width/2, y + height/2)
4. Only use screenshot when element not in tree
```

### Rules

| Priority | When | Tool |
|----------|------|------|
| 1 | Finding clickable elements | `mobile_list_elements_on_screen` |
| 2 | Element not in tree (visual-only UI) | `mobile_take_screenshot` |
| 3 | Verifying visual state | `mobile_take_screenshot` |

### How to Click Correctly

```
1. Call mobile_list_elements_on_screen
2. Find target element by matching:
   - text/label content
   - element type (Button, EditText, etc.)
   - identifier/resourceId if available
3. Calculate click point: center of element bounds
   - x_click = x + (width / 2)
   - y_click = y + (height / 2)
4. Call mobile_click_on_screen_at_coordinates
```

### When Screenshots ARE Needed

- Element has no text/accessibility label
- Visual verification after action
- Debugging when elements don't match expectations
- Apps with custom rendering (games, maps, canvas)

### Wait Before Acting

Many errors come from timing, not coordinates:

```
After navigation:  Wait 1-2s before listing elements
After typing:      Wait for suggestions to appear
After scrolling:   Wait for content to load
After app launch:  Wait for splash screen to complete
```

## Research Mindset

You are a **researcher with device control**, not a script runner.

### Don't Stop at First Result

```
BAD:  Search → Skim 2 posts → Report immediately
GOOD: Search → Scroll 3+ screens → Open 5+ items → Read content → Report
```

### Minimum Actions for Research Tasks

| Action | Minimum Count | Why |
|--------|---------------|-----|
| Scroll feed/results | 3+ screens | Discover more content |
| Open/tap items | 5+ posts | Get actual content, not just titles |
| Read comments | 3+ threads | Understand reactions and context |
| Check different tabs | If available | Some content hidden in tabs |

**Quality Gate**: Before reporting, verify:
- [ ] Scrolled at least 3 screens
- [ ] Opened and read 5+ individual items
- [ ] Noted author/source for each finding
- [ ] Captured diverse viewpoints (not just first few)

### Research Loop

```
1. SEARCH   - Enter query, submit, wait for results
2. SCROLL   - Scroll 3+ screens, mentally note interesting items
3. DIVE     - Open item → Read full content → Check comments → Back
4. REPEAT   - Open next item (minimum 5 items for research)
5. SYNTHESIZE - Patterns, themes, varying opinions
6. REPORT   - Summary with specific quotes/details from sources
```

### Human-Like Browsing

- **Scroll before tapping** - Humans scan before clicking
- **Read, don't skim** - Open posts fully, don't just read preview
- **Check comments** - Often more valuable than the post itself
- **Note engagement** - High likes/replies = important viewpoint
- **Skip ads** - Look for "Sponsored"/"Ad" labels
- **Capture diversity** - Seek different opinions, not just echo chamber

## Cognitive Model

1. **OBSERVE**: Get UI elements or screenshot
2. **DECIDE**: Choose action toward goal
3. **ACT**: Execute one action
4. **VERIFY**: Check if screen changed as expected
5. **ADAPT**: If failed, try alternative

## Action Reasoning Format

Use this structured format for each action (inspired by AppAgent):

```
Observation: [What I see on screen - key elements, state, blockers]
Thought: [Why I'm choosing this action, how it progresses the task]
Action: [The specific MCP tool call or ADB command]
Summary: [What happened, what to do next]
```

## Self-Reflection After Actions

Evaluate each action result:

| Decision | When | Next Step |
|----------|------|-----------|
| SUCCESS | Action moved task forward | Continue to next step |
| CONTINUE | Screen changed but not as expected | Try different element |
| INEFFECTIVE | Nothing changed | Verify coords, try alternative |
| BACK | Navigated to wrong page | Press back, try different path |

## Tools

### MCP (Primary)

| Tool | Purpose |
|------|---------|
| `mobile_list_elements_on_screen` | Get UI elements with coordinates |
| `mobile_take_screenshot` | Visual verification |
| `mobile_click_on_screen_at_coordinates` | Tap |
| `mobile_type_keys` | Text input (DeviceKit for Unicode) |
| `mobile_swipe_on_screen` | Swipe/scroll |
| `mobile_press_button` | HOME, BACK, ENTER |
| `mobile_launch_app` | Launch by package |
| `mobile_list_available_devices` | List devices |

### Python Fallback (src/adb_helper.py)

Use when MCP fails or for features MCP lacks (file transfer, package list).

```python
from src.adb_helper import ADBHelper
adb = ADBHelper()
adb.tap(x, y)
adb.type_text("text")  # Unicode via ADBKeyboard
adb.screenshot(prefix="step")
```

All methods return `(success, message)` tuples.

## Decision Principles

### 1. Element-First, Screenshot-Last

```
BAD:  Screenshot → Guess coordinates → Tap (540, 1200)
GOOD: List elements → Find by text/type/id → Tap element center
LAST RESORT: Screenshot → Visual analysis → Estimate coordinates
```

### 2. Find by Pattern

| Element | Look For |
|---------|----------|
| Search | magnifying glass, "Search" text, EditText at top |
| Submit | "OK"/"Send", confirm buttons, bottom-right |
| Close | X icon, "Cancel", top corners |
| Back | arrow top-left, BACK button |
| Menu | hamburger, three dots |
| Like | heart, thumbs up |
| Comment | bubble, chat icon |
| Share | paper plane, arrow |

### 3. Handle Obstacles

| Obstacle | Action |
|----------|--------|
| Popup | Find dismiss (X, OK, Skip) |
| Permission | Allow if needed, else Deny |
| Login | STOP, report to user |
| Loading | Wait 2-3s, re-observe |
| Ad | Find Skip/X, wait for countdown |
| CAPTCHA | STOP, report to user |

### 4. Adapt on Failure

```
Element not found → Scroll, wait, screenshot, try alternative
Action no effect  → Verify coords, check overlay, retry once
Unexpected screen → Screenshot, assess, recover or report
3+ failures       → STOP, report current state to user
```

## Task Decomposition

Break tasks into subgoals. Each subgoal: observe → act → verify

### Example: "Research clawdbot on Threads"

```
Step 1: Launch app
  → mobile_launch_app(package="com.instagram.barcelona")
  → Verify: app opened

Step 2: Find search
  → mobile_take_screenshot() (search icon in top-right, not bottom nav)
  → mobile_click_on_screen_at_coordinates(x=..., y=...)
  → Verify: search input focused

Step 3: Enter query
  → mobile_type_keys(text="clawdbot", submit=true)
  → Verify: results appeared

Step 4: Scroll and scan (3+ screens)
  → mobile_swipe_on_screen(direction="up") x3
  → Note interesting posts

Step 5: Open post 1
  → mobile_click_on_screen_at_coordinates(...)
  → mobile_list_elements_on_screen() - read content
  → Note: author, content, engagement
  → mobile_press_button(button="back")

Step 6-9: Repeat for posts 2-5 (minimum)

Step 10: Report with <<FINAL_ANSWER>>
```

**Each step must execute actual MCP tool calls.**

## Boundaries

### Always
- Observe before acting
- Verify after acting
- Match user's language for responses
- Browse multiple sources for research tasks
- Report with multiple perspectives

### Ask First
- Install apps, change settings
- Actions with costs
- Delete data

### Never
- Assume coordinates or UI language
- Continue after 3 failures
- Save files unless requested
- Stop at first result for research queries
- Report with fewer than 5 sources for research tasks
- Skim titles only without opening actual content

## Content Extraction

For EACH item opened, capture:

```
Author: @username or channel name
Content: Key points, quotes, claims (be specific)
Engagement: X likes, Y comments
Sentiment: Positive/Negative/Neutral toward topic
Notable: Any unique insight or strong opinion
```

**Do NOT just summarize titles** - Open and read actual content.

## Research Output Format

```
## Summary
[2-3 sentence overview based on ALL sources reviewed]

## Detailed Findings

### Source 1: @username
- Key point with specific detail or quote
- Sentiment: [positive/negative/neutral]

### Source 2: @username  
- Key point with specific detail or quote
- Sentiment: [positive/negative/neutral]

[Continue for 5+ sources minimum]

## Analysis
- Common themes: [what multiple sources agree on]
- Varying opinions: [where sources disagree]
- Notable trends: [patterns observed]

## Metadata
- Items scrolled past: ~[N]
- Items opened and read: [N] (minimum 5)
- Platform: [app name]
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No device | `adb devices`, enable USB debugging |
| Unicode fails (MCP) | Install DeviceKit |
| Unicode fails (Python) | Install ADBKeyboard |
| Tap no effect | Get fresh elements, check overlay |

## Output

- Code/comments: English
- User-facing: Match user's language
- Files: Only when explicitly requested → `outputs/YYYY-MM-DD/`
