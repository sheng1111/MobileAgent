---
name: search-triage
description: Multi-round search with keyword variants on social platforms. Browse results, open promising items, check engagement, and produce a ranked candidate list. Use when user needs comprehensive search results.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
compatibility: Requires mobile-mcp MCP server, connected Android device with target social app installed
---

# Iterative Search and Triage

## Purpose

Perform human-like exploratory search: multiple search rounds with keyword variants, opening promising items, checking comment activity, backing out to list, continuing until budget exhausted or sufficient candidates found.

## Scope

### What This Skill Does

- Execute multi-round searches with keyword variants
- Open and inspect individual posts/articles
- Assess engagement signals (likes, comments, shares)
- Return to list and continue browsing
- Track visited items to avoid re-processing
- Produce ranked candidate list with evidence

### What This Skill Does NOT Do

- Deep-read all comments (use `comment-reading-and-sentiment-scan`)
- Extract full article content (use `full-article-extraction`)
- Generate or post comments (use comment skills)
- Make final decisions (presents candidates for user/next skill)

## Inputs

### From Task Specification

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `platform` | string | Yes | Target platform |
| `keywords` | list | Yes | Search terms with variants |
| `scope` | string | No | "posts" / "articles" / "all" (default: all) |
| `time_range` | string | No | Time filter to apply |
| `max_items` | int | No | Maximum items to process (default: 10) |
| `max_scrolls` | int | No | Maximum scroll rounds per search (default: 5) |
| `max_time_minutes` | int | No | Time budget (default: 15) |

### Runtime Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `relevance_threshold` | float | Minimum relevance score to keep (0-1, default: 0.3) |
| `min_engagement` | int | Minimum likes+comments to consider (default: 5) |

## Outputs

### Candidate List Format

```yaml
search_results:
  task_id: string
  platform: string
  search_duration_seconds: int

  statistics:
    searches_performed: int
    items_scanned: int
    items_opened: int
    candidates_found: int

  keywords_used:
    - keyword: string
      results_count: int
      useful_results: int

  candidates:
    - rank: int
      title: string
      author: string
      url: string  # If available
      platform_id: string  # Post ID

      relevance:
        score: float  # 0-1
        keyword_matches: list
        reason: string

      engagement:
        likes: int
        comments: int
        shares: int
        engagement_rate: string  # "high" / "medium" / "low"

      content_preview: string  # First 200 chars
      has_active_discussion: boolean

      evidence:
        screenshot: string  # Path if captured
        excerpt: string

  rejected:
    count: int
    reasons:
      - reason: string
        count: int

  errors: list
  recommendations: string
```

## Primary Workflow

### Phase 1: Prepare Search Variants

Before searching, expand keywords:

```
Original: "AI agents"

Variants:
- "AI agents" (exact)
- "AI agent" (singular)
- "LLM agents"
- "autonomous agents"
- "Claude agent" (if relevant)
- 中文: "AI智能体" (if targeting Chinese content)
```

### Phase 2: Execute First Search

```
1. Launch platform app
   → launch_and_wait(package="com.instagram.barcelona", wait_text="Search")

2. Navigate to search
   → find_and_click(text="Search") OR platform-specific location

3. Enter search keyword
   → type_and_submit(text="AI agents", submit=true)

4. Wait for results
   → smart_wait(text="post" OR text="result", timeout=5)

5. Record initial view
   → get_screen_summary()
```

### Phase 3: Scan Results

```
For each visible item:
  1. Extract visible info (title, author, preview, engagement indicators)
  2. Quick relevance check:
     - Does title/preview contain keywords?
     - Is engagement above threshold?
     - Is it recent enough?
  3. Decision:
     - OPEN if: keyword match + decent engagement
     - SKIP if: no match or very low engagement
     - MARK if: maybe relevant, check later if time permits
```

### Phase 4: Open and Inspect

```
For items marked OPEN:
  1. Click to open
     → find_and_click(text=item_title)

  2. Wait for load
     → smart_wait(text="comment" OR text="like", timeout=3)

  3. Scan content:
     - Read full visible text
     - Note comment count
     - Check if comments seem active (visible comment preview)

  4. Quick scroll (1-2 times) to see more content
     → mobile_swipe_on_screen(direction="up")

  5. Record findings

  6. BACK to results
     → navigate_back(expected_text="Search")

  7. Mark as VISITED to avoid re-checking
```

### Phase 5: Scroll and Continue

```
After processing visible items:
  1. Scroll down to load more
     → mobile_swipe_on_screen(direction="up", distance=400)

  2. Wait for new content
     → smart_wait(timeout=1.5)

  3. Check for new items (compare with visited list)

  4. Repeat Phase 3-4 for new items

  5. Continue until:
     - max_scrolls reached
     - max_items processed
     - no new content loading
```

### Phase 6: Next Keyword Round

```
If more keywords to try AND budget remaining:
  1. Clear search OR navigate to fresh search
  2. Enter next keyword variant
  3. Repeat Phases 3-5
  4. De-duplicate (same posts may appear for different keywords)
```

### Phase 7: Rank and Report

```
1. Sort candidates by relevance score
2. Filter below threshold
3. Generate evidence (screenshots of top candidates)
4. Compile final candidate list
5. Add recommendations for next steps
```

## Heuristics

### Relevance Scoring

```python
def calculate_relevance(item, keywords):
    score = 0.0

    # Title match: +0.4
    if any(kw.lower() in item.title.lower() for kw in keywords):
        score += 0.4

    # Content match: +0.3
    if any(kw.lower() in item.content.lower() for kw in keywords):
        score += 0.3

    # Engagement bonus: +0.2
    if item.engagement > 50:
        score += 0.2
    elif item.engagement > 20:
        score += 0.1

    # Recency bonus: +0.1
    if item.is_recent:  # Within time_range
        score += 0.1

    return min(score, 1.0)
```

### When to Skip vs Open

| Signal | Action |
|--------|--------|
| Keyword in title + comments > 10 | OPEN |
| Keyword in title + no comments | OPEN (quick look) |
| No keyword but high engagement | OPEN (might be relevant) |
| No keyword + low engagement | SKIP |
| Already visited | SKIP |
| Clearly off-topic (e.g., ad) | SKIP |

### Scroll Budget Allocation

```
If 3 keywords and max_scrolls=5:
  - Keyword 1: 3 scrolls (primary term)
  - Keyword 2: 1 scroll (variant)
  - Keyword 3: 1 scroll (variant)
```

### De-duplication

Track by:
1. Post ID (if available)
2. Author + first 50 chars of content
3. Exact title match

### Stop Conditions

- `max_items` reached
- `max_scrolls` reached
- `max_time_minutes` exceeded
- Same content appearing (infinite scroll loop)
- 3 consecutive scrolls with no new relevant items

## Failure Modes & Recovery

### 1. Search Returns No Results

**Symptom:** Platform shows "No results" or empty state.

**Recovery:**
- Try next keyword variant
- Remove special characters from keyword
- Try broader term
- Report to user if all variants fail

### 2. Items Don't Open

**Symptom:** Clicking on item doesn't navigate to detail view.

**Recovery:**
- Try clicking on different part of item (title vs. image)
- Check if item is an ad (skip)
- Wait longer for tap to register
- After 2 failures, skip and note error

### 3. Can't Return to List

**Symptom:** Back press doesn't return to search results.

**Recovery:**
- Try pressing BACK again
- Check if in comments section (need extra back)
- If stuck, go HOME and restart search
- Note which items were lost

### 4. Infinite Scroll Loop

**Symptom:** Same items keep appearing after scroll.

**Recovery:**
- Check screen hash (if unchanged, stop scrolling)
- Note: "End of results reached"
- Move to next keyword

### 5. Login/Auth Wall

**Symptom:** Platform asks to log in to see more.

**Recovery:**
- Report: "Additional results require login"
- Stop current search
- Return found candidates so far

### 6. Rate Limited

**Symptom:** "Slow down" message or search disabled.

**Recovery:**
- Wait 30-60 seconds
- Reduce scroll frequency
- If persists, stop and report

## Tooling (MCP)

### Primary Tools (mobile-macro)

| Tool | Use Case |
|------|----------|
| `launch_and_wait` | Start platform app |
| `find_and_click` | Navigate to search, open items |
| `type_and_submit` | Enter search keywords |
| `smart_wait` | Wait for results, content load |
| `scroll_and_find` | Load more results |
| `navigate_back` | Return to list after viewing item |
| `get_screen_summary` | Quick state check |

### Secondary Tools (mobile-mcp)

| Tool | Use Case |
|------|----------|
| `mobile_list_elements_on_screen` | Get all visible items |
| `mobile_swipe_on_screen` | Manual scroll when needed |
| `mobile_save_screenshot` | Capture evidence |

### Usage Pattern

```
1. Launch: launch_and_wait(package, wait_text="Search")
2. Search: find_and_click(text="Search")
3. Type: type_and_submit(text=keyword)
4. Get elements: mobile_list_elements_on_screen
5. Click item: find_and_click(text=item_title)
6. Read: get_screen_summary()
7. Back: navigate_back()
8. Scroll: mobile_swipe_on_screen(direction="up")
9. Repeat 4-8
```

## Examples

### Example 1: Basic Threads Search

**Input:**
```yaml
platform: threads
keywords: ["AI agents", "LLM agents"]
max_items: 10
max_scrolls: 5
```

**Execution Log:**
```
[1] Launched com.instagram.barcelona
[2] Found search icon (top-right area)
[3] Searched "AI agents"
[4] Results loaded - 6 visible posts
[5] Scanned posts:
    - Post 1: "My AI agent failed..." - 23 likes, relevant → OPEN
    - Post 2: "Best travel agents in NYC" - 45 likes, not relevant → SKIP
    - Post 3: "Building agents with Claude" - 89 likes, relevant → OPEN
[6] Opened Post 1, read content, 12 comments, BACK
[7] Opened Post 3, read content, active discussion, BACK
[8] Scrolled, 4 new posts visible
[9] ...continued...
[15] Switched to "LLM agents" keyword
[16] 3 new results (2 duplicates filtered)
[20] Budget exhausted, compiling results
```

**Output:**
```yaml
search_results:
  platform: threads
  search_duration_seconds: 420

  statistics:
    searches_performed: 2
    items_scanned: 18
    items_opened: 7
    candidates_found: 5

  candidates:
    - rank: 1
      title: "Building agents with Claude"
      author: "@techdev"
      relevance:
        score: 0.9
        keyword_matches: ["AI agents", "Claude"]
        reason: "Direct keyword match, high engagement, active discussion"
      engagement:
        likes: 89
        comments: 34
        engagement_rate: "high"
      has_active_discussion: true

    - rank: 2
      title: "My AI agent failed - lessons learned"
      author: "@aibuilder"
      relevance:
        score: 0.7
        keyword_matches: ["AI agent"]
        reason: "Experience report, moderate engagement"
      engagement:
        likes: 23
        comments: 12

    # ... more candidates ...

  recommendations: "Candidate #1 has most active discussion, recommend for comment-reading skill"
```

---

### Example 2: WeChat Article Search

**Input:**
```yaml
platform: wechat
keywords: ["AI大模型", "人工智能"]
scope: articles
max_items: 8
```

**Note:** WeChat search works differently - use "搜一搜" feature.

**Output:**
```yaml
search_results:
  platform: wechat

  candidates:
    - rank: 1
      title: "2024年AI大模型发展趋势报告"
      author: "机器之心"
      relevance:
        score: 0.95
        reason: "Exact keyword match, authoritative source"
      content_preview: "本报告详细分析了2024年上半年AI大模型领域的..."
```

---

### Example 3: No Results Scenario

**Input:**
```yaml
platform: threads
keywords: ["xyznonexistentterm123"]
```

**Output:**
```yaml
search_results:
  platform: threads

  statistics:
    searches_performed: 1
    items_scanned: 0
    candidates_found: 0

  keywords_used:
    - keyword: "xyznonexistentterm123"
      results_count: 0
      useful_results: 0

  candidates: []

  errors:
    - type: NO_RESULTS
      keyword: "xyznonexistentterm123"
      message: "No results found for this keyword"

  recommendations: "Try different keywords. Suggestions: broaden the search term or check spelling."
```

## Key Reminders

1. **Human-like browsing** - Don't just scan metadata; actually open and look at items
2. **Track visited items** - Never process same item twice
3. **Keyword variants matter** - First keyword may miss relevant content
4. **Back to list** - Always return to results after viewing item
5. **Evidence for candidates** - Each candidate needs reason + engagement data
6. **Respect budgets** - Stop when max_items/scrolls/time reached
7. **De-duplicate across keywords** - Same post can appear in multiple searches
8. **Report rejected items** - Helps calibrate thresholds
