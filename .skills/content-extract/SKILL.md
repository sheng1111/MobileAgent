---
name: content-extract
description: Extract full content from articles/posts with structured NLP analysis (who, what, when, where, what). Save to file. Use when user wants complete content, not just summaries.
---

# Content Extract Skill - Full Content + NLP Analysis

## When to Use

User wants **complete content**, not summaries:

```
"Read WeChat account XXX's articles, extract title, full content, and analyze"
"Get the full article from this post, identify people/events/dates mentioned"
"Save the content with keyword extraction"
```

**NOT** for quick browsing or sentiment overview (use patrol skill for that).

## Output Structure

For each article/post, extract and structure:

```yaml
Article:
  source: "WeChat Official Account / @username"
  title: "Full article title"
  author: "Author name"
  publish_date: "2024-01-15"
  url_or_id: "article identifier if available"

  content:
    full_text: |
      Complete article content here...
      Paragraph by paragraph...
      No truncation unless user specifies limit.

    word_count: 1523

  nlp_analysis:
    who:  # People mentioned
      - "Elon Musk - CEO of Tesla"
      - "Sam Altman - CEO of OpenAI"

    what:  # Events/Actions
      - "Product launch announcement"
      - "Partnership agreement signed"

    when:  # Time references
      - "January 2024"
      - "Last quarter"
      - "Next month"

    where:  # Locations
      - "San Francisco"
      - "Shanghai office"

    objects:  # Things/Products/Concepts mentioned
      - "GPT-5"
      - "Electric vehicles"
      - "AI regulations"

  keywords:
    - "artificial intelligence"
    - "technology"
    - "innovation"

  sentiment: "positive/negative/neutral"

  summary: "One paragraph summary for quick reference"
```

## Execution Flow

### Phase 1: Navigate to Source

```
1. Launch app (WeChat, browser, etc.)
2. Navigate to the specific account/page
   - WeChat: 通讯录 → 公众号 → Find account
   - Browser: Open URL directly
3. Find the target article(s)
4. VERIFY: Correct account/page reached
```

### Phase 2: Extract Content

```
For each article:

1. Open article
   mobile_click_on_screen_at_coordinates(article_x, article_y)

2. Wait for full load (2-3s)

3. Extract via mobile_list_elements_on_screen:
   - Title: Usually large text at top
   - Author/Account: Below title
   - Date: Near author
   - Content: Main text body

4. Scroll and continue extracting:
   mobile_swipe_on_screen(direction="up")
   Continue until reaching end or comments section

5. Compile full text
   DO NOT truncate unless user specifies
```

### Phase 3: NLP Analysis

After extracting full content, analyze:

```
WHO - Identify people:
- Look for names (Chinese: 2-4 characters with surname patterns)
- Look for titles (CEO, 总裁, 教授, etc.)
- Look for organizations + person references

WHAT - Identify events/actions:
- Verbs + objects (announced, launched, signed)
- News-worthy actions
- Changes, updates, decisions

WHEN - Identify time:
- Explicit dates (2024年1月, January 15)
- Relative time (昨天, last week, 上个月)
- Time periods (Q1, 第一季度)

WHERE - Identify locations:
- City names
- Country names
- Specific addresses or venues
- "在XX" patterns in Chinese

OBJECTS - Identify things:
- Product names
- Company names
- Technologies
- Concepts being discussed

KEYWORDS - Extract key terms:
- Frequently mentioned terms
- Technical terms
- Topic indicators
```

### Phase 4: Save to File

```
Save location: outputs/YYYY-MM-DD/

File format options:
1. JSON (structured, machine-readable)
2. Markdown (human-readable)
3. Both

Filename: {source}_{date}_{title_slug}.{ext}
Example: wechat_20240115_ai-industry-report.json
```

## Example Execution

```
User: "看微信公眾號「36氪」的最新文章，提取完整內容，分析人事時地物"

Agent:
1. Launch WeChat
2. Navigate: 通讯录 → 公众号 → Search "36氪"
3. Open account page
4. Click latest article
5. Scroll and extract full content
6. Perform NLP analysis
7. Save to file

Output file: outputs/2024-01-29/wechat_36kr_ai-startup-funding.json

{
  "source": "WeChat Official Account: 36氪",
  "title": "2024年AI創業公司融資報告",
  "author": "36氪研究院",
  "publish_date": "2024-01-28",

  "content": {
    "full_text": "完整文章內容...(2000+ 字)...",
    "word_count": 2341
  },

  "nlp_analysis": {
    "who": [
      "李開復 - 創新工場董事長",
      "張一鳴 - 字節跳動創始人"
    ],
    "what": [
      "AI創業公司融資創新高",
      "大模型賽道競爭加劇"
    ],
    "when": [
      "2024年第一季度",
      "過去12個月"
    ],
    "where": [
      "北京",
      "上海",
      "矽谷"
    ],
    "objects": [
      "大語言模型",
      "GPT-4",
      "文心一言",
      "風險投資"
    ]
  },

  "keywords": ["AI", "創業", "融資", "大模型", "投資"],

  "sentiment": "positive",

  "summary": "報告顯示2024年AI創業公司融資額創歷史新高，大模型賽道成為最熱門領域..."
}

Also saved: outputs/2024-01-29/wechat_36kr_ai-startup-funding.md
```

## Platform-Specific Notes

### WeChat Official Accounts (微信公眾號)

```
Navigation path:
微信 → 通讯录 (Contacts) → 公众号 (Official Accounts) → Search/Find account

Article structure:
- Title: Top of article
- Author: Below title, often "作者：XXX" or account name
- Date: Near author, format "2024年1月15日" or "1月15日"
- Content: Main body
- End markers: "阅读原文", comments section
```

### Weibo

```
Navigation: Search user → Profile → Posts tab
Content: Post text + images
Engagement: 转发/评论/赞 counts
```

### News Apps (今日头条, etc.)

```
Navigation: Search or category → Article list
Content: Usually complete in-app
```

## Multiple Articles Mode

If user wants multiple articles:

```
ARTICLES_EXTRACTED: []
MAX_ARTICLES: (user specified or default 5)

For each article:
1. Extract full content
2. Perform NLP analysis
3. Add to ARTICLES_EXTRACTED
4. Back to list
5. Next article

Save all to single JSON array or separate files
```

## User Interaction

Ask for clarification when needed:

| Unclear | Ask |
|---------|-----|
| Which account? | "Which WeChat account should I look at?" |
| How many articles? | "How many articles should I extract? (default: latest 3)" |
| Save format? | "Save as JSON, Markdown, or both?" |
| Full content or limit? | "Extract complete content or limit to first N paragraphs?" |

## File Output Format

### JSON Format

```json
{
  "extraction_meta": {
    "extracted_at": "2024-01-29T10:30:00",
    "platform": "WeChat",
    "account": "36氪",
    "total_articles": 3
  },
  "articles": [
    { /* article 1 */ },
    { /* article 2 */ },
    { /* article 3 */ }
  ]
}
```

### Markdown Format

```markdown
# Content Extraction: 36氪

Extracted: 2024-01-29 10:30

---

## Article 1: [Title]

**Author:** XXX
**Date:** 2024-01-28

### Content

[Full article text...]

### NLP Analysis

**Who:**
- Person 1
- Person 2

**What:**
- Event 1

**When:**
- Time reference 1

**Where:**
- Location 1

**Keywords:** keyword1, keyword2, keyword3

---

## Article 2: [Title]
...
```

## Key Reminders

1. **Full content** - Don't truncate unless user asks
2. **Scroll completely** - Get all paragraphs
3. **Structure data** - Use consistent format
4. **Save files** - Always save to outputs/
5. **NLP is analysis** - Extract entities, not just copy text
