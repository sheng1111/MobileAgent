---
name: article-extract
description: Extract complete article content including full text, metadata, and expanded sections. Scrolls to load all content, expands "read more" sections. Use when user needs full article text, not summaries.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
compatibility: Requires mobile-mcp MCP server, connected Android device with target app open to article
---

# Full Article Extraction

## Purpose

Extract the complete, untruncated content of an article or long-form post. Ensure all "read more" sections are expanded, all content is scrolled into view, and output a structured document with the full text and metadata.

## Scope

### What This Skill Does

- Navigate to target article/post
- Expand any "Read more" / "展开全文" sections
- Scroll through entire content to load lazy-loaded sections
- Extract complete text content paragraph by paragraph
- Capture article metadata (title, author, date, source)
- Identify and extract embedded media descriptions
- Save structured output to file
- Generate human-readable summary alongside full text

### What This Skill Does NOT Do

- Search for articles (use `iterative-search-and-triage`)
- Read or analyze comments (use `comment-reading-and-sentiment-scan`)
- Browse multiple articles (one article per invocation)
- Translate content (extract as-is)
- Post comments or interact

## Inputs

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | string | Platform name |
| `article_identifier` | object | How to find the article |

### Article Identifier Options

```yaml
# Option 1: From search
article_identifier:
  type: search_result
  keyword: "AI agents"
  position: 2

# Option 2: By title match
article_identifier:
  type: content_match
  title_contains: "2024年AI趋势"
  author: "36氪"

# Option 3: Direct navigation (if already at article)
article_identifier:
  type: current_screen
```

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_scrolls` | int | 20 | Maximum scrolls for long articles |
| `save_to_file` | boolean | true | Save output to outputs/ |
| `include_images` | boolean | false | Capture image descriptions |
| `output_format` | string | "both" | "json" / "markdown" / "both" |

## Outputs

### JSON Output Format

```json
{
  "extraction_meta": {
    "version": "1.0",
    "extracted_at": "2024-01-15T10:30:00Z",
    "platform": "wechat",
    "extraction_status": "SUCCESS",
    "confidence": 0.95
  },
  "article": {
    "title": "Article Title",
    "author": {
      "name": "Author Name",
      "account": "account_id",
      "verified": true
    },
    "publish_date": "2024-01-14",
    "source": "36氪",
    "url": "https://...",
    "content": {
      "full_text": "Complete article text here...",
      "paragraphs": [
        "First paragraph text",
        "Second paragraph text"
      ],
      "word_count": 1523,
      "char_count": 8291,
      "language": "zh-CN"
    },
    "media": {
      "image_count": 3,
      "image_descriptions": [
        "Chart showing growth trend",
        "Photo of CEO"
      ],
      "has_video": false
    },
    "summary": "AI-generated 2-3 sentence summary",
    "key_points": [
      "Key point 1",
      "Key point 2"
    ],
    "entities_mentioned": {
      "organizations": ["OpenAI", "Anthropic"],
      "people": ["Sam Altman"],
      "products": ["GPT-4", "Claude"]
    }
  },
  "extraction_log": {
    "scrolls_performed": 8,
    "expansions_clicked": 1,
    "sections_found": 12,
    "time_spent_seconds": 45
  }
}
```

### Markdown Output Format

```markdown
# Article Title

**Author:** Author Name (@account)
**Date:** 2024-01-14
**Source:** Platform Name
**Words:** 1,523

---

## Summary

AI-generated 2-3 sentence summary of the article.

## Key Points

- Key point 1
- Key point 2
- Key point 3

---

## Full Content

[Complete article text, preserving paragraph structure]

First paragraph...

Second paragraph...

[Image: Chart showing growth trend]

Third paragraph...

---

## Metadata

- Extracted: 2024-01-15 10:30
- Platform: WeChat
- Confidence: 95%
```

## Primary Workflow

### Phase 1: Navigate to Article

```
If article_identifier.type == "search_result":
  1. Search for keyword
  2. Navigate to Nth result
  3. Verify content matches expected

If article_identifier.type == "content_match":
  1. Search or navigate to article
  2. Verify title and author match

If article_identifier.type == "current_screen":
  1. Verify current screen is an article
  2. Note starting position
```

### Phase 2: Initial Assessment

```
1. Get screen summary
   → get_screen_summary()

2. Identify article structure:
   - Title location
   - Author/date location
   - "Read more" or "展开全文" buttons
   - Scroll area

3. Extract visible metadata:
   - Title
   - Author
   - Date (if visible)
   - Comment count (for reference)
```

### Phase 3: Expand Truncated Content

```
Look for expansion triggers:
  - "Read more" / "Continue reading"
  - "展开全文" / "查看全文" / "阅读原文"
  - "..." at end of visible text
  - "Show more" buttons

For each expansion found:
  1. Click expansion element
     → find_and_click(text="展开") OR find_and_click(text="Read more")

  2. Wait for content to expand
     → smart_wait(timeout=2)

  3. Verify expansion occurred (more text visible)
```

### Phase 4: Scroll and Collect

```
Initialize:
  collected_paragraphs = []
  previous_text_hash = None
  scroll_count = 0

Loop:
  1. Get current visible text
     → mobile_list_elements_on_screen()

  2. Extract text from article body elements
     - Skip navigation elements
     - Skip ads/promotions
     - Preserve paragraph structure

  3. Add new paragraphs to collected_paragraphs
     - De-duplicate (some paragraphs may overlap between scrolls)

  4. Check for more content:
     - Is there scroll room below?
     - Is current text hash same as previous? (end of content)

  5. If more content:
     → mobile_swipe_on_screen(direction="up", distance=400)
     → scroll_count++
     → Wait for new content to load

  6. Stop conditions:
     - Reached comment section (different content type)
     - Same text hash twice (no new content)
     - scroll_count >= max_scrolls
     - Found "end of article" indicator
```

### Phase 5: Content Assembly

```
1. Merge collected paragraphs
   - Remove duplicates from scroll overlap
   - Preserve order

2. Clean text:
   - Remove navigation remnants
   - Remove ad markers
   - Fix encoding issues if any

3. Identify media:
   - Note image placeholders
   - Describe visible images if include_images=true

4. Calculate statistics:
   - Word count
   - Character count
   - Paragraph count
   - Detected language
```

### Phase 6: Generate Metadata

```
1. Compile metadata:
   - Title (from extraction)
   - Author (from extraction)
   - Date (from visible info or infer from context)
   - Platform

2. Generate summary:
   - 2-3 sentence overview
   - Based on full extracted text

3. Extract key points:
   - Main arguments or findings
   - 3-5 bullet points

4. Entity extraction:
   - Organizations mentioned
   - People mentioned
   - Products/technologies mentioned
```

### Phase 7: Save and Return

```
If save_to_file:
  1. Create directory: outputs/YYYY-MM-DD/
  2. Generate filename: {platform}_{sanitized_title}_{timestamp}
  3. Write JSON file
  4. Write Markdown file (if output_format includes markdown)

Return extraction result to user
```

## Heuristics

### End of Article Detection

| Signal | Confidence |
|--------|------------|
| "Comment" / "评论" section starts | High |
| "Related articles" / "推荐阅读" | High |
| Share/Like bar (article-end style) | Medium |
| Author bio section | Medium |
| 3 consecutive scrolls, no new text | High |
| Reached page bottom (scroll bounces) | High |

### Content vs. Non-Content Classification

**Include:**
- Main body paragraphs
- Block quotes
- Lists within article
- Image captions

**Exclude:**
- Navigation menus
- "Follow us" prompts
- Ad banners
- "Related articles" links
- Comment section

### Paragraph Deduplication

```python
def is_duplicate(new_para, existing_paras):
    # Exact match
    if new_para in existing_paras:
        return True

    # 80% overlap (for partial scroll overlaps)
    for existing in existing_paras:
        overlap = len(set(new_para.split()) & set(existing.split()))
        if overlap / len(new_para.split()) > 0.8:
            return True

    return False
```

### Language Detection

```
If >50% characters are Chinese: zh-CN
If >50% characters are Japanese kana: ja-JP
If contains Hangul: ko-KR
Default: en-US
```

## Failure Modes & Recovery

### 1. Article Behind Paywall

**Symptom:** "Subscribe to continue" or partial content visible.

**Recovery:**
- Extract what's available
- Mark extraction_status: "PARTIAL"
- Note in output: "Article is paywalled, only preview extracted"
- Report word count of available portion

### 2. Expansion Button Not Found

**Symptom:** Text appears truncated but no "Read more" button.

**Recovery:**
- Try scrolling (content might auto-expand)
- Try tapping on truncated text
- Check for "..." that might be clickable
- Proceed with available content, note limitation

### 3. Infinite Scroll Content

**Symptom:** Content keeps loading indefinitely (rare for articles).

**Recovery:**
- Enforce max_scrolls
- Look for article end markers aggressively
- Stop if same content repeats 3 times

### 4. Content in Images/Screenshots

**Symptom:** Key content is embedded in images, not text.

**Recovery:**
- Note image presence
- Describe images if include_images=true
- Mark extraction: "Contains image-based content not extracted"
- Consider OCR tools if available

### 5. Dynamic Content Loading Fails

**Symptom:** Sections show loading spinner indefinitely.

**Recovery:**
- Wait up to 10 seconds
- Try scrolling past and back
- Extract what loaded, mark sections as "LOADING_FAILED"

### 6. Wrong Article Extracted

**Symptom:** Extracted content doesn't match expected title.

**Recovery:**
- Verify navigation was correct
- If mismatch, report error
- Don't save wrong content to file

## Tooling (MCP)

### Primary Tools

| Tool | Use Case |
|------|----------|
| `find_and_click` | Navigate to article, click expansions |
| `smart_wait` | Wait for content to load |
| `get_screen_summary` | Get current visible text |
| `scroll_and_find` | Find end-of-article markers |

### Secondary Tools

| Tool | Use Case |
|------|----------|
| `mobile_list_elements_on_screen` | Get detailed text elements |
| `mobile_swipe_on_screen` | Scroll through article |
| `mobile_save_screenshot` | Capture images if needed |

### File Operations

| Tool | Use Case |
|------|----------|
| `write_file` | Save JSON and Markdown output |
| `create_directory` | Ensure output directory exists |

### Workflow Pattern

```
1. Navigate to article
2. find_and_click(text="展开全文") [if exists]
3. Loop:
   a. mobile_list_elements_on_screen() → extract text
   b. mobile_swipe_on_screen(direction="up")
   c. Check for article end
4. Assemble and clean content
5. write_file(outputs/YYYY-MM-DD/article.json)
6. write_file(outputs/YYYY-MM-DD/article.md)
```

## Examples

### Example 1: WeChat Official Account Article

**Input:**
```yaml
platform: wechat
article_identifier:
  type: content_match
  title_contains: "AI大模型发展趋势"
  author: "机器之心"
save_to_file: true
output_format: both
```

**Execution:**
```
1. Opened WeChat article "2024年AI大模型发展趋势"
2. Found "展开全文" button - clicked
3. Content expanded (was 500 chars, now 3200 chars visible)
4. Scrolled 6 times to read full article
5. Reached comment section - stopped
6. Total paragraphs: 18
7. Total words: 2,847
```

**Output (JSON excerpt):**
```json
{
  "extraction_meta": {
    "platform": "wechat",
    "extraction_status": "SUCCESS",
    "confidence": 0.98
  },
  "article": {
    "title": "2024年AI大模型发展趋势报告",
    "author": {
      "name": "机器之心",
      "verified": true
    },
    "content": {
      "word_count": 2847,
      "paragraphs": [
        "2024年上半年，AI大模型领域经历了前所未有的快速发展...",
        "据统计，全球AI大模型融资总额达到...",
        ...
      ]
    },
    "summary": "本报告分析了2024年上半年AI大模型领域的主要发展趋势，包括融资规模增长42%、多模态能力突破、以及应用落地加速等关键动向。"
  }
}
```

**Files Saved:**
- `outputs/2024-01-15/wechat_ai大模型发展趋势_103045.json`
- `outputs/2024-01-15/wechat_ai大模型发展趋势_103045.md`

---

### Example 2: Threads Long Post

**Input:**
```yaml
platform: threads
article_identifier:
  type: search_result
  keyword: "AI agents"
  position: 1
max_scrolls: 5
```

**Output (shorter content):**
```json
{
  "extraction_meta": {
    "extraction_status": "SUCCESS"
  },
  "article": {
    "title": "My experience building AI agents for a year",
    "author": {
      "name": "@aibuilder"
    },
    "content": {
      "word_count": 412,
      "paragraphs": [
        "After a year of building AI agents, here's what I learned:",
        "1. Start simple. Don't try to automate everything...",
        "2. Verification is key...",
        ...
      ]
    }
  }
}
```

---

### Example 3: Paywalled Article

**Input:**
```yaml
platform: news_app
article_identifier:
  type: content_match
  title_contains: "Exclusive: Tech Industry Report"
```

**Output:**
```json
{
  "extraction_meta": {
    "extraction_status": "PARTIAL",
    "confidence": 0.4
  },
  "article": {
    "title": "Exclusive: 2024 Tech Industry Report",
    "content": {
      "word_count": 287,
      "full_text": "[Preview content only]\\n\\nThe tech industry is poised for major changes in 2024...\\n\\n[Subscribe to read more]"
    },
    "notes": "Article is behind paywall. Only preview content extracted."
  }
}
```

## Key Reminders

1. **FULL content** - Don't stop at preview; expand everything
2. **One article per call** - Multi-article extraction needs multiple invocations
3. **Verify completeness** - Check word count seems reasonable for article type
4. **Preserve structure** - Keep paragraph breaks, don't merge everything
5. **Clean output** - Remove navigation and ad remnants
6. **Save incrementally** - Don't lose content if error occurs at end
7. **Detect end accurately** - Comment section is NOT part of article
8. **Report limitations** - If partial, say why (paywall, loading failure, etc.)
