---
name: memory
description: Task memory system for recording observations, findings, and learnings during task execution. Short-term memory per task, long-term memory across tasks.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
compatibility: All CLI tools (codex, claude, gemini)
---

# Memory Skill

## CRITICAL: Use This Skill

**You MUST use memory during task execution.** Files are your only persistent storage.

```
At task start:    Read .memory/MEMORY.md
During execution: Append to .memory/tasks/<task_id>.md
At task end:      Update .memory/MEMORY.md with reusable learnings
```

Use `filesystem.write_text_file` or `filesystem.append_text_file` MCP tools to write memory.

## Purpose

Record observations, findings, and learnings during task execution to:
1. **Avoid repeating mistakes** - Remember what didn't work
2. **Track progress** - Know what you've already tried
3. **Preserve context** - Don't lose important findings across compaction
4. **Build knowledge** - Accumulate learnings for future tasks

## Memory Types

### Short-Term Memory (Task-Specific)

**Location**: `.memory/tasks/<task_id>.md`

Record task-specific observations as you work:
- Elements found on screen
- Actions attempted and their results
- Errors encountered
- Posts/content discovered
- Navigation paths tried

**When to write**:
- After each significant action
- When discovering important information
- When encountering errors or obstacles
- Before moving to next step

### Long-Term Memory (Cross-Task)

**Location**: `.memory/MEMORY.md`

Record durable knowledge that applies to future tasks:
- App UI patterns (where buttons are located)
- Common error solutions
- Successful strategies
- User preferences
- Platform-specific quirks

**When to write**:
- Discovering a reusable pattern
- Finding a workaround for a common issue
- Learning something about app behavior
- At task completion (lessons learned)

## Memory Format

### Short-Term (Task) Memory

```markdown
# Task: <task_id>
**Started**: <timestamp>
**Goal**: <task description>

## Progress Log

### <timestamp> - <action_type>
**Action**: <what you did>
**Result**: <what happened>
**Observation**: <what you learned>

### <timestamp> - Finding
**Source**: <where you found it>
**Content**: <key information>
**Relevance**: <why it matters>

## Summary
<brief summary of findings when task completes>
```

### Long-Term Memory

```markdown
# MobileAgent Memory

## App Knowledge

### Threads (com.instagram.barcelona)
- Search: Tap magnifying glass top-right, not bottom nav
- Feed: Swipe up to scroll, tap post to open
- Back: Android back button or swipe from left

### WeChat (com.tencent.mm)
- Official Accounts: Me > Settings > Official Accounts
- Article list: Tap account name > View history

## Strategies

### Research Tasks
1. Always scroll 3+ screens before concluding
2. Open at least 5 posts for thorough research
3. Check comments for additional context

## Error Solutions

### Unicode Input Fails
- Ensure DeviceKit is installed
- Use mobile_type_keys with submit=true

## User Preferences
- Language: zh-TW
- Output format: Structured with sources
```

## Usage Instructions

### At Task Start

1. Read long-term memory for relevant knowledge
2. Create task memory file with initial template

**MCP filesystem commands:**

```javascript
// Step 1: Read long-term memory
filesystem.read_text_file({ path: ".memory/MEMORY.md" })

// Step 2: Create task memory (use session ID as task ID)
filesystem.write_text_file({
  path: ".memory/tasks/<session_id>.md",
  content: "# Task: <description>\n\n## Observations\n\n"
})
```

### During Task Execution

After each significant action, append to task memory:

**MCP command:**

```javascript
filesystem.append_text_file({
  path: ".memory/tasks/<session_id>.md",
  content: "\n### Screen Analysis\n- Found search at (543, 150) top-right\n- 15 clickable elements\n"
})
```

**Example memory entry:**

```markdown
### Screen Analysis
- Found search at (543, 150) top-right, NOT bottom nav
- 15 clickable elements including: Home, Search, Profile
- Feed shows 3 posts, need to scroll for more
```

### When Finding Information

Record key findings immediately so you don't lose them:

```javascript
filesystem.append_text_file({
  path: ".memory/tasks/<session_id>.md",
  content: `
### Content Found
- Source: @clawdbot_user
- Content: "Claude MCP integration is amazing for automation"
- Engagement: 234 likes, 45 comments
- Sentiment: Positive
`
})
```

### At Task Completion

1. Append summary to task memory
2. Update long-term memory with NEW learnings only

**MCP commands:**

```javascript
// Append task summary
filesystem.append_text_file({
  path: ".memory/tasks/<session_id>.md",
  content: "\n## Summary\n- Found 8 posts, 6 positive\n- Themes: AI, MCP, productivity\n"
})

// Update MEMORY.md if you discovered something new and reusable
// Read first, then append new section
filesystem.read_text_file({ path: ".memory/MEMORY.md" })
filesystem.append_text_file({
  path: ".memory/MEMORY.md",
  content: "\n### New App: Reddit\n- Search via magnifying glass\n- Posts sorted by Hot/New/Top\n"
})
```

### Before Context Gets Too Long

If you've been working for a while, flush important state to memory:

```javascript
filesystem.append_text_file({
  path: ".memory/tasks/<session_id>.md",
  content: `
### Progress Checkpoint
- Posts reviewed: 3 of 5 target
- Sentiment so far: 2 positive, 1 neutral
- Still need: Check @user1, @user2 posts
- Next action: Scroll to find more posts
`
})
```

This ensures you can resume if context is compacted.

## Best Practices

1. **Write early, write often** - Don't wait until the end
2. **Be concise** - Memory is for reference, not prose
3. **Use structured format** - Easy to parse later
4. **Separate facts from opinions** - Quote sources
5. **Update long-term memory sparingly** - Only durable knowledge

## File Paths

```
.memory/
├── MEMORY.md           # Long-term memory (cross-task)
└── tasks/
    ├── abc12345.md     # Task-specific memory
    ├── def67890.md
    └── ...
```

## Integration with Other Skills

- **search-triage**: Record search results in task memory
- **content-extract**: Save extracted content summaries
- **comment-scan**: Log sentiment analysis findings
- **patrol**: Track visited posts to avoid duplicates
