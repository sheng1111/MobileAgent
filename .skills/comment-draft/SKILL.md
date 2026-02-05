---
name: comment-draft
description: Generate 1-3 comment drafts based on article context, tone, and identity constraints. Does NOT post comments or execute app operations. Use when user wants to compose a comment before posting.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
---

# Comment Composition and Tone Control

## Purpose

Generate appropriate comment drafts based on article content, comment section context, user-specified tone, and identity. Output options for user approval before posting.

## Scope

### What This Skill Does

- Analyze article/post content for comment relevance
- Consider existing comment sentiment and discussions
- Generate 1-3 comment drafts matching specified tone
- Respect word limits and platform conventions
- Flag potential risks (controversial topics, sensitive phrasing)
- Provide rationale for each draft option
- Support multiple languages based on content language

### What This Skill Does NOT Do

- Execute any app operations (no tapping, scrolling)
- Post comments (use `comment-posting-workflow`)
- Read articles or comments (expects input from other skills)
- Make final decisions (user selects which draft to use)

## Inputs

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `context` | object | Content and comment context (see below) |
| `tone` | string | Desired comment tone |
| `identity` | string | How the commenter should present themselves |

### Context Object

```yaml
context:
  article:
    title: string
    summary: string  # 2-3 sentences
    key_points: list  # Main points to potentially reference
    language: string  # Content language

  comment_section:
    sentiment_summary: string  # From comment-reading skill
    top_comments: list  # Notable existing comments
    common_questions: list  # Unanswered questions
    controversies: list  # Debate points

  user_goal: string  # What user wants to achieve
  # Examples:
  # - "Share my perspective on AI safety"
  # - "Ask a clarifying question"
  # - "Support the author's point"
  # - "Offer a counterpoint respectfully"
```

### Tone Options

| Tone | Description | Characteristics |
|------|-------------|-----------------|
| `professional` | Expert/business context | Formal language, data-driven, credentials implied |
| `casual` | Friendly conversation | Relaxed language, personal anecdotes, emoji allowed |
| `neutral` | Balanced observer | No strong opinion, factual, questioning |
| `supportive` | Agreement/encouragement | Positive framing, appreciation, building on ideas |
| `constructive_critical` | Respectful disagreement | "I see your point, but...", alternatives offered |
| `curious` | Question-focused | Asks questions, seeks clarification |
| `humorous` | Light-hearted | Appropriate wit, not offensive |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_length` | int | 280 | Character limit for comment |
| `drafts_count` | int | 3 | Number of options to generate |
| `forbidden_topics` | list | [] | Topics to avoid mentioning |
| `must_include` | list | [] | Points that must be addressed |
| `language` | string | auto | Output language (auto = match content) |

## Outputs

### Comment Draft Output

```yaml
comment_drafts:
  generated_at: timestamp
  input_summary:
    article_topic: string
    requested_tone: string
    identity: string

  drafts:
    - draft_id: 1
      content: string
      tone_match: float  # 0-1, how well it matches requested tone
      length: int  # Character count
      language: string

      strategy: string  # How this comment approaches the topic
      # Examples:
      # - "Adds personal experience to support main point"
      # - "Asks clarifying question about methodology"
      # - "Offers alternative perspective with evidence"

      references:  # What from context it builds on
        - type: string  # "article_point" / "existing_comment" / "user_goal"
          source: string

      risks:
        level: "none" | "low" | "medium" | "high"
        concerns: list  # Specific concerns if any
        # Examples:
        # - "Might be seen as dismissive of original post"
        # - "References controversial figure"
        # - "Could start heated debate"

    - draft_id: 2
      content: string
      # ... same structure

    - draft_id: 3
      content: string
      # ... same structure

  recommendation:
    suggested_draft: int  # Which draft is recommended
    reason: string
```

## Primary Workflow

### Step 1: Analyze Context

```
1. Understand article topic and stance
2. Note key points that could be referenced
3. Review comment section sentiment
4. Identify opportunities:
   - Unanswered questions to address
   - Points needing support
   - Gaps in discussion
   - Misconceptions to clarify
```

### Step 2: Map Tone to Style

```
Based on requested tone, determine:

Professional:
  - Vocabulary: technical terms, precise language
  - Structure: clear thesis, supporting evidence
  - Avoid: slang, emoji, excessive enthusiasm

Casual:
  - Vocabulary: everyday words, contractions
  - Structure: conversational flow
  - Allow: light emoji, personal pronouns, anecdotes

Supportive:
  - Opening: appreciation ("Great point about...")
  - Body: build on existing ideas
  - Closing: encouragement

Constructive_critical:
  - Opening: acknowledge merit ("I see the logic here")
  - Body: respectful disagreement with reason
  - Closing: open to discussion

Curious:
  - Frame as questions, not statements
  - "I'm wondering...", "Could you elaborate..."
  - Show genuine interest
```

### Step 3: Incorporate Identity

```
Identity affects:
  - How commenter introduces themselves (if at all)
  - What knowledge/experience they can reference
  - Credibility signals

Examples:
  Identity: "AI researcher"
  → Can reference research experience
  → Should use accurate terminology
  → Should not overclaim expertise

  Identity: "curious reader"
  → Ask questions, not make assertions
  → Can express learning journey
  → Should not pretend expertise

  Identity: "industry practitioner"
  → Can share real-world examples
  → Practical perspective
  → Avoid academic jargon
```

### Step 4: Generate Draft Variations

```
For drafts_count drafts:

Draft 1: Direct response to main article point
  - Most straightforward approach
  - Clear connection to content

Draft 2: Engage with existing comments
  - Build on or respond to notable comments
  - Join the conversation

Draft 3: Unique angle
  - Add new perspective
  - Ask unexpected question
  - Share relevant experience
```

### Step 5: Apply Constraints

```
For each draft:
  1. Check length against max_length
     - If over, condense without losing meaning

  2. Check forbidden_topics
     - Remove any forbidden references
     - Flag if removal changes meaning significantly

  3. Check must_include
     - Ensure all required points are addressed

  4. Language check
     - Ensure output language matches specification
     - For Chinese content, use appropriate formality
```

### Step 6: Risk Assessment

```
Evaluate each draft for:

HIGH RISK:
  - Directly contradicts/attacks author
  - References sensitive political topics
  - Makes unverifiable claims
  - Could be seen as spam/promotional

MEDIUM RISK:
  - Strong opinion on controversial topic
  - Disagrees with popular comments
  - References ongoing debates

LOW RISK:
  - Expresses opinion with hedging
  - Asks questions
  - Shares personal experience only

NO RISK:
  - Supportive comments
  - Neutral observations
  - Simple questions
```

### Step 7: Recommend Best Draft

```
Selection criteria:
  1. Best tone match
  2. Lowest risk (unless user wants to be provocative)
  3. Most relevant to user's goal
  4. Most likely to get engagement
```

## Heuristics

### Length Guidelines by Platform

| Platform | Typical Comment Length | Max Recommended |
|----------|----------------------|-----------------|
| Threads | 50-150 chars | 280 chars |
| Instagram | 50-200 chars | 300 chars |
| WeChat | 50-200 chars | 500 chars |
| Weibo | 100-200 chars | 500 chars |
| X/Twitter | 50-200 chars | 280 chars |
| YouTube | 100-500 chars | 1000 chars |

### Opening Patterns by Tone

| Tone | Good Openings | Avoid |
|------|---------------|-------|
| Professional | "This analysis highlights...", "Building on this point..." | "OMG", "Yo" |
| Casual | "Love this!", "This is so true!", "Same here..." | Over-formal language |
| Supportive | "Great insight!", "Couldn't agree more", "This needed to be said" | Backhanded compliments |
| Critical | "Interesting perspective, though...", "I see the merit, but consider..." | "You're wrong", "This is stupid" |
| Curious | "I'm curious about...", "Could you elaborate on...", "What about..." | Rhetorical attacks |

### Culture-Aware Phrasing

**Chinese platforms (WeChat, Weibo):**
- More indirect criticism preferred
- "个人观点" (personal opinion) as hedging
- Emoji and stickers more common
- Reference to "学习了" (learned something) for appreciation

**English platforms:**
- Direct but polite
- "I think" / "In my experience" for hedging
- Emoji usage varies by platform

## Failure Modes & Recovery

### 1. Insufficient Context

**Symptom:** Not enough information to write relevant comment.

**Recovery:**
- Request more context from user
- Generate very general comment with disclaimer
- Suggest what additional info would help

### 2. Conflicting Requirements

**Symptom:** Tone and identity don't match (e.g., "casual" + "formal expert").

**Recovery:**
- Prioritize tone (explicit request)
- Adjust identity expression
- Note conflict in output

### 3. Impossible Constraints

**Symptom:** Max length too short for meaningful comment.

**Recovery:**
- Note limitation
- Provide shortest possible version
- Suggest longer version if constraints relaxed

### 4. Highly Controversial Topic

**Symptom:** No way to comment without taking controversial stance.

**Recovery:**
- Flag as high risk
- Offer "question only" alternative
- Suggest user reconsider engaging

### 5. Language Mismatch

**Symptom:** User wants to comment in different language than content.

**Recovery:**
- Can generate, but flag potential reception issues
- Suggest matching content language

### 6. All Drafts Too Similar

**Symptom:** Different approaches converge on same comment.

**Recovery:**
- Be more creative with angles
- Explicitly try contrasting strategies
- Note if topic limits variation

## Tooling (MCP)

This skill does NOT use MCP tools.

It is a pure text generation skill that:
- Receives context from other skills
- Outputs draft text for user approval
- Feeds selected draft to `comment-posting-workflow`

## Examples

### Example 1: Professional Supportive Comment

**Input:**
```yaml
context:
  article:
    title: "Why AI Agents Will Transform Software Development"
    summary: "Author argues AI agents can autonomously handle routine coding tasks, freeing developers for creative work."
    key_points:
      - "Agents can write boilerplate code"
      - "Human oversight still essential"
      - "5-10 years to mainstream adoption"

  comment_section:
    sentiment_summary: "Generally positive, some skepticism about timeline"
    top_comments:
      - "Finally someone gets it - agents are tools, not replacements"

  user_goal: "Support the author's balanced view"

tone: professional
identity: "Software engineer with AI experience"
max_length: 200
```

**Output:**
```yaml
comment_drafts:
  drafts:
    - draft_id: 1
      content: "Excellent analysis. As someone who's integrated AI agents into our development workflow, I can confirm the productivity gains are real—but so is the need for human review. The 5-10 year timeline feels right given current capabilities."
      tone_match: 0.95
      length: 198
      strategy: "Validate from personal experience"
      risks:
        level: "none"

    - draft_id: 2
      content: "This captures the nuance often missing from AI discussions. The agent-as-tool framing is crucial. In my team's experience, the biggest wins come from reducing context-switching, not replacing engineers entirely."
      tone_match: 0.90
      length: 196
      strategy: "Add complementary insight"
      risks:
        level: "none"

    - draft_id: 3
      content: "Building on the oversight point—we've found that agents actually improve code review quality because reviewers can focus on architecture and logic instead of style and boilerplate. Win-win."
      tone_match: 0.85
      length: 188
      strategy: "Extend specific argument"
      risks:
        level: "low"
        concerns: ["Might seem like humble-bragging about team practices"]

  recommendation:
    suggested_draft: 1
    reason: "Most direct support for author, balanced, mentions real experience"
```

---

### Example 2: Constructive Criticism (Chinese)

**Input:**
```yaml
context:
  article:
    title: "大模型将在两年内取代程序员"
    summary: "作者认为大模型发展迅速，两年内将完全取代初级程序员工作"
    language: "zh-CN"

  user_goal: "Respectfully disagree with timeline"

tone: constructive_critical
identity: "行业从业者"
language: "zh-CN"
max_length: 200
```

**Output:**
```yaml
comment_drafts:
  drafts:
    - draft_id: 1
      content: "作者对技术发展的观察很敏锐，不过个人认为两年的时间线可能过于乐观。从实际落地来看，AI目前更像是提效工具而非替代方案。当然技术发展常有惊喜，拭目以待。"
      tone_match: 0.92
      length: 89
      strategy: "承认观点后委婉质疑"
      risks:
        level: "low"

    - draft_id: 2
      content: "思路很有启发性。想请教：这个两年预测是基于哪些技术节点的判断？从我接触的项目看，复杂业务逻辑的处理仍是难点，很好奇作者怎么看这块。"
      tone_match: 0.88
      length: 94
      strategy: "以提问方式引导反思"
      risks:
        level: "none"

    - draft_id: 3
      content: "有启发。不过历史上类似预测（如'5年内实现无人驾驶'）往往低估了工程落地的复杂度。AI辅助编程是趋势，'取代'可能需要更长时间观察。个人看法，仅供参考。"
      tone_match: 0.85
      length: 98
      strategy: "引用历史类比"
      risks:
        level: "medium"
        concerns: ["可能被认为在否定作者观点"]

  recommendation:
    suggested_draft: 2
    reason: "以提问形式最委婉，避免直接对抗"
```

---

### Example 3: Casual Curious Comment

**Input:**
```yaml
context:
  article:
    title: "My Experience Using AI Agents for a Month"
    summary: "Personal blog post about trying various AI agents for daily tasks"

  comment_section:
    common_questions:
      - "Which agent did you find best for coding?"

  user_goal: "Ask about the author's coding workflow"

tone: casual
identity: "curious reader"
max_length: 150
```

**Output:**
```yaml
comment_drafts:
  drafts:
    - draft_id: 1
      content: "Super interesting write-up! I'm curious - for the coding tasks you mentioned, did you find any agent particularly good at debugging vs. writing new code? Trying to figure out which to try first 🤔"
      tone_match: 0.95
      length: 148
      strategy: "Specific follow-up question"
      risks:
        level: "none"

    - draft_id: 2
      content: "This is exactly what I needed to read! Quick q - were you using these agents with any specific IDE or just web interfaces? Trying to set up something similar 👀"
      tone_match: 0.90
      length: 142
      strategy: "Practical setup question"
      risks:
        level: "none"

    - draft_id: 3
      content: "Love the honest take! Do you think a complete beginner could follow a similar workflow, or is some coding background needed to make good use of these tools?"
      tone_match: 0.88
      length: 145
      strategy: "Accessibility question"
      risks:
        level: "none"

  recommendation:
    suggested_draft: 1
    reason: "Most directly addresses unanswered question in comments"
```

## Key Reminders

1. **Pure text generation** - No app operations, just compose text
2. **Multiple options** - Always provide choices, let user decide
3. **Match content language** - Unless user explicitly wants different
4. **Risk transparency** - Always flag potential issues
5. **Respect constraints** - Length limits are hard limits
6. **Tone consistency** - Every word should match requested tone
7. **Identity authenticity** - Don't claim expertise the identity doesn't have
8. **User goal alignment** - Drafts should serve user's stated purpose
