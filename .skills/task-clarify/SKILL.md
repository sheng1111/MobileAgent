---
name: task-clarify
description: Convert ambiguous user requests into structured task specifications with clear parameters and success criteria. Use at the start of complex tasks to ensure requirements are understood.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
---

# Task Intake and Clarification

## Purpose

Transform ambiguous user requests into structured, actionable task specifications with clear parameters, constraints, and success criteria.

## Scope

### What This Skill Does

- Parse user intent from natural language requests
- Identify missing information and ask clarifying questions
- Define search parameters (platform, keywords, scope, time range)
- Establish interaction rules (tone, identity, forbidden topics)
- Create structured task specification for downstream skills
- Confirm understanding with user before execution

### What This Skill Does NOT Do

- Execute any app operations (no tapping, scrolling, typing)
- Perform searches or browse content
- Generate comment content (use `comment-composition-and-tone-control`)
- Extract article content (use `full-article-extraction`)

## Inputs

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_request` | string | The original user request in any language |

### Optional

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `previous_context` | object | null | Context from previous interactions |
| `known_constraints` | list | [] | Pre-established rules or preferences |

## Outputs

### Task Specification Format

```yaml
task_spec:
  task_id: string           # Unique identifier
  task_type: enum           # search | browse | comment | extract | monitor
  created_at: timestamp

  target:
    platform: string        # threads | instagram | wechat | weibo | ...
    accounts: list          # Specific accounts to follow (optional)
    keywords: list          # Search terms with variants
    scope: enum             # posts | comments | articles | all
    time_range: string      # last_24h | last_week | last_month | all_time

  constraints:
    max_items: int          # Maximum items to process
    max_scrolls: int        # Maximum scroll rounds
    max_time_minutes: int   # Time budget
    language: string        # Expected content language

  interaction:
    mode: enum              # read_only | comment_allowed
    tone: string            # neutral | supportive | professional | casual
    identity: string        # How agent should present itself
    forbidden_topics: list  # Topics to avoid

  output:
    format: enum            # summary | json | markdown | report
    save_to_file: boolean
    include_screenshots: boolean

  status: enum              # draft | confirmed | in_progress | completed
```

## Primary Workflow

### Step 1: Parse Initial Request

Extract from user message:
- Action verb (search, find, browse, comment, extract, monitor)
- Target platform (explicit or implied)
- Subject/topic/keyword
- Any stated constraints

```
User: "Help me find what people are saying about AI agents on Threads"

Parsed:
- Action: search + read comments
- Platform: Threads
- Keywords: ["AI agents"]
- Scope: posts + comments
```

### Step 2: Identify Missing Information

Check for gaps using this checklist:

| Category | Question | Default if Not Asked |
|----------|----------|---------------------|
| Platform | Which platform? | Must ask |
| Keywords | What to search for? | Must ask |
| Scope | Posts only or include comments? | posts + comments |
| Time | Recent or all time? | last_week |
| Output | Summary or full extraction? | summary |
| Interaction | Just read or also comment? | read_only |

### Step 3: Generate Clarifying Questions

If critical information is missing, ask ONE focused question at a time:

```
Good: "Should I search on Threads, Instagram, or both?"
Bad: "What platform, keywords, time range, and output format do you want?"
```

Priority order for questions:
1. Platform (if unclear)
2. Primary keyword (if missing)
3. Interaction mode (if user mentioned commenting)
4. Output format (if user needs specific deliverable)

### Step 4: Expand Keywords

Generate keyword variants for robust search:

```yaml
original: "AI agents"
variants:
  - "AI agents"
  - "AI agent"
  - "artificial intelligence agents"
  - "LLM agents"
  - "autonomous agents"
  - synonyms in target language if non-English
```

### Step 5: Apply Sensible Defaults

For unspecified parameters:

| Parameter | Default Value |
|-----------|--------------|
| max_items | 10 |
| max_scrolls | 5 |
| max_time_minutes | 15 |
| tone | neutral |
| output format | summary |
| include_screenshots | false |

### Step 6: Confirm with User

Present the task specification in user's language:

```
I'll search Threads for posts about "AI agents" and related terms.

Plan:
- Browse up to 10 posts
- Read comments on each post
- Report sentiment and key opinions
- Time limit: 15 minutes

Should I proceed, or would you like to adjust anything?
```

### Step 7: Output Structured Spec

After confirmation, output the YAML specification for downstream skills.

## Heuristics

### Platform Detection

| Keywords in Request | Likely Platform |
|--------------------|-----------------|
| "threads", "thread" (not email) | Threads |
| "IG", "gram", "reel" | Instagram |
| "微信", "公众号", "wechat" | WeChat |
| "微博", "weibo" | Weibo |
| "小红书", "RED" | Xiaohongshu |
| "tweet", "X", "twitter" | X/Twitter |

### Intent Classification

| Keywords | Task Type |
|----------|-----------|
| "find", "search", "look for" | search |
| "read", "browse", "check out" | browse |
| "comment", "reply", "respond" | comment |
| "extract", "get full content" | extract |
| "monitor", "patrol", "watch" | monitor |

### Urgency Signals

| Signal | Interpretation |
|--------|----------------|
| "quickly", "briefly" | Reduce max_items to 5 |
| "thorough", "comprehensive" | Increase max_items to 20+ |
| "recent", "latest" | time_range = last_24h |
| "trending", "hot" | Sort by engagement |

## Failure Modes & Recovery

### 1. Platform Ambiguity

**Symptom:** User doesn't specify which social platform.

**Recovery:**
- Check if context implies platform (e.g., "公众号" → WeChat)
- Ask: "Which platform should I search? (Threads / Instagram / WeChat / ...)"

### 2. Keyword Too Vague

**Symptom:** User gives very broad topic like "technology".

**Recovery:**
- Ask for specifics: "Could you narrow down what aspect of technology? (e.g., AI, smartphones, startups)"
- Suggest popular related terms

### 3. Conflicting Requirements

**Symptom:** User wants quick results but also comprehensive coverage.

**Recovery:**
- Explain trade-off: "A thorough search may take 15+ minutes. Should I do a quick scan (5 posts) or comprehensive review (20+ posts)?"

### 4. Unsupported Platform

**Symptom:** User requests platform not in our capability set.

**Recovery:**
- List supported platforms
- Suggest alternative: "I can't access LinkedIn directly. Would you like to try a similar search on X/Twitter instead?"

### 5. Language Mismatch

**Symptom:** User asks in English but wants Chinese content.

**Recovery:**
- Confirm: "You want to search for Chinese-language posts about [topic], correct?"
- Generate keywords in target language

### 6. Scope Creep

**Symptom:** User keeps adding requirements during clarification.

**Recovery:**
- Summarize current scope
- Offer to split into phases: "I can start with the search now, then we can do the commenting as a follow-up task."

## Tooling (MCP)

This skill does NOT use MCP tools directly.

It produces specifications consumed by:
- `iterative-search-and-triage` (search/browse tasks)
- `full-article-extraction` (extract tasks)
- `comment-posting-workflow` (comment tasks)
- `patrol` (monitor tasks)

## Examples

### Example 1: Simple Search Request

**User:** "What are people saying about Claude on Threads?"

**Clarification:** None needed - platform and keyword are clear.

**Output:**
```yaml
task_spec:
  task_id: ts_001
  task_type: search

  target:
    platform: threads
    keywords: ["Claude", "Claude AI", "Anthropic Claude"]
    scope: posts
    time_range: last_week

  constraints:
    max_items: 10
    max_scrolls: 5
    max_time_minutes: 15

  interaction:
    mode: read_only

  output:
    format: summary
    save_to_file: false

  status: confirmed
```

**Response to User:**
"I'll search Threads for posts about 'Claude' and report what people are saying. This will take about 10-15 minutes. Proceed?"

---

### Example 2: Comment Request (Needs Clarification)

**User:** "I want to join discussions about AI safety and add my perspective."

**Clarification Needed:**
- Platform
- Tone/identity for commenting

**Agent asks:** "Which platform would you like to comment on? And what tone should I use - professional, casual, or neutral?"

**User:** "Threads, professional tone. I'm a researcher."

**Output:**
```yaml
task_spec:
  task_id: ts_002
  task_type: comment

  target:
    platform: threads
    keywords: ["AI safety", "AI alignment", "responsible AI"]
    scope: posts

  interaction:
    mode: comment_allowed
    tone: professional
    identity: "AI safety researcher"
    forbidden_topics: []

  output:
    format: report
    include_screenshots: true

  status: confirmed
```

---

### Example 3: WeChat Public Account Browsing

**User:** "帮我看看这几个公众号的最新文章：36氪、机器之心、量子位"

**Parsed:**
- Platform: WeChat
- Action: browse specific accounts
- Output: article summaries

**Output:**
```yaml
task_spec:
  task_id: ts_003
  task_type: extract

  target:
    platform: wechat
    accounts: ["36氪", "机器之心", "量子位"]
    scope: articles
    time_range: latest

  constraints:
    max_items: 3  # Latest article from each account

  output:
    format: markdown
    save_to_file: true

  status: confirmed
```

**Response to User (in Chinese):**
"我會瀏覽這三個公眾號的最新文章，並為您提取完整內容。預計需要 10-15 分鐘。開始嗎？"

---

### Example 4: Insufficient Information

**User:** "Search for trending topics"

**Problem:** No platform, no specific topic.

**Agent asks:** "I'd be happy to search for trending topics. Could you tell me:
1. Which platform? (Threads, Instagram, Weibo, etc.)
2. Any specific area of interest? (tech, entertainment, news, etc.)"

This skill does NOT proceed until minimum requirements are met.

## Key Reminders

1. **Never execute app operations** - This skill only produces specifications
2. **One question at a time** - Don't overwhelm users with multiple questions
3. **Use sensible defaults** - Don't ask about every parameter
4. **Confirm before execution** - Always summarize the plan
5. **Match user's language** - Respond in the language they used
6. **Keep specifications complete** - All downstream skills should have what they need
