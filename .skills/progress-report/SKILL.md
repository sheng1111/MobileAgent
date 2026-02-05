---
name: progress-report
description: Report task progress with evidence including screenshots, text excerpts, and data summaries. Ensures claims are backed by proof. Use periodically during long tasks or when user asks for status.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
---

# Progress Reporting and Evidence

## Purpose

Provide transparent, evidence-backed progress updates throughout task execution. Ensure every claim is supported by screenshots, text excerpts, or verifiable data.

## Scope

### What This Skill Does

- Generate structured progress reports at key milestones
- Capture and reference screenshots as evidence
- Quote relevant excerpts from discovered content
- Maintain running tallies (items processed, errors, time elapsed)
- Present candidate lists with selection criteria
- Report failures and recovery attempts honestly

### What This Skill Does NOT Do

- Execute search or browse operations (use other skills)
- Make decisions about what to search or extract
- Generate comments or content
- Modify task specifications

## Inputs

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `task_spec` | object | The task specification from task-intake |
| `current_state` | object | Current execution state |

### State Object Structure

```yaml
current_state:
  phase: enum           # searching | browsing | extracting | commenting
  items_processed: int
  items_total: int      # If known
  errors: list
  time_elapsed_seconds: int
  last_action: string
  screenshots: list     # Paths to captured screenshots
  findings: list        # Discovered items with metadata
```

## Outputs

### Progress Report Format

```yaml
progress_report:
  task_id: string
  timestamp: string
  phase: string

  metrics:
    items_completed: int
    items_remaining: int
    errors_count: int
    time_elapsed: string
    estimated_remaining: string  # Optional

  evidence:
    screenshots:
      - path: string
        description: string
        timestamp: string
    excerpts:
      - source: string
        quote: string
        relevance: string

  findings_summary:
    candidates_found: int
    top_candidates:
      - title: string
        source: string
        why_relevant: string
        engagement: object  # likes, comments, shares

  issues:
    - type: string
      description: string
      recovery_action: string

  next_steps: string
  user_decision_needed: boolean
  decision_prompt: string  # If user decision needed
```

## Primary Workflow

### Step 1: Milestone Detection

Report at these milestones:
- Task started
- Every 3-5 items processed
- Platform/section change
- Error encountered
- Significant finding discovered
- Task blocked (needs user input)
- Task completed

### Step 2: Capture Evidence

For each reportable event:

```
1. Take screenshot if visual context needed
   → mobile_save_screenshot(device, saveTo="outputs/{date}/evidence_{n}.png")

2. Extract relevant text quotes
   → Copy key phrases that justify decisions

3. Record metrics
   → items processed, time, errors
```

### Step 3: Structure the Report

**Concise format for mid-task updates:**

```
Progress: 4/10 posts reviewed (40%)
Time: 3 min elapsed

Found so far:
- Post by @user1: "AI agents are changing..." (127 likes)
- Post by @user2: Discusses Claude vs GPT (45 comments)

No issues. Continuing...
```

**Detailed format for milestones:**

```
=== Progress Report ===
Task: Search "AI agents" on Threads
Phase: Browsing results
Status: In progress

Metrics:
- Posts reviewed: 7/10
- Comments read: 23
- Time elapsed: 8 minutes
- Errors: 0

Key Findings:
1. [HIGH RELEVANCE] Post by @techguru
   - Quote: "AI agents are finally delivering on promises"
   - 234 likes, 67 comments
   - Screenshot: evidence_003.png

2. [MEDIUM RELEVANCE] Post by @skeptic99
   - Quote: "Overhyped, just chatbots with extra steps"
   - 89 likes, 122 comments (heated discussion)
   - Screenshot: evidence_004.png

Next: Continue to posts 8-10, then summarize findings.
```

### Step 4: Handle User Decisions

When task is blocked or options exist:

```
=== Decision Needed ===

Situation: Found 3 posts matching criteria. Two require scrolling
through 50+ comments each.

Options:
A) Deep dive into top 2 posts (comments analysis) - ~10 min more
B) Quick scan remaining posts instead - ~3 min more
C) Stop here and summarize what we have

Which would you prefer?
```

### Step 5: Final Report

At task completion:

```
=== Task Complete ===
Task: Search "AI agents" on Threads
Duration: 12 minutes

Summary:
- Posts reviewed: 10
- Comments read: 47
- Screenshots saved: 5

Key Findings:
1. Positive sentiment dominates (70% of engagement)
2. Main concerns: privacy, job displacement
3. Most mentioned products: Claude, ChatGPT, AutoGPT

Top 3 Candidates (for follow-up):
1. Post by @airesearcher - Deep technical discussion
2. Post by @ethicist - AI safety debate with 200+ comments
3. Post by @developer - Real-world agent usage examples

Evidence Files:
- outputs/2024-01-15/evidence_001.png through evidence_005.png
- outputs/2024-01-15/threads_search_results.json

Recommendations:
- Post #2 has most engagement for potential commenting
- Consider monitoring @airesearcher for future posts
```

## Heuristics

### When to Take Screenshots

| Situation | Screenshot? | Reason |
|-----------|------------|--------|
| Search results page | Yes | Proves search was executed |
| High-relevance post | Yes | Evidence for recommendation |
| Error state | Yes | Debugging reference |
| Comment posted | Yes | Proof of action |
| Normal browsing | No | Reduces noise |

### Relevance Scoring

```
HIGH: Keyword in title + 50+ engagement + discussion in comments
MEDIUM: Keyword in content OR 20+ engagement
LOW: Related topic but no direct keyword match
SKIP: Irrelevant despite appearing in search
```

### Error Severity

| Type | Severity | Report Immediately? |
|------|----------|-------------------|
| Element not found | Low | No, retry first |
| Navigation stuck | Medium | After 2 retries |
| App crash | High | Yes |
| Login required | High | Yes |
| Rate limited | High | Yes |

## Failure Modes & Recovery

### 1. No Screenshots Saved

**Symptom:** Screenshot capture fails silently.

**Recovery:**
- Check `outputs/` directory exists
- Fallback to text-only evidence
- Note in report: "Screenshot capture failed, text evidence only"

### 2. Metrics Drift

**Symptom:** Reported numbers don't match actual progress.

**Recovery:**
- Re-count from findings list
- Include discrepancy note
- Trust actual findings over counters

### 3. Evidence Lost on Error

**Symptom:** Task crashes, losing collected evidence.

**Recovery:**
- Save evidence incrementally (after each item)
- Report last known good state
- Offer to resume from checkpoint

### 4. Report Overload

**Symptom:** Too many reports interrupt user flow.

**Recovery:**
- Batch updates (every 3-5 items)
- Only immediate reports for errors
- Use concise format for routine updates

### 5. Vague Findings

**Symptom:** "Found some relevant posts" without specifics.

**Recovery:**
- Always include at least one quote
- Always include engagement numbers
- Always explain WHY it's relevant

### 6. False Completion

**Symptom:** Report "completed" but items remain.

**Recovery:**
- Cross-check items_completed vs task_spec.max_items
- Don't report completion until verified
- List remaining items if stopped early

## Tooling (MCP)

### Screenshot Capture

```
Tool: mobile_save_screenshot (mobile-mcp)
Parameters:
  device: string
  saveTo: "outputs/YYYY-MM-DD/evidence_{n}.png"
```

### File Operations

```
Tool: write_file (filesystem)
Use: Save JSON findings, reports

Tool: create_directory (filesystem)
Use: Ensure outputs directory exists
```

### Screen State (for context)

```
Tool: get_screen_summary (mobile-macro)
Use: Capture current screen state as text evidence
```

## Examples

### Example 1: Mid-Task Update

**Context:** User asked to search for AI news. 5 posts reviewed.

**Report:**
```
Progress: 5/10 posts (halfway)
Time: 4 min

Highlights:
- Found 2 highly relevant posts about Claude
- 1 post has 150+ comments worth deep-diving
- No errors

Continuing to next 5 posts...
```

---

### Example 2: Error Encountered

**Context:** Navigation stuck after back press.

**Report:**
```
⚠️ Issue Encountered

Problem: "Back" button didn't return to search results.
Current screen: Unknown app state
Screenshot: evidence_007.png

Recovery attempted:
1. Retry back button - Failed
2. Press HOME - Success, returned to launcher

Impact: Lost position in results. Will restart search from beginning.

Time lost: ~2 minutes
Posts affected: Need to re-review posts 6-8

Continuing with fresh search...
```

---

### Example 3: Decision Point

**Context:** Found posts but user's query was ambiguous.

**Report:**
```
Clarification Needed

I found 12 posts about "agents" but they fall into two categories:

Category A: AI agents / LLM agents (8 posts)
- Technical discussions about autonomous AI
- Average 45 comments per post

Category B: Real estate agents (4 posts)
- Property listings and agent promotions
- Average 5 comments per post

Which category should I focus on?
(Reply "A" for AI agents, "B" for real estate, or "both")
```

---

### Example 4: Completion Report (Chinese User)

**Context:** Task was to browse WeChat accounts.

**Report:**
```
=== 任務完成 ===
任務：瀏覽 36氪、機器之心、量子位 公眾號
耗時：11 分鐘

結果摘要：
- 文章閱讀：3 篇（每個帳號最新 1 篇）
- 截圖保存：3 張
- 錯誤：0

主要發現：
1. 36氪：「2024年AI融資趨勢分析」
   - 重點：AI行業融資額較去年增長42%
   - 完整內容已保存

2. 機器之心：「Claude 3 能力評測」
   - 重點：在數學和程式碼方面表現突出
   - 含多張對比圖表

3. 量子位：「AI Agent 實戰經驗分享」
   - 重點：五個落地案例剖析
   - 有開發者訪談

輸出文件：
- outputs/2024-01-15/wechat_articles.json
- outputs/2024-01-15/wechat_articles.md

需要我進一步分析哪篇文章嗎？
```

## Key Reminders

1. **Evidence or it didn't happen** - Every claim needs a screenshot, quote, or data point
2. **Numbers must match** - Items reported = items actually processed
3. **Explain relevance** - Don't just list, explain WHY each finding matters
4. **Report errors honestly** - Don't hide failures, explain and recover
5. **Match user's language** - Reports should be in user's preferred language
6. **Save incrementally** - Don't wait until the end to save evidence
7. **Structured over verbose** - Use clear formats, not walls of text
