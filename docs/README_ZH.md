# MobileAgent - AI 驅動的手機自動化框架

[English README](../README.md)

透過 AI Agent 與 MCP (Model Context Protocol) 控制 Android 裝置的自動化框架。

## 功能特色

- Web UI - 網頁介面管理裝置與任務，支援繁中/英文
- MCP 整合 - 支援 mobile-mcp、filesystem、fetch、context7 等 MCP 伺服器
- AI Agent 相容 - 支援 Cursor、Claude Code、Gemini CLI、Codex、Windsurf、Roo Code
- Skills 系統 - 統一的 Skills 來源，自動部署到偵測到的 AI Agents
- 多模型支援 - Gemini、Claude、GPT 等最新模型
- ADB 輔助腳本 - 當 MCP 工具受限時的備援方案
- Unicode 輸入 - 透過 ADBKeyboard 支援中文、表情符號等

## 系統需求

- Python 3.8+
- Node.js 18+
- Android SDK Platform Tools (ADB)
- Android 裝置（已啟用 USB 偵錯）

## 快速開始

### 1. 執行設定腳本

```bash
chmod +x set.sh && ./set.sh
```

這會自動：
- 建立 Python 虛擬環境並安裝相依套件
- 設定各 AI CLI 工具的 MCP 設定
- 驗證並部署 Skills 到偵測到的 AI Agents

### 2. 驗證環境

```bash
python tests/test_environment.py
```

### 3. 設定 AI Agent

將 `mcp/mcp_setting.json` 複製到你的 AI Agent 設定中。

### 4. 連接裝置

```bash
adb devices
```

## 專案結構

```
MobileAgent/
├── AGENTS.md           # AI Agent 使用指南（必讀）
├── CLAUDE.md           # Claude Code 參考
├── GEMINI.md           # Gemini CLI 參考
├── set.sh              # 設定腳本（含 Skills 部署）
├── .skills/            # Skills 來源目錄
│   ├── app-explore/    # 主要技能：App 操作 + 研究思維
│   ├── app-action/     # 快速單步操作
│   ├── patrol/         # 海巡技能（搜尋關鍵字、監控輿情）
│   ├── content-extract/# 完整內容擷取 + NLP 分析
│   ├── device-check/   # 裝置連線檢查
│   ├── screen-analyze/ # 畫面狀態分析
│   ├── troubleshoot/   # 問題診斷
│   └── unicode-setup/  # Unicode 輸入設定
├── src/                # Python 模組
│   ├── adb_helper.py   # ADB 指令封裝
│   ├── logger.py       # 日誌模組
│   ├── executor.py     # 確定性執行器（Element-First 強制）
│   ├── tool_router.py  # 統一 MCP/ADB 介面
│   ├── state_tracker.py # 導航狀態機
│   └── patrol.py       # 海巡自動化（程式化使用）
├── web/                # Web UI
│   ├── app.py          # Flask 後端
│   ├── static/         # CSS/JS
│   └── templates/      # HTML
├── tests/              # 單元測試
├── mcp/                # MCP 設定
├── apk_tools/          # APK 工具
├── outputs/            # 截圖、下載、摘要
└── temp/logs/          # 日誌檔案
```

## Skills 系統

MobileAgent 使用統一的 Skills 來源目錄 (`.skills/`)，執行 `set.sh` 時會自動偵測已安裝的 AI Agents 並部署對應的 skills。

### 支援的 AI Agents

| AI Agent | 偵測方式 | 部署路徑 |
|----------|---------|---------|
| Cursor | `~/.cursor/` 存在 | `.cursor/skills/` |
| Claude Code | `claude` 指令或 `~/.claude/` | `.claude/skills/` |
| Gemini CLI | `gemini` 指令或 `~/.gemini/` | `.gemini/skills/` |
| Codex CLI | `codex` 指令或 `~/.codex/` | `.codex/skills/` |
| Windsurf | `~/.codeium/` 存在 | `.windsurf/skills/` |
| Roo Code | `~/.roo/` 存在 | `.roo/skills/` |

### 新增 Skill

1. 在 `.skills/` 下建立新目錄
2. 建立 `SKILL.md` 檔案（含 frontmatter）
3. 執行 `./set.sh` 驗證並部署

詳細說明請參閱 `.skills/README.md`。

### 海巡技能 (Patrol Skill)

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

### 內容擷取技能 (Content Extract Skill)

擷取**完整內容**（非摘要）並進行結構化 NLP 分析：

- **完整文字擷取**：完整文章內容，不截斷
- **NLP 分析**：人（人物）、事（事件）、時（時間）、地（地點）、物（事物/產品）
- **關鍵字**：主要詞彙和主題
- **儲存檔案**：JSON 和/或 Markdown 格式，存放於 `outputs/` 目錄

使用範例：
```
用戶：「看微信公眾號 36氪 的最新文章，提取完整內容，分析人事時地物」

AI Agent 會：
1. 導航到微信公眾號
2. 找到並開啟文章
3. 滾動並擷取完整內容
4. 進行 NLP 分析（人/事/時/地/物）
5. 儲存結構化輸出到 outputs/2024-01-29/wechat_36kr_article.json
```

### App 探索技能 (App Explore Skill)

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

## Web UI

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

## 使用範例

```python
from src.adb_helper import ADBHelper

adb = ADBHelper()
adb.screenshot(prefix="step1")
adb.tap(540, 1200)
adb.type_text("搜尋關鍵字")
adb.press_enter()
```

## 常見問題

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

### Q: 如何查看日誌？

`temp/logs/mobile_agent_YYYYMMDD.log`

## 授權

本專案採用 [MIT License](LICENSE)。

### 相依工具授權

| 工具/套件 | 授權 | 說明 |
|-----------|------|------|
| MCP (Model Context Protocol) | Open Source (Linux Foundation) | Anthropic 捐贈給 Agentic AI Foundation |
| mobile-mcp | Apache-2.0 | MCP server for mobile automation |
| context7 | MIT | 文件查詢 MCP server |
| ADB (Android Debug Bridge) | Apache-2.0 | Android SDK Platform Tools |
| ADBKeyboard | GPL-2.0 | Unicode 輸入支援 |
| Flask | BSD-3-Clause | Web UI 框架 |
