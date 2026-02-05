---
name: content-extract
description: Extract complete article content (not summaries) with structured NLP analysis. Identifies who, what, when, where, and objects. Outputs JSON for API integration. Use when user wants full text extraction with analysis.
license: MIT
metadata:
  author: MobileAgent
  version: "2.0"
compatibility: Requires mobile-mcp MCP server and connected Android device. Outputs saved to outputs/ directory.
---

# Content Extract Skill - Full Content + NLP Analysis

## When to Use

User wants **complete content**, not summaries:

```
"Read WeChat account XXX's articles, extract title, full content, and analyze"
"Get the full article from this post, identify people/events/dates mentioned"
"Save the content with keyword extraction"
"Extract article and output as JSON"
```

**NOT** for quick browsing or sentiment overview (use patrol skill for that).

## JSON Output Schema

All output MUST follow this JSON schema for easy integration with other programs:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "extraction_meta": {
      "type": "object",
      "properties": {
        "version": { "type": "string", "const": "2.0" },
        "extracted_at": { "type": "string", "format": "date-time" },
        "platform": { "type": "string" },
        "source_account": { "type": "string" },
        "total_articles": { "type": "integer" },
        "extraction_status": { "type": "string", "enum": ["success", "partial", "failed"] }
      },
      "required": ["version", "extracted_at", "platform", "extraction_status"]
    },
    "articles": {
      "type": "array",
      "items": { "$ref": "#/$defs/article" }
    }
  },
  "$defs": {
    "article": {
      "type": "object",
      "properties": {
        "id": { "type": "string" },
        "source": { "type": "string" },
        "title": { "type": "string" },
        "author": { "type": "string" },
        "publish_date": { "type": "string", "format": "date" },
        "url": { "type": "string" },
        "content": { "$ref": "#/$defs/content" },
        "nlp_analysis": { "$ref": "#/$defs/nlp" },
        "keywords": { "type": "array", "items": { "type": "string" } },
        "sentiment": { "type": "string", "enum": ["positive", "negative", "neutral", "mixed"] },
        "summary": { "type": "string" }
      },
      "required": ["id", "title", "content"]
    },
    "content": {
      "type": "object",
      "properties": {
        "full_text": { "type": "string" },
        "paragraphs": { "type": "array", "items": { "type": "string" } },
        "word_count": { "type": "integer" },
        "char_count": { "type": "integer" },
        "language": { "type": "string" }
      },
      "required": ["full_text", "word_count"]
    },
    "nlp": {
      "type": "object",
      "properties": {
        "who": { "type": "array", "items": { "$ref": "#/$defs/entity" } },
        "what": { "type": "array", "items": { "$ref": "#/$defs/entity" } },
        "when": { "type": "array", "items": { "$ref": "#/$defs/entity" } },
        "where": { "type": "array", "items": { "$ref": "#/$defs/entity" } },
        "objects": { "type": "array", "items": { "$ref": "#/$defs/entity" } }
      }
    },
    "entity": {
      "type": "object",
      "properties": {
        "value": { "type": "string" },
        "context": { "type": "string" },
        "confidence": { "type": "number", "minimum": 0, "maximum": 1 }
      },
      "required": ["value"]
    }
  }
}
```

## Complete JSON Example

```json
{
  "extraction_meta": {
    "version": "2.0",
    "extracted_at": "2024-01-29T10:30:00+08:00",
    "platform": "WeChat",
    "source_account": "36氪",
    "total_articles": 1,
    "extraction_status": "success",
    "device_id": "SM-A5460",
    "skill_version": "content-extract-2.0"
  },
  "articles": [
    {
      "id": "wechat_36kr_20240128_001",
      "source": "WeChat Official Account: 36氪",
      "title": "2024年AI創業公司融資報告：大模型賽道持續火熱",
      "author": "36氪研究院",
      "publish_date": "2024-01-28",
      "url": "https://mp.weixin.qq.com/s/xxxxx",
      
      "content": {
        "full_text": "2024年開年，AI創業公司融資市場持續火熱。據統計，僅一月份全球AI領域融資額已突破50億美元，其中大語言模型賽道佔比超過60%。\n\n李開復旗下的創新工場近日宣布，其AI基金已完成新一輪募資，規模達10億美元。創新工場表示，該基金將重點投資大模型應用層創業公司。\n\n在北京和上海，多家AI初創公司宣布獲得新一輪融資。其中，智譜AI完成了由騰訊領投的B輪融資，估值突破100億人民幣。\n\n業內人士分析，2024年將是AI大模型落地應用的關鍵一年。預計到今年第四季度，主要大模型廠商都將推出面向企業的商用版本。\n\n值得注意的是，AI安全和監管討論也在同步升溫。多位專家呼籲，在發展AI技術的同時，需要建立完善的安全評估機制。",
        "paragraphs": [
          "2024年開年，AI創業公司融資市場持續火熱。據統計，僅一月份全球AI領域融資額已突破50億美元，其中大語言模型賽道佔比超過60%。",
          "李開復旗下的創新工場近日宣布，其AI基金已完成新一輪募資，規模達10億美元。創新工場表示，該基金將重點投資大模型應用層創業公司。",
          "在北京和上海，多家AI初創公司宣布獲得新一輪融資。其中，智譜AI完成了由騰訊領投的B輪融資，估值突破100億人民幣。",
          "業內人士分析，2024年將是AI大模型落地應用的關鍵一年。預計到今年第四季度，主要大模型廠商都將推出面向企業的商用版本。",
          "值得注意的是，AI安全和監管討論也在同步升溫。多位專家呼籲，在發展AI技術的同時，需要建立完善的安全評估機制。"
        ],
        "word_count": 342,
        "char_count": 456,
        "language": "zh-TW"
      },

      "nlp_analysis": {
        "who": [
          {
            "value": "李開復",
            "context": "創新工場董事長，AI基金募資相關",
            "confidence": 0.95
          },
          {
            "value": "智譜AI",
            "context": "獲得騰訊領投B輪融資的AI公司",
            "confidence": 0.90
          },
          {
            "value": "騰訊",
            "context": "智譜AI B輪融資領投方",
            "confidence": 0.90
          }
        ],
        "what": [
          {
            "value": "AI創業公司融資創新高",
            "context": "一月份全球AI融資突破50億美元",
            "confidence": 0.95
          },
          {
            "value": "創新工場AI基金募資完成",
            "context": "規模達10億美元",
            "confidence": 0.90
          },
          {
            "value": "智譜AI獲得B輪融資",
            "context": "騰訊領投，估值破100億",
            "confidence": 0.90
          }
        ],
        "when": [
          {
            "value": "2024年一月",
            "context": "融資統計時間",
            "confidence": 0.95
          },
          {
            "value": "2024年第四季度",
            "context": "預計大模型商用版本發布時間",
            "confidence": 0.85
          },
          {
            "value": "近日",
            "context": "創新工場宣布時間",
            "confidence": 0.70
          }
        ],
        "where": [
          {
            "value": "北京",
            "context": "AI初創公司融資地點",
            "confidence": 0.90
          },
          {
            "value": "上海",
            "context": "AI初創公司融資地點",
            "confidence": 0.90
          },
          {
            "value": "全球",
            "context": "AI融資統計範圍",
            "confidence": 0.85
          }
        ],
        "objects": [
          {
            "value": "大語言模型",
            "context": "融資熱門賽道，佔比超60%",
            "confidence": 0.95
          },
          {
            "value": "AI基金",
            "context": "創新工場募資工具，規模10億美元",
            "confidence": 0.90
          },
          {
            "value": "AI安全評估機制",
            "context": "專家呼籲建立",
            "confidence": 0.85
          }
        ]
      },

      "keywords": [
        "AI",
        "創業",
        "融資",
        "大語言模型",
        "投資",
        "創新工場",
        "智譜AI"
      ],

      "sentiment": "positive",

      "summary": "2024年AI創業融資市場開局火熱，一月全球融資額突破50億美元。創新工場完成10億美元AI基金募資，智譜AI獲騰訊領投B輪融資估值破百億。業界預計今年第四季度大模型將推出企業商用版本。"
    }
  ]
}
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

After extracting full content, analyze and populate the `nlp_analysis` object:

```
WHO - Identify people/organizations:
- Look for names (Chinese: 2-4 characters with surname patterns)
- Look for titles (CEO, 总裁, 教授, etc.)
- Look for organizations + person references
- Set confidence based on context clarity

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
```

### Phase 4: Save to File

```
Save location: outputs/YYYY-MM-DD/

Primary format: JSON (required for integration)
Secondary format: Markdown (optional, human-readable)

Filename: {platform}_{account}_{date}_{title_slug}.json
Example: wechat_36kr_20240128_ai-startup-funding.json
```

## API Integration Example

### Python Integration

```python
import json
from pathlib import Path

def load_extraction_result(filepath):
    """Load and validate extraction result."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate version
    assert data['extraction_meta']['version'] == '2.0'
    
    return data

def process_articles(data):
    """Process extracted articles."""
    for article in data['articles']:
        print(f"Title: {article['title']}")
        print(f"Word count: {article['content']['word_count']}")
        
        # Process NLP entities
        for person in article['nlp_analysis'].get('who', []):
            print(f"  Person: {person['value']} (confidence: {person.get('confidence', 'N/A')})")
        
        # Access keywords
        keywords = article.get('keywords', [])
        print(f"  Keywords: {', '.join(keywords)}")

# Usage
result = load_extraction_result('outputs/2024-01-29/wechat_36kr_extract.json')
process_articles(result)
```

### Node.js Integration

```javascript
const fs = require('fs');

function loadExtractionResult(filepath) {
  const data = JSON.parse(fs.readFileSync(filepath, 'utf8'));
  
  // Validate version
  if (data.extraction_meta.version !== '2.0') {
    throw new Error('Unsupported extraction format version');
  }
  
  return data;
}

function processArticles(data) {
  for (const article of data.articles) {
    console.log(`Title: ${article.title}`);
    console.log(`Sentiment: ${article.sentiment}`);
    
    // Process NLP entities
    const who = article.nlp_analysis.who || [];
    who.forEach(person => {
      console.log(`  Person: ${person.value}`);
    });
  }
}

// Usage
const result = loadExtractionResult('outputs/2024-01-29/wechat_36kr_extract.json');
processArticles(result);
```

### cURL / HTTP Request Example

```bash
# If using web API endpoint
curl -X POST http://localhost:6443/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "wechat",
    "account": "36氪",
    "max_articles": 3,
    "output_format": "json"
  }'

# Response follows the same JSON schema
```

## Minimal JSON Output (for errors or partial extraction)

```json
{
  "extraction_meta": {
    "version": "2.0",
    "extracted_at": "2024-01-29T10:30:00+08:00",
    "platform": "WeChat",
    "extraction_status": "failed",
    "error_message": "Could not navigate to account",
    "error_code": "NAV_FAILED"
  },
  "articles": []
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `SUCCESS` | Extraction completed successfully |
| `NAV_FAILED` | Could not navigate to source |
| `CONTENT_EMPTY` | Article opened but no content found |
| `SCROLL_STUCK` | Scrolling did not reveal new content |
| `LOGIN_REQUIRED` | Login wall blocked access |
| `TIMEOUT` | Operation timed out |
| `PARTIAL` | Some articles extracted, others failed |

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

```json
{
  "extraction_meta": {
    "version": "2.0",
    "extracted_at": "2024-01-29T10:30:00+08:00",
    "platform": "WeChat",
    "source_account": "36氪",
    "total_articles": 3,
    "extraction_status": "success"
  },
  "articles": [
    { "id": "001", "title": "Article 1...", "...": "..." },
    { "id": "002", "title": "Article 2...", "...": "..." },
    { "id": "003", "title": "Article 3...", "...": "..." }
  ]
}
```

## User Interaction

Ask for clarification when needed:

| Unclear | Ask |
|---------|-----|
| Which account? | "Which WeChat account should I look at?" |
| How many articles? | "How many articles should I extract? (default: latest 3)" |
| Save format? | "Save as JSON only, or include Markdown too?" |
| Full content or limit? | "Extract complete content or limit to first N paragraphs?" |

## Markdown Format (Secondary Output)

For human readability, also save as markdown:

```markdown
# Content Extraction: 36氪

**Extracted:** 2024-01-29 10:30
**Platform:** WeChat Official Account
**Status:** Success

---

## Article 1: 2024年AI創業公司融資報告

- **Author:** 36氪研究院
- **Date:** 2024-01-28
- **Word Count:** 342
- **Sentiment:** Positive

### Content

[Full article text...]

### NLP Analysis

#### Who (People/Organizations)
- **李開復** - 創新工場董事長 (confidence: 0.95)
- **智譜AI** - B輪融資AI公司 (confidence: 0.90)

#### What (Events)
- AI創業公司融資創新高

#### When (Time)
- 2024年一月

#### Where (Locations)
- 北京
- 上海

#### Objects (Things/Products)
- 大語言模型
- AI基金

### Keywords
AI, 創業, 融資, 大語言模型, 投資

---
```

## Key Reminders

1. **JSON First** - Always output JSON for integration
2. **Full content** - Don't truncate unless user asks
3. **Scroll completely** - Get all paragraphs
4. **Include confidence** - Add confidence scores to NLP entities
5. **Save files** - Always save to `outputs/YYYY-MM-DD/`
6. **Version tag** - Always include `version: "2.0"` in meta
7. **Status tracking** - Set appropriate `extraction_status`
