---
name: patrol
description: Patrol social media for a keyword like a coast guard hunting smugglers. Actively search, monitor, and collect opinions about a topic. AI Agent executes autonomously.
---

# Patrol Skill - AI Agent Autonomous Execution

## What is "Patrol" (海巡)

Like a coast guard actively hunting for targets, you **proactively search** for a keyword, **monitor** related posts, and **collect intelligence** about what people are saying.

```
User: "Search Threads for clawdbot and see what people think about it"

You do:
1. Launch Threads
2. Search "clawdbot"
3. Browse multiple posts mentioning it
4. Read comments and reactions
5. Report back: "Here's what people are saying about clawdbot..."
```

## CRITICAL: You Execute This Yourself

**You are the AI Agent. You execute MCP tools directly. You track state in your memory.**

```
YOU DO:
1. Call mobile_launch_app
2. Call mobile_list_elements_on_screen
3. Find target element in result
4. Call mobile_click_on_screen_at_coordinates
5. Verify by calling mobile_list_elements_on_screen again
6. Decide next action
7. Repeat until done

YOU DO NOT:
- Call Python scripts
- Ask user to run code
- Just describe what would happen
```

## Your Internal State (Track These)

As you execute, maintain these in your working memory:

```
VISITED_POSTS: []          # List of (author, title_snippet) you've seen
SCROLL_COUNT: 0            # How many times you've scrolled
POSTS_COLLECTED: []        # Data from posts you've read
CURRENT_STATE: "init"      # Where you are: init/results/post/comments
ERROR_COUNT: 0             # Consecutive errors
```

**Update these after each action!**

## Budget (Default Limits)

| Limit | Value | Stop When |
|-------|-------|-----------|
| max_posts | 5-10 | len(VISITED_POSTS) >= max_posts |
| max_scrolls | 3-5 | SCROLL_COUNT >= max_scrolls AND no new posts |
| max_errors | 3 | ERROR_COUNT >= 3 |

User can override: "patrol 10 posts" means max_posts=10

## The Patrol Flow

### Phase 1: Launch & Search

```
1. mobile_launch_app(packageName="com.instagram.barcelona")  # Threads
2. Wait 2-3 seconds
3. mobile_list_elements_on_screen → Find search icon or input

   Threads: Search is TOP-RIGHT (not bottom tabs!)
   - If not in element list → mobile_take_screenshot → look top-right
   - Approximate position: (screen_width - 80, 100)

4. mobile_click_on_screen_at_coordinates(x, y)
5. Wait 1s
6. mobile_list_elements_on_screen → Verify EditText/input focused
7. mobile_type_keys(text="YOUR_KEYWORD", submit=true)
8. Wait 2-3s for results
9. mobile_list_elements_on_screen → Verify results appeared

   CURRENT_STATE = "results"
```

### Phase 2: Scan Results

```
1. mobile_list_elements_on_screen
2. Identify post cards:
   - Look for clickable elements with text content
   - Skip: "Home", "Search", "Profile", navigation elements
   - Posts usually have: author (@username), content text

3. For each potential post:
   - Extract: author, title/content snippet
   - Check: Is (author, snippet) in VISITED_POSTS?
   - If NOT visited → This is our target

4. If no unvisited posts:
   - If SCROLL_COUNT < max_scrolls:
     mobile_swipe_on_screen(direction="up")
     SCROLL_COUNT += 1
     Wait 1s, go to step 1
   - Else: STOP, generate report
```

### Phase 3: Enter Post

```
1. Record before state:
   BEFORE_ELEMENTS = [list of current elements]

2. Click the unvisited post:
   mobile_click_on_screen_at_coordinates(post_x, post_y)

3. Wait 1-2s

4. VERIFY - mobile_list_elements_on_screen:
   - Look for: "Like", "Comment", "Share", "Reply" elements
   - If found → SUCCESS, CURRENT_STATE = "post"
   - If same as before → RETRY (max 2 times)
   - If still fails → ERROR_COUNT += 1, try next post

5. Extract post data:
   - Author: @username
   - Content: Main text
   - Engagement: likes, comments count
   - Sentiment: positive/negative/neutral about the keyword
   - Add to POSTS_COLLECTED
```

### Phase 4: Read Comments (Optional)

```
1. Find comments element:
   - Look for: "Comment", "replies", numbers like "23 replies"

2. Click to open comments:
   mobile_click_on_screen_at_coordinates(comment_x, comment_y)

3. Wait 1s

4. VERIFY:
   - mobile_list_elements_on_screen
   - Should see comment list, reply input

5. Scroll and extract:
   - mobile_swipe_on_screen(direction="up") 1-2 times
   - Extract top comments (author, text, sentiment)

6. Back to post:
   mobile_press_button(button="BACK")
   Wait 1s
   VERIFY still in post (has Like/Share buttons)
```

### Phase 5: Back to Results

```
1. mobile_press_button(button="BACK")

2. Wait 1s

3. VERIFY - mobile_list_elements_on_screen:
   - Should see post list again
   - If NOT: press BACK again, or HOME and restart

4. Mark visited:
   VISITED_POSTS.append((author, title_snippet))
   CURRENT_STATE = "results"
   ERROR_COUNT = 0  # Reset on success

5. Check budget:
   - If len(VISITED_POSTS) >= max_posts → STOP
   - Else → Go to Phase 2 (scan for next post)
```

## Verification Rules (MANDATORY)

**Every action must be verified:**

| Action | Verify By |
|--------|-----------|
| Click post | Elements changed, see Like/Comment buttons |
| Click comments | See comment list |
| Press back | Return to previous screen elements |
| Type search | Results appear |
| Scroll | Different elements in view |

**If verification fails:**
1. Retry once
2. If still fails, ERROR_COUNT += 1
3. If ERROR_COUNT >= 3, STOP and report

## Example Execution

```
User: "Search Threads for clawdbot, see what people think"

Agent:
- Keyword: "clawdbot"
- Platform: Threads
- Goal: Collect opinions about clawdbot
- Initialize: VISITED_POSTS=[], max_posts=5

[Execute tools: launch → search → type "clawdbot" → browse posts]

After visiting 5 posts, report:

## Patrol Report: clawdbot

### Summary
Searched "clawdbot" on Threads, reviewed 5 posts.

### Findings

1. @user1 - Positive
   "clawdbot is amazing for automation..."
   ❤️ 234 likes | 💬 45 comments

2. @user2 - Neutral
   "Just tried clawdbot, still figuring it out"
   ❤️ 12 likes | 💬 3 comments

3. @user3 - Positive
   "This tool saved me hours of work"
   ❤️ 89 likes | 💬 15 comments

### Overall Sentiment
- Mostly positive (3/5)
- Common praise: automation, time-saving
- Concerns: learning curve for beginners
- Discussion level: moderate activity
```

## Platform Quick Reference

| Platform | Package | Search Location |
|----------|---------|-----------------|
| Threads | com.instagram.barcelona | TOP-RIGHT icon |
| Instagram | com.instagram.android | Bottom nav "Search" tab |
| TikTok | com.zhiliaoapp.musically | Top-right icon |
| X/Twitter | com.twitter.android | Bottom nav search icon |
| Facebook | com.facebook.katana | Top search bar |
| YouTube | com.google.android.youtube | Top-right search icon |

## Error Recovery

| Error | Recovery |
|-------|----------|
| Click no effect | Wait 1s, retry. Still fails? Try different coordinates |
| Can't find search | Screenshot, look visually, estimate position |
| Back goes wrong place | Press BACK again. Still wrong? HOME + relaunch |
| App crashed | Relaunch, start from search |
| Login required | STOP, tell user to login first |

## Key Reminders

1. **YOU execute tools** - Don't just describe, actually call them
2. **Track state in memory** - VISITED_POSTS, SCROLL_COUNT, etc.
3. **Verify every action** - list_elements after every click
4. **Respect budget** - Stop when limit reached
5. **Report findings** - Summarize what people are saying about the keyword
