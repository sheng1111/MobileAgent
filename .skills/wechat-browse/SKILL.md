---
name: wechat-browse
description: Browse specific WeChat Official Accounts (公众号) by name, navigate to their article history, and extract articles. Use when user wants to read content from specific WeChat accounts.
license: MIT
metadata:
  author: MobileAgent
  version: "2.0"
compatibility: Requires mobile-mcp MCP server, connected Android device with WeChat (com.tencent.mm) installed and logged in
---

# WeChat Official Accounts Browser

## Purpose

Navigate to specific WeChat Official Accounts (公众号) by name, browse their article history, and coordinate with `full-article-extraction` to get complete content. This skill handles WeChat's unique navigation and discovery patterns.

## Scope

### What This Skill Does

- Search for Official Accounts by name
- Navigate to account profile/article list
- Browse article history (scroll through past articles)
- Identify latest and popular articles
- Coordinate extraction of selected articles
- Handle WeChat-specific UI patterns (tabs, menus, dialogs)
- Manage account list (multiple accounts in one session)

### What This Skill Does NOT Do

- Extract article content directly (uses `full-article-extraction`)
- Analyze comments (use `comment-reading-and-sentiment-scan`)
- Post comments or interact with articles
- Access accounts requiring special permissions
- Browse WeChat Moments or chat messages

## Inputs

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `accounts` | list | Official Account names to browse |

### Account List Format

```yaml
accounts:
  - name: "36氪"
    alias: "36kr"  # Optional, for reference
  - name: "机器之心"
  - name: "量子位"
```

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `articles_per_account` | int | 3 | How many articles to list per account |
| `extract_content` | boolean | true | Whether to extract full article content |
| `time_filter` | string | "all" | "latest" / "this_week" / "this_month" / "all" |
| `selection_mode` | string | "auto" | "auto" / "interactive" (ask user which to read) |

## Outputs

**IMPORTANT: Always output JSON format for deduplication and integration.**

### JSON Output Format

Save to: `outputs/YYYY-MM-DD/wechat_browse_{timestamp}.json`

```json
{
  "extraction_meta": {
    "version": "2.0",
    "extracted_at": "2024-01-15T10:30:00Z",
    "platform": "wechat",
    "extraction_type": "official_accounts",
    "total_accounts": 3,
    "total_articles": 9
  },
  "accounts": [
    {
      "account_name": "36氪",
      "account_id": "wow36kr",
      "verified": true,
      "status": "SUCCESS",
      "articles": [
        {
          "id": "wechat_36kr_20240115_001",
          "title": "2024年AI融资趋势分析",
          "author": "36氪",
          "publish_date": "2024-01-14",
          "preview": "本报告详细分析了2024年上半年...",
          "read_count": "2.3万",
          "url_hash": "a1b2c3d4",
          "extracted": true,
          "extraction_file": "outputs/2024-01-15/36kr_ai融资_001.json"
        }
      ]
    }
  ],
  "errors": [],
  "dedup_index": {
    "a1b2c3d4": "wechat_36kr_20240115_001",
    "e5f6g7h8": "wechat_36kr_20240115_002"
  }
}
```

### Deduplication Strategy

The `dedup_index` maps content hashes to article IDs:
- Hash is computed from: `account_id + title + publish_date`
- Before extracting, check if hash exists in previous runs
- Skip already-extracted articles unless `force_refresh=true`

### Loading Previous State

```python
# Check for existing extractions
prev_file = f"outputs/{date}/wechat_browse_*.json"
if exists(prev_file):
    prev_data = load_json(prev_file)
    known_hashes = prev_data.get("dedup_index", {})
    # Skip articles with matching hashes
```

## Primary Workflow

### Phase 1: Launch WeChat and Navigate

```
1. Launch WeChat
   → launch_and_wait(package="com.tencent.mm", wait_text="微信")

2. Navigate to Discover tab (发现)
   → find_and_click(text="发现")

3. Enter Search (搜一搜)
   → find_and_click(text="搜一搜")

4. Wait for search interface
   → smart_wait(text="搜索", timeout=3)
```

### Phase 2: Search for Official Account

```
For each account in accounts:
  1. Clear previous search (if any)
  2. Enter account name
     → type_and_submit(text=account.name)

  3. Wait for results
     → smart_wait(timeout=3)

  4. Switch to "公众号" tab (important!)
     → find_and_click(text="公众号")

  5. Find matching account in results
     - Look for exact name match
     - Check for verified badge (optional)

  6. If found: tap to enter account profile
     → find_and_click(text=account.name)

  7. If not found: record error, continue to next account
```

### Phase 3: Browse Account Profile

```
Once in account profile:
  1. Identify profile elements:
     - Account name (confirm correct account)
     - Verified status
     - Follower count (if visible)
     - "全部消息" or article history button

  2. Navigate to article list:
     - Tap "查看历史消息" or similar
     → find_and_click(text="历史消息") OR find_and_click(text="全部消息")

  3. Wait for article list to load
     → smart_wait(timeout=5)
```

### Phase 4: Scan Article List

```
Initialize:
  articles_found = []
  scroll_count = 0

Loop (until articles_per_account collected):
  1. Get visible articles
     → mobile_list_elements_on_screen()

  2. For each article:
     - Extract title
     - Extract date (if visible)
     - Extract preview text
     - Extract read count (if visible)
     - Add to articles_found

  3. If need more articles:
     → mobile_swipe_on_screen(direction="up")
     → scroll_count++

  4. Stop conditions:
     - articles_found >= articles_per_account
     - scroll_count > max_scrolls
     - Reached end of list
```

### Phase 5: Extract Articles (if requested)

```
If extract_content:
  For each article in selected_articles:
    1. Navigate back to article list (if not there)
    2. Tap on article
       → find_and_click(text=article.title)

    3. Wait for article to load
       → smart_wait(text="阅读原文" OR text="赞", timeout=5)

    4. Invoke full-article-extraction skill (or inline extraction)
       - Scroll through article
       - Collect all text
       - Save to file

    5. Navigate back to article list
       → navigate_back()

    6. Record extraction status
```

### Phase 6: Next Account

```
1. Navigate back to search
   → navigate_back() (multiple times if needed)
   - Until back at search interface

2. Repeat Phases 2-5 for next account

3. Continue until all accounts processed
```

### Phase 7: Compile Results

```
1. Gather all results
2. Calculate statistics
3. Generate summary in user's language
4. Save combined report if requested
```

## WeChat-Specific Patterns

### Navigation Structure

```
微信 (Main)
├── 微信 (Chats)
├── 通讯录 (Contacts)
├── 发现 (Discover)
│   ├── 朋友圈 (Moments)
│   ├── 视频号 (Channels)
│   ├── 搜一搜 (Search) ← Use this
│   └── ...
└── 我 (Me)

搜一搜 (Search)
├── 全部 (All)
├── 公众号 (Official Accounts) ← Switch to this tab
├── 小程序 (Mini Programs)
├── 朋友圈 (Moments)
└── 文章 (Articles)
```

### Element Patterns

| UI Element | Common Text/Identifier |
|------------|----------------------|
| Search button | "搜一搜", "搜索" |
| Official Accounts tab | "公众号" |
| Article history | "历史消息", "全部消息", "查看更多" |
| Read count | "阅读", "万阅读" |
| Publish date | "月日", "年月日", "昨天", "今天" |
| Verified badge | Blue checkmark icon |
| Back button | "返回", left arrow |

### Common Dialogs

| Dialog | Action |
|--------|--------|
| "允许访问通讯录" | Click "不允许" / "拒绝" |
| "开启通知" | Click "暂不开启" |
| "登录失效" | Report to user - need re-login |
| "网络错误" | Retry, if persists report |

## Heuristics

### Account Verification

```
Account is correct if:
  - Name exactly matches (or contains) search query
  - Has verified badge (for known big accounts)
  - Article titles match expected topic

Account might be wrong if:
  - Name is similar but not exact
  - No recent articles
  - Content doesn't match expected
```

### Article Selection Priority

```
When selecting which articles to extract:

Priority 1: Most recent (published within 7 days)
Priority 2: High read count (> 1万阅读)
Priority 3: Title contains relevant keywords
Priority 4: Featured/pinned articles
```

### Time Filter Application

```
"latest": Articles from last 7 days
"this_week": Articles from current week
"this_month": Articles from current month
"all": No time restriction (use articles_per_account limit)
```

## Failure Modes & Recovery

### 1. Account Not Found

**Symptom:** Search returns no results or wrong accounts.

**Recovery:**
- Try alternative spellings (36氪 vs 36kr)
- Try English name if Chinese fails
- Check if account name changed
- Report: "Account not found: [name]"

### 2. Access Restricted

**Symptom:** "该公众号已被封禁" or requires login.

**Recovery:**
- Report to user
- Skip to next account
- Note in results: "ACCESS_DENIED"

### 3. Article History Not Accessible

**Symptom:** Can't find "历史消息" or button doesn't work.

**Recovery:**
- Try scrolling profile page
- Look for alternative links ("全部消息", "查看更多")
- Try tapping on any visible article directly
- Report if completely blocked

### 4. WeChat Not Logged In

**Symptom:** Login screen appears instead of main interface.

**Recovery:**
- Cannot proceed without user login
- Report: "WeChat login required"
- Provide instructions for user to log in manually

### 5. Navigation Lost

**Symptom:** Back presses don't return to expected screen.

**Recovery:**
- Try pressing BACK multiple times
- Go HOME and restart from WeChat launch
- Track progress, resume from last successful point

### 6. Rate Limiting

**Symptom:** Search disabled or "请稍后重试".

**Recovery:**
- Wait 30-60 seconds
- Reduce request frequency
- If persists, stop and report partial results

## Tooling (MCP)

### Primary Tools

| Tool | Use Case |
|------|----------|
| `launch_and_wait` | Start WeChat |
| `find_and_click` | Navigate tabs, search, select accounts |
| `type_and_submit` | Enter search queries |
| `smart_wait` | Wait for content to load |
| `navigate_back` | Return to previous screens |
| `scroll_and_find` | Browse article lists |

### Secondary Tools

| Tool | Use Case |
|------|----------|
| `mobile_list_elements_on_screen` | Extract article metadata |
| `mobile_swipe_on_screen` | Scroll through articles |
| `dismiss_popup` | Handle WeChat dialogs |
| `mobile_save_screenshot` | Capture account/article info |

### File Operations

| Tool | Use Case |
|------|----------|
| `write_file` | Save extracted articles |
| `create_directory` | Create output folders |

## Examples

### Example 1: Multiple Accounts - Basic

**Input:**
```yaml
accounts:
  - name: "36氪"
  - name: "机器之心"
  - name: "量子位"
articles_per_account: 2
extract_content: true
```

**Execution Log:**
```
[1] Launched WeChat
[2] Navigated to 发现 → 搜一搜
[3] Searched "36氪", switched to 公众号 tab
[4] Found 36氪 (verified), entered profile
[5] Accessed 历史消息
[6] Found 2 articles:
    - "2024年AI融资趋势" (2天前, 2.3万阅读)
    - "创业公司如何选择AI工具" (5天前, 1.8万阅读)
[7] Extracted first article → saved to file
[8] Extracted second article → saved to file
[9] Navigated back to search
[10] Repeated for 机器之心...
[15] Repeated for 量子位...
[20] Compiled final report
```

**Output:**
```yaml
wechat_browse_result:
  session_info:
    accounts_requested: 3
    accounts_found: 3
    articles_extracted: 6

  accounts:
    - account_name: "36氪"
      verified: true
      status: "SUCCESS"
      articles:
        - title: "2024年AI融资趋势分析"
          publish_date: "2024-01-13"
          read_count: "2.3万"
          extracted: true
          extraction_file: "outputs/2024-01-15/36kr_ai融资趋势_001.json"
        - title: "创业公司如何选择AI工具"
          publish_date: "2024-01-10"
          extracted: true

    - account_name: "机器之心"
      verified: true
      status: "SUCCESS"
      articles: [...]

    - account_name: "量子位"
      verified: true
      status: "SUCCESS"
      articles: [...]

  summary: "成功浏览 3 个公众号，提取 6 篇文章。所有文件已保存至 outputs/2024-01-15/"
```

---

### Example 2: Account Not Found

**Input:**
```yaml
accounts:
  - name: "不存在的公众号测试"
  - name: "36氪"
articles_per_account: 1
```

**Output:**
```yaml
wechat_browse_result:
  accounts:
    - account_name: "不存在的公众号测试"
      status: "NOT_FOUND"
      articles: []

    - account_name: "36氪"
      status: "SUCCESS"
      articles:
        - title: "Latest article..."
          extracted: true

  errors:
    - account: "不存在的公众号测试"
      error_type: "NOT_FOUND"
      message: "公众号搜索无结果，请确认账号名称是否正确"

  summary: "请求 2 个公众号，找到 1 个。1 个账号未找到（详见错误列表）。"
```

---

### Example 3: Interactive Selection Mode

**Input:**
```yaml
accounts:
  - name: "36氪"
articles_per_account: 5
selection_mode: "interactive"
extract_content: true
```

**Mid-execution prompt to user:**
```
Found 5 recent articles from 36氪:

1. [2024-01-14] 2024年AI融资趋势分析 (2.3万阅读)
2. [2024-01-12] 创业公司如何选择AI工具 (1.8万阅读)
3. [2024-01-10] 硅谷大厂裁员潮分析 (3.1万阅读)
4. [2024-01-08] 新能源汽车市场报告 (1.5万阅读)
5. [2024-01-05] AI Agent 实战指南 (2.7万阅读)

Which articles should I extract? (Enter numbers, e.g., "1,3,5")
```

**User response:** "1,5"

**Continues extraction for articles 1 and 5 only.**

## Key Reminders

1. **Always switch to 公众号 tab** - Default search shows all content types
2. **Verify account identity** - Don't extract from wrong account
3. **Handle WeChat dialogs** - Pop-ups are common, dismiss properly
4. **Track navigation state** - WeChat navigation can be confusing
5. **Respect rate limits** - Don't search too rapidly
6. **Login required** - Can't proceed without logged-in WeChat
7. **Save progress** - Don't lose extracted content if later steps fail
8. **Report partial success** - If some accounts fail, still return successful ones
