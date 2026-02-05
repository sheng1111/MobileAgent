---
name: comment-scan
description: Deep-read and analyze comments on a post/article. Identify consensus, controversies, common questions, and notable quotes. Use when user wants to understand public opinion on a specific post.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
compatibility: Requires mobile-mcp MCP server, connected Android device with target app open to post with comments
---

# Comment Reading and Sentiment Scan

## Purpose

Thoroughly read and analyze comments on a specific post or article. Extract sentiment patterns, identify consensus and controversy points, find common questions, and surface notable quotes for insight or response planning.

## Scope

### What This Skill Does

- Navigate to a specific post's comment section
- Scroll through and read comments systematically
- Categorize comments by sentiment (positive/negative/neutral)
- Identify consensus points (what most agree on)
- Surface controversies (heated debates, opposing views)
- Extract common questions from commenters
- Note highly-engaged comments (many replies/likes)
- Compile structured sentiment report

### What This Skill Does NOT Do

- Search for posts (use `iterative-search-and-triage`)
- Extract full article content (use `full-article-extraction`)
- Generate comment responses (use `comment-composition-and-tone-control`)
- Post comments (use `comment-posting-workflow`)
- Read multiple posts (one post per invocation)

## Inputs

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | string | Platform name |
| `post_identifier` | object | How to find the post (see below) |

### Post Identifier Options

```yaml
# Option 1: Direct URL (if supported)
post_identifier:
  type: url
  value: "https://threads.net/@user/post/abc123"

# Option 2: From search position
post_identifier:
  type: search_result
  keyword: "AI agents"
  position: 3  # 3rd result from search

# Option 3: By title/author (for returning to known post)
post_identifier:
  type: content_match
  title_contains: "Building agents with Claude"
  author: "@techdev"
```

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_comments` | int | 50 | Maximum comments to read |
| `max_scrolls` | int | 10 | Maximum scrolls in comment section |
| `include_replies` | boolean | true | Expand and read reply threads |
| `min_likes_for_notable` | int | 10 | Threshold for "notable" comment |

## Outputs

### Comment Analysis Report

```yaml
comment_analysis:
  post_info:
    platform: string
    title: string
    author: string
    post_date: string
    total_comments: int  # Displayed count
    comments_read: int   # Actually processed

  summary:
    overall_sentiment: enum  # positive | negative | mixed | neutral
    sentiment_confidence: float  # 0-1
    one_line_summary: string

  sentiment_breakdown:
    positive:
      count: int
      percentage: float
      themes: list
      sample_quotes:
        - quote: string
          author: string
          likes: int
    negative:
      count: int
      percentage: float
      themes: list
      sample_quotes: list
    neutral:
      count: int
      percentage: float

  consensus_points:
    - point: string
      support_evidence: string
      mentioned_by: int  # Number of commenters

  controversy_points:
    - topic: string
      side_a:
        position: string
        sample_comment: string
      side_b:
        position: string
        sample_comment: string
      heat_level: enum  # mild | moderate | heated

  common_questions:
    - question: string
      asked_by: int  # Number of similar questions
      answered: boolean
      answer_summary: string  # If answered in comments

  notable_comments:
    - author: string
      content: string
      likes: int
      replies: int
      why_notable: string  # "high engagement" / "expert opinion" / "viral"

  discussion_patterns:
    reply_depth_avg: float
    most_active_thread_topic: string
    author_participation: boolean  # Did post author reply?
    author_replies_count: int

  evidence:
    screenshots: list
    scroll_count: int
    time_spent_seconds: int
```

## Primary Workflow

### Phase 1: Navigate to Post

```
If post_identifier.type == "search_result":
  1. Launch platform app
  2. Search for keyword
  3. Navigate to Nth result
  4. Verify correct post (title/author match)

If post_identifier.type == "content_match":
  1. Search for partial title
  2. Find matching post
  3. Verify author matches
```

### Phase 2: Enter Comment Section

```
1. Locate comment section
   - Look for "Comments", "回复", "留言" or comment count
   → find_and_click(text="comments") OR find_and_click(text="View all X comments")

2. Wait for comments to load
   → smart_wait(timeout=3)

3. Note total comment count from UI
```

### Phase 3: Read Comments Systematically

```
Initialize:
  comments_read = []
  scroll_count = 0

Loop:
  1. Get visible comments
     → mobile_list_elements_on_screen()

  2. For each new comment (not in comments_read):
     - Extract author name
     - Extract comment text
     - Extract engagement (likes, replies count)
     - Classify sentiment
     - Check for questions (ends with ?)
     - Add to comments_read

  3. Check for "See replies" or similar
     - If include_replies=true, expand and read replies
     - Track reply depth

  4. Scroll to load more comments
     → mobile_swipe_on_screen(direction="up")
     → scroll_count++

  5. Check stop conditions:
     - scroll_count >= max_scrolls
     - comments_read >= max_comments
     - No new comments after scroll

  6. Continue loop if not stopped
```

### Phase 4: Sentiment Classification

For each comment, apply sentiment rules:

```
POSITIVE indicators:
  - Praise words: "great", "love", "amazing", "helpful", "太棒了", "讚"
  - Support: "agree", "same", "正確", "同意"
  - Gratitude: "thanks", "感謝"
  - Emoji: 👍 ❤️ 🙌 🎉

NEGATIVE indicators:
  - Criticism: "wrong", "bad", "terrible", "disagree", "不同意", "差"
  - Frustration: "annoying", "waste", "失望"
  - Dismissal: "pointless", "useless", "沒用"
  - Emoji: 👎 😤 😒

NEUTRAL:
  - Questions without opinion
  - Pure information/facts
  - "I wonder...", "What about..."
```

### Phase 5: Pattern Identification

```
Consensus Detection:
  - Group comments by key themes/phrases
  - If >30% mention same point positively → consensus
  - Example: 5/15 comments say "finally a good explanation" → consensus on clarity

Controversy Detection:
  - Look for direct disagreements ("No, that's wrong", "I disagree")
  - Look for reply chains with opposing views
  - Long reply threads often indicate debate

Question Extraction:
  - Comments ending with "?"
  - "How do you...", "What is...", "Does anyone know..."
  - Group similar questions

Notable Comments:
  - Likes > min_likes_for_notable
  - Has many replies
  - Author is verified/known
  - Particularly articulate point
```

### Phase 6: Compile Report

```
1. Calculate sentiment percentages
2. Select best sample quotes for each sentiment
3. Summarize consensus points
4. Structure controversies with both sides
5. List unique questions
6. Highlight notable comments
7. Add overall summary
```

### Phase 7: Exit and Return

```
1. Navigate back to post (if in comment detail)
2. Navigate back to search results (if needed for next skill)
   → navigate_back()
```

## Heuristics

### Sentiment Classification Rules

| Pattern | Sentiment | Confidence |
|---------|-----------|------------|
| Contains praise + no criticism | Positive | High |
| Contains criticism + no praise | Negative | High |
| Mixed signals | Neutral/Mixed | Medium |
| Question only | Neutral | High |
| Emoji only (positive) | Positive | Medium |
| Single word "nice", "good" | Positive | Low |

### Notable Comment Criteria

```
Score = (likes * 2) + (replies * 3)

If score > 50: Definitely notable
If score > 20: Consider notable
If score < 10: Only notable if content exceptional
```

### Controversy Indicators

- Direct contradiction: "Actually no", "That's incorrect"
- Heated language: ALL CAPS, multiple !!!
- Long reply chains (5+ back-and-forth)
- Significant engagement on opposing comments

### When to Expand Replies

```
Expand if:
  - Reply count > 5 (likely discussion)
  - Top-level comment is controversial
  - User specifically asked to understand debates

Don't expand if:
  - Reply count < 3 (likely simple responses)
  - Reaching scroll budget
  - Replies are mostly emoji/short reactions
```

## Failure Modes & Recovery

### 1. Comment Section Doesn't Load

**Symptom:** Comments indicator shows count but section empty.

**Recovery:**
- Wait longer (some platforms lazy-load)
- Scroll within post to trigger load
- Try "View comments" link if visible
- Report: "Comments failed to load"

### 2. Comments Behind Login

**Symptom:** "Log in to see comments" message.

**Recovery:**
- Report limitation
- Try scrolling to see if any are visible
- Return what's available

### 3. Reply Expansion Fails

**Symptom:** "View replies" clicked but nothing expands.

**Recovery:**
- Try clicking again
- Skip this thread, continue with others
- Note in report: "Some replies couldn't be expanded"

### 4. Infinite Comment Scroll

**Symptom:** New comments keep loading forever.

**Recovery:**
- Enforce max_comments strictly
- Check for duplicate comments (loop detection)
- Stop after max_scrolls regardless

### 5. Mixed Language Comments

**Symptom:** Comments in multiple languages confuse sentiment.

**Recovery:**
- Apply sentiment rules for detected language
- Group by language in report if needed
- Note multilingual nature in summary

### 6. Mostly Emoji/Sticker Comments

**Symptom:** Comments are 90% reactions, no text.

**Recovery:**
- Classify emoji sentiment
- Report: "Discussion is mostly reaction-based"
- Lower confidence on sentiment analysis

## Tooling (MCP)

### Primary Tools

| Tool | Use Case |
|------|----------|
| `find_and_click` | Navigate to comments, expand replies |
| `smart_wait` | Wait for comments to load |
| `scroll_and_find` | Scroll through comments |
| `navigate_back` | Return to post/search |
| `get_screen_summary` | Quick text extraction |

### Secondary Tools

| Tool | Use Case |
|------|----------|
| `mobile_list_elements_on_screen` | Get all visible comment text |
| `mobile_swipe_on_screen` | Scroll comment section |
| `mobile_save_screenshot` | Capture notable exchanges |

### Workflow Pattern

```
1. Navigate to post
2. find_and_click(text="comments") OR find_and_click(text="View all")
3. smart_wait(timeout=3)
4. Loop:
   a. mobile_list_elements_on_screen() → extract comments
   b. mobile_swipe_on_screen(direction="up") → load more
   c. Check termination conditions
5. navigate_back()
```

## Examples

### Example 1: Tech Post Analysis

**Input:**
```yaml
platform: threads
post_identifier:
  type: content_match
  title_contains: "Claude is better than GPT"
max_comments: 30
```

**Output:**
```yaml
comment_analysis:
  post_info:
    platform: threads
    title: "Hot take: Claude is better than GPT for coding"
    author: "@devopinionated"
    total_comments: 89
    comments_read: 30

  summary:
    overall_sentiment: mixed
    sentiment_confidence: 0.75
    one_line_summary: "Divided opinions with strong feelings on both sides; coding ability is main debate point"

  sentiment_breakdown:
    positive:
      count: 12
      percentage: 40
      themes: ["coding ability", "reasoning", "less hallucination"]
      sample_quotes:
        - quote: "Switched to Claude last month, night and day difference for code review"
          author: "@codemaster"
          likes: 34
    negative:
      count: 10
      percentage: 33
      themes: ["speed", "availability", "context window needed"]
      sample_quotes:
        - quote: "Claude is too slow and the rate limits kill productivity"
          author: "@speedcoder"
          likes: 28
    neutral:
      count: 8
      percentage: 27

  controversy_points:
    - topic: "Coding assistance quality"
      side_a:
        position: "Claude produces cleaner, more maintainable code"
        sample_comment: "Claude actually understands architecture, GPT just writes functions"
      side_b:
        position: "GPT-4 with good prompting matches or exceeds Claude"
        sample_comment: "With the right system prompt, GPT-4 is just as good"
      heat_level: moderate

  common_questions:
    - question: "Which is better for [specific language]?"
      asked_by: 4
      answered: true
      answer_summary: "Consensus: Claude for Python/JS, mixed for others"

  notable_comments:
    - author: "@airesearcher"
      content: "I've benchmarked both extensively. Claude wins on code quality but loses on speed. Depends on your use case."
      likes: 67
      replies: 12
      why_notable: "High engagement, balanced perspective"
```

---

### Example 2: Chinese Platform (WeChat Article)

**Input:**
```yaml
platform: wechat
post_identifier:
  type: content_match
  title_contains: "AI大模型"
  author: "机器之心"
max_comments: 20
```

**Output:**
```yaml
comment_analysis:
  post_info:
    platform: wechat
    title: "2024年AI大模型发展趋势"
    author: "机器之心"
    comments_read: 20

  summary:
    overall_sentiment: positive
    one_line_summary: "读者普遍认可分析质量，关注具体落地场景"

  sentiment_breakdown:
    positive:
      count: 14
      percentage: 70
      themes: ["分析深入", "数据详实", "关注实际应用"]
      sample_quotes:
        - quote: "终于有人认真分析落地场景了，不是只吹概念"
          author: "用户A"
          likes: 23

  common_questions:
    - question: "哪些行业最适合落地？"
      asked_by: 3
      answered: false
```

---

### Example 3: Low Engagement Post

**Input:**
```yaml
platform: threads
post_identifier:
  type: search_result
  keyword: "AI agents"
  position: 5
max_comments: 50
```

**Output:**
```yaml
comment_analysis:
  post_info:
    total_comments: 3
    comments_read: 3

  summary:
    overall_sentiment: neutral
    sentiment_confidence: 0.4
    one_line_summary: "Minimal discussion; insufficient data for meaningful sentiment analysis"

  sentiment_breakdown:
    positive:
      count: 1
    negative:
      count: 0
    neutral:
      count: 2

  consensus_points: []
  controversy_points: []
  common_questions: []

  notable_comments: []

  evidence:
    note: "Post has very limited engagement. Consider selecting a different candidate for deeper analysis."
```

## Key Reminders

1. **One post per invocation** - Don't try to analyze multiple posts
2. **Comments, not article** - This skill reads comments, not main content
3. **Scroll systematically** - Don't skip sections of comments
4. **Quote accurately** - Exact quotes, not paraphrased
5. **Note what you didn't read** - If comments_read < total_comments, say so
6. **Identify author replies** - These are often important context
7. **Sentiment requires evidence** - Every sentiment claim needs example
8. **Exit cleanly** - Return to expected screen state for next skill
