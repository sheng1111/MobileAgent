# MobileAgent Skills

統一的 AI Agent Skills 來源目錄。執行 `./set.sh` 後會自動驗證並部署到偵測到的 AI Agent 對應目錄。

## 支援的 AI Agents

| AI Agent | 專案層級路徑 | 偵測方式 |
|----------|-------------|---------|
| Cursor | `.cursor/skills/` | `~/.cursor/` 目錄存在 |
| Claude Code | `.claude/skills/` | `claude` 指令或 `~/.claude/` |
| Gemini CLI | `.gemini/skills/` | `gemini` 指令或 `~/.gemini/` |
| Codex CLI | `.codex/skills/` | `codex` 指令或 `~/.codex/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/` 目錄存在 |
| Roo Code | `.roo/skills/` | `~/.roo/` 目錄存在 |

## 目錄結構

```
.skills/
├── README.md
├── app-action/
│   └── SKILL.md
├── device-check/
│   └── SKILL.md
├── screen-analyze/
│   └── SKILL.md
├── troubleshoot/
│   └── SKILL.md
└── unicode-setup/
    └── SKILL.md
```

## Skill 格式

每個 skill 必須包含 `SKILL.md` 檔案，開頭需要 YAML frontmatter：

```markdown
---
name: skill-name
description: 描述此 skill 的用途以及何時使用。
---

# Skill 標題

詳細說明...
```

### 必要欄位

| 欄位 | 說明 |
|------|------|
| `name` | Skill 識別名稱，只能包含小寫字母、數字和連字號 |
| `description` | 描述功能與觸發時機，Agent 會根據此決定是否啟用 |

## 新增 Skill

1. 在 `.skills/` 下建立新目錄
2. 建立 `SKILL.md` 檔案（含 frontmatter）
3. 執行 `./set.sh` 驗證並部署

## 附加資源

Skill 可以包含額外目錄存放支援檔案：

```
.skills/
└── deploy-workflow/
    ├── SKILL.md
    ├── scripts/
    │   └── deploy.sh
    └── references/
        └── checklist.md
```

## 相關文件

- Agent Skills 規範: https://agentskills.io/
- AGENTS.md - Agent 行為指南
- CLAUDE.md - 專案概覽
