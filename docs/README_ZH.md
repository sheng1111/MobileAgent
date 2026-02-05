# MobileAgent - AI 驅動的手機自動化框架

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sheng1111/MobileAgent)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)

[English README](../README.md)

一個開源的自動化框架，透過 **AI Agent** 與 **MCP** (Model Context Protocol) 控制 **Android 裝置**。使用自然語言指令建構智慧型手機自動化工作流程。

## 🌟 核心功能

### 基礎能力
- **🤖 AI Agent 相容** - 支援 Cursor、Claude Code、Gemini CLI、Codex、Windsurf、Roo Code
- **🔌 MCP 整合** - 支援 mobile-mcp、filesystem、fetch、context7 等 MCP 伺服器
- **📱 多裝置支援** - 同時控制多台 Android 裝置
- **🌐 Web UI** - 網頁介面管理裝置與任務，支援繁中/英文
- **🎯 Skills 系統** - 統一的 Skills 來源，自動部署到偵測到的 AI Agents
- **🔤 Unicode 輸入** - 透過 ADBKeyboard 支援中文、日文、表情符號

### 進階自動化 (v2.0 新增)
- **⚡ MCP Macro 伺服器** - 高階工具，更快更可靠的自動化
- **🎯 uiautomator2 整合** - 基於選擇器的操作，無需猜測座標
- **🔄 平台適配器** - 統一介面支援 Threads、Instagram、X、TikTok、YouTube、Facebook
- **🔍 Element-First 策略** - 優先使用元素樹，而非截圖，提升速度與準確度
- **✅ Click-Verify 協議** - 每次動作都驗證是否成功
- **🐛 除錯工件** - 動作失敗時自動儲存截圖與元素樹

## 📋 系統需求

- Python 3.8+
- Node.js 18+
- Android SDK Platform Tools (ADB)
- Android 裝置（已啟用 USB 偵錯）

### 選用（推薦）
- [uiautomator2](https://github.com/openatx/uiautomator2) - 基於選擇器的自動化

## 🚀 快速開始

### 1. 執行設定腳本

```bash
chmod +x set.sh && ./set.sh
```

這會自動：
- 檢查相依套件（Python 3.8+、Node.js 18+、ADB）
- 建立 Python 虛擬環境並安裝相依套件
- 安裝 uiautomator2（若有裝置連接，也會初始化 ATX agent）
- 設定各 AI CLI 工具的 MCP 設定（Gemini、Claude、Codex）
- 驗證並部署 Skills 到偵測到的 AI Agents
- 建立必要目錄（`outputs/`、`temp/logs/`）

### 2. 連接裝置並開始使用

```bash
adb devices                    # 確認裝置連接
source .venv/bin/activate      # 啟動虛擬環境
```

完成！現在可以開始使用 MobileAgent 搭配你的 AI Agent。

## 📁 專案結構

```
MobileAgent/
├── AGENTS.md              # AI Agent 行為準則（必讀）
├── GEMINI.md              # Gemini CLI 快速參考
├── CLAUDE.md              # Claude Code 快速參考
├── set.sh                 # 設定腳本（含 Skills 部署）
│
├── src/                   # Python 模組
│   ├── adb_helper.py      # ADB 指令封裝
│   ├── executor.py        # 確定性執行器（Element-First 強制）
│   ├── tool_router.py     # 統一 MCP/ADB/u2 介面
│   ├── u2_driver.py       # uiautomator2 選擇器操作
│   ├── mcp_macro_server.py # 高階 MCP 巨集工具
│   ├── platform_adapter.py # 多平台統一介面
│   ├── state_tracker.py   # 導航狀態機
│   ├── patrol.py          # 社群媒體海巡自動化
│   └── logger.py          # 日誌模組
│
├── .skills/               # Skills 來源目錄
│   ├── app-explore/       # 主要技能：App 操作 + 研究思維
│   ├── app-action/        # 快速單步操作
│   ├── patrol/            # 海巡技能（搜尋關鍵字、監控輿情）
│   ├── content-extract/   # 完整內容擷取 + NLP 分析
│   ├── device-check/      # 裝置連線檢查
│   ├── screen-analyze/    # 畫面狀態分析
│   ├── troubleshoot/      # 問題診斷
│   └── unicode-setup/     # Unicode 輸入設定
│
├── web/                   # Web UI
│   ├── app.py             # Flask 後端
│   ├── static/            # CSS/JS
│   └── templates/         # HTML 模板
│
├── mcp/                   # MCP 設定
├── apk_tools/             # APK 工具（DeviceKit、ADBKeyboard）
├── tests/                 # 單元測試
├── outputs/               # 截圖、下載、海巡報告
└── temp/logs/             # 日誌檔案
```

## 🛠️ MCP Macro 伺服器

新的 **mobile-macro** MCP 伺服器提供高階自動化工具，將多個步驟整合成單一操作，減少 LLM 來回次數，提升可靠性。

### 可用工具

| 工具 | 說明 |
|------|------|
| `find_and_click` | 元素搜尋 + 點擊 + 驗證，一次完成 |
| `type_and_submit` | 聚焦 + 輸入 + 送出，一次完成 |
| `smart_wait` | 使用原生 u2 等待元素 |
| `scroll_and_find` | 自動滾動直到找到元素 |
| `navigate_back` | 返回 + 驗證導航 |
| `dismiss_popup` | 關閉常見對話框（確定、取消、關閉等） |
| `launch_and_wait` | 啟動 App + 等待就緒指示 |
| `get_screen_summary` | 畫面狀態概覽，含可見文字 |
| `run_patrol` | 完整的社群媒體瀏覽自動化 |

### 設定方式

加入到你的 MCP 設定：

```json
{
  "mcpServers": {
    "mobile-macro": {
      "command": "python",
      "args": ["-m", "src.mcp_macro_server"],
      "cwd": "<專案路徑>"
    }
  }
}
```

## 🎯 uiautomator2 整合

要獲得最可靠的自動化體驗，請安裝 uiautomator2：

```bash
pip install uiautomator2
python -m uiautomator2 init
```

### 優勢比較

| 操作 | 座標式 | 選擇器式 (u2) |
|------|--------|---------------|
| 點擊按鈕 | `router.click(x=540, y=1200)` | `router.click(text="搜尋")` |
| 尋找元素 | 截圖 + 視覺辨識 | 直接選擇器查詢 |
| 等待元素 | 輪詢截圖 | 原生等待支援 |
| 穩定性 | 依賴螢幕尺寸 | 跨裝置通用 |

### 程式碼使用

```python
from src.tool_router import ToolRouter

router = ToolRouter()  # 自動偵測 u2

# 選擇器式點擊（最可靠）
router.click(text="搜尋")
router.click_by_selector(resourceId="com.app:id/btn", clickable=True)

# 智慧等待
router.wait_for_element_u2(text="載入中", gone=True, timeout=10)

# 滾動尋找
found, el = router.scroll_to_element(text="設定", max_scrolls=5)
```

## 🎓 Skills 系統

MobileAgent 採用開放的 [Agent Skills 規範](https://agentskills.io) 來定義 AI 代理能力。Skills 存放於 `.skills/` 目錄，執行 `set.sh` 時會自動部署到偵測到的 AI Agents。

### Agent Skills 標準

每個 skill 遵循規範，包含正確的 frontmatter：

```yaml
---
name: skill-name
description: 功能說明與使用時機
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
---
```

### 支援的 AI Agents

| AI Agent | Skills 目錄 | MCP 配置 |
|----------|------------|----------|
| Cursor | `.cursor/skills/` | `.cursor/mcp.json` |
| Claude Code | `.claude/skills/` | `.mcp.json` |
| Gemini CLI | `.gemini/skills/` | `.gemini/settings.json` |
| Codex CLI | `.codex/skills/` | `.codex/config.toml` |
| Roo Code | `.roo/skills/` | `.roo/mcp.json` |
| Windsurf | `.windsurf/skills/` | 僅全域配置 |

### 新增 Skill

1. 在 `.skills/` 下建立新目錄
2. 建立 `SKILL.md` 檔案（含正確的 frontmatter）
3. 執行 `./set.sh` 驗證並部署

詳細的 Agent Skills 規範與範例請參閱 `.skills/README.md`。

### 🏄 海巡技能 (Patrol Skill)

像海巡署查緝走私一樣，**主動搜尋**特定關鍵字，**緊盯**相關貼文，**收集情報**回報給用戶。

使用範例：
```
用戶：「打開 Threads 搜尋 clawdbot，看看網路上對這個工具的評價」

AI Agent 會：
1. 啟動 Threads app
2. 搜尋 "clawdbot"
3. 瀏覽 5+ 篇相關貼文
4. 閱讀留言和反應
5. 回報：「以下是大家對 clawdbot 的評價...」
```

AI Agent 會自主執行 MCP 工具，內部追蹤已訪問的貼文，避免重複。

### 📄 內容擷取技能 (Content Extract Skill)

擷取**完整內容**（非摘要）並進行結構化 NLP 分析：

- **完整文字擷取**：完整文章內容，不截斷
- **NLP 分析**：人（人物）、事（事件）、時（時間）、地（地點）、物（事物/產品）
- **關鍵字**：主要詞彙和主題，含信心分數
- **JSON 輸出**：標準化 Schema，便於 API 串接
- **儲存檔案**：JSON（主要）和 Markdown（次要），存放於 `outputs/` 目錄

JSON 輸出結構範例：
```json
{
  "extraction_meta": {
    "version": "2.0",
    "extracted_at": "2024-01-29T10:30:00+08:00",
    "platform": "WeChat",
    "extraction_status": "success"
  },
  "articles": [{
    "title": "文章標題",
    "content": { "full_text": "...", "word_count": 342 },
    "nlp_analysis": {
      "who": [{ "value": "人名", "confidence": 0.95 }],
      "what": [{ "value": "事件描述", "confidence": 0.90 }]
    },
    "keywords": ["AI", "科技"],
    "sentiment": "positive"
  }]
}
```

### 📱 App 探索技能 (App Explore Skill)

主要的 App 操作技能，帶有研究思維：

| 平台 | 功能 |
|------|------|
| LINE, WeChat, Telegram, WhatsApp | 傳訊息、搜尋聯絡人 |
| Facebook, Instagram, Threads, X | 按讚、留言、分享、追蹤 |
| YouTube, TikTok | 按讚、留言、訂閱 |
| Gmail, LinkedIn, Discord, Snapchat | 各平台特定操作 |

特色：
- **Element-First 策略**：優先使用元素樹，而非截圖
- **Click-Verify 協議**：每次點擊都驗證是否成功
- 分離式 UI 參考檔，按需載入節省 tokens
- 多語言 UI 關鍵字對照（EN/zh/JP/KR）

## 🖥️ Web UI

啟動網頁控制面板：

```bash
source .venv/bin/activate
pip install flask
python web/app.py
```

開啟瀏覽器訪問 http://localhost:6443

### 功能

- 查看已連接裝置
- 選擇 CLI 工具（Gemini/Claude/Codex）與模型
- 即時查看任務輸出
- 任務歷史紀錄
- 繁體中文/英文介面切換

### 截圖展示

| 主控台 | 新增任務 |
|:------:|:--------:|
| ![主控台](images/webui-dashboard.png) | ![新增任務](images/webui-new-task.png) |
| 查看已連接裝置與任務歷史 | 選擇 CLI 工具、模型，描述任務 |

| 任務執行中 | 任務完成 |
|:----------:|:--------:|
| ![執行中](images/webui-with-device.png) | ![完成](images/webui-task-completed.png) |
| 即時輸出搭配裝置畫面 | 查看結果與任務摘要 |

## 💻 使用範例

### Python API

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()
adb.screenshot(prefix="step1")
adb.tap(540, 1200)
adb.type_text("搜尋關鍵字")
adb.press_enter()
```

### 確定性執行器

```python
from src.executor import DeterministicExecutor

executor = DeterministicExecutor()

# 觀察 → 尋找 → 點擊 → 驗證
state = executor.observe()
element = executor.find_element(text="搜尋")
if element:
    result = executor.click_and_verify(element)
    if result.result == ActionResult.SUCCESS:
        print("點擊驗證成功！")
```

### Tool Router（統一介面）

```python
from src.tool_router import ToolRouter

router = ToolRouter()

# 自動選擇最佳工具（u2 > MCP > ADB）
router.click(text="搜尋")           # 依文字尋找並點擊
router.type_text("你好 Hello")      # 支援 Unicode
router.swipe("up", verify=True)    # 滾動並驗證
router.wait_for_element(text="結果")
```

### 海巡自動化

```python
from src.patrol import PatrolStateMachine, PatrolConfig

config = PatrolConfig(max_posts=10, max_scrolls=5)
patrol = PatrolStateMachine(platform="threads", config=config)
report = patrol.run(keyword="AI agents")

print(f"已訪問 {len(report.posts)} 篇貼文")
print(report.summary)
```

## ❓ 常見問題

### Q: 無法連接裝置？

```bash
adb kill-server && adb start-server
adb devices
```

### Q: 文字輸入失敗？

```python
from src.adb_helper import setup_adbkeyboard
setup_adbkeyboard()
```

或安裝 DeviceKit APK（用於 MCP）：
```bash
adb install apk_tools/mobilenext-devicekit.apk
```

### Q: 如何查看日誌？

`temp/logs/mobile_agent_YYYYMMDD.log`

### Q: 如何啟用 uiautomator2？

```bash
pip install uiautomator2
python -m uiautomator2 init
```

ToolRouter 會自動偵測並使用。

## 📜 授權

本專案採用 [MIT License](../LICENSE)。

### 相依工具授權

| 工具/套件 | 授權 | 說明 |
|-----------|------|------|
| MCP (Model Context Protocol) | Open Source (Linux Foundation) | Anthropic 捐贈給 Agentic AI Foundation |
| mobile-mcp | Apache-2.0 | MCP server for mobile automation |
| context7 | MIT | 文件查詢 MCP server |
| uiautomator2 | MIT | Android 自動化函式庫 |
| ADB (Android Debug Bridge) | Apache-2.0 | Android SDK Platform Tools |
| ADBKeyboard | GPL-2.0 | Unicode 輸入支援 |
| Flask | BSD-3-Clause | Web UI 框架 |

## 📧 聯繫

- **問題回報**: [GitHub Issues](https://github.com/sheng1111/MobileAgent/issues)
- **討論**: [GitHub Discussions](https://github.com/sheng1111/MobileAgent/discussions)

---

<p align="center">
  <strong>以 ❤️ 為 AI Agent 社群打造</strong>
</p>
