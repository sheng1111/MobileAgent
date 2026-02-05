# MobileAgent Skills

Specialized skills for AI agents. Each skill is focused and non-overlapping.

> **Note**: These are **MobileAgent-specific skills** following the [Agent Skills Specification](https://agentskills.io). They are compatible with multiple AI agents (Cursor, Claude Code, Gemini CLI, OpenAI Codex, Windsurf, Roo Code, GitHub Copilot). These are **NOT** GitHub Copilot skills replacements.

## Agent Skills Standard

MobileAgent skills follow the open [Agent Skills specification](https://agentskills.io/specification):

### SKILL.md Format

Each skill directory contains a `SKILL.md` file with:

```yaml
---
name: skill-name                    # Required: lowercase, hyphens only
description: What this skill does   # Required: when to use it (max 1024 chars)
license: MIT                        # Optional: license info
metadata:                           # Optional: additional info
  author: MobileAgent
  version: "1.0"
compatibility: Requires X, Y       # Optional: environment requirements
---

# Skill Title

Instructions for the AI agent...
```

### Progressive Disclosure

Skills are loaded efficiently:
1. **Metadata** (~100 tokens): `name` and `description` loaded at startup
2. **Instructions** (<5000 tokens): Full `SKILL.md` loaded when activated
3. **References** (as needed): Files in `references/` loaded on demand

### Optional Directories

```
skill-name/
├── SKILL.md          # Required: main instructions
├── references/       # Optional: detailed docs (loaded on-demand)
│   └── platform.md
├── scripts/          # Optional: executable code
└── assets/           # Optional: templates, data
```

---

## Skill Categories

### A. Task Planning & Interaction

| Skill | Purpose |
|-------|---------|
| **task-clarify** | Convert user requests into structured task specs |
| **progress-report** | Report progress with screenshots and evidence |

### B. Exploration & Search

| Skill | Purpose |
|-------|---------|
| **app-explore** | Main skill for app operations with research mindset |
| **search-triage** | Multi-round search, produce candidate list |
| **comment-scan** | Deep-read comments, analyze sentiment |
| **patrol** | Autonomous keyword monitoring (海巡) |

### C. Content Extraction

| Skill | Purpose |
|-------|---------|
| **content-extract** | Full content + NLP analysis (JSON output) |
| **article-extract** | Extract complete article content |
| **wechat-browse** | Browse WeChat Official Accounts |

### D. Commenting & Interaction

| Skill | Purpose |
|-------|---------|
| **comment-draft** | Generate comment drafts (no app ops) |
| **comment-post** | Post and verify comments |

### E. Memory & Learning

| Skill | Purpose |
|-------|---------|
| **memory** | Record observations and learnings during task execution |

### F. Utility Skills

| Skill | Purpose |
|-------|---------|
| **app-action** | Single-step operations (quick actions) |
| **screen-analyze** | Analyze screen state, find elements |
| **device-check** | Verify device connection |
| **troubleshoot** | Diagnose and fix issues systematically |
| **unicode-setup** | Configure Unicode input |

---

## Skill Selection Guide

### "Search for opinions about X on Threads"

```
task-clarify → search-triage → comment-scan → progress-report
```

### "Browse WeChat accounts and get articles"

```
wechat-browse → article-extract (outputs JSON for dedup)
```

### "Find and comment on AI discussions"

```
task-clarify → search-triage → comment-scan → comment-draft → comment-post
```

### "Quick patrol"

```
patrol (automated)
```

### Simple single action

```
app-action (for tap, type, swipe)
```

---

## AI Agent Compatibility

| Agent | Skills Directory | MCP Config (Project-Level) | Reference |
|-------|-----------------|---------------------------|-----------|
| **Cursor** | `.cursor/skills/` | `.cursor/mcp.json` | [Cursor MCP](https://cursor.com/docs/context/mcp) |
| **Claude Code** | `.claude/skills/` | `.mcp.json` | [Claude Code MCP](https://code.claude.com/docs/en/mcp) |
| **Gemini CLI** | `.gemini/skills/` | `.gemini/settings.json` | [Gemini CLI Config](https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html) |
| **OpenAI Codex** | `.codex/skills/` | `.codex/config.toml` | [Codex MCP](https://developers.openai.com/codex/mcp/) |
| **Roo Code** | `.roo/skills/` | `.roo/mcp.json` | [Roo Code MCP](https://docs.roocode.com/features/mcp/using-mcp-in-roo) |
| **GitHub Copilot** | `.github/skills/` | - | [Copilot Skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| **Windsurf** | `.windsurf/skills/` | ⚠️ Global only | [Windsurf MCP](https://docs.windsurf.com/plugins/cascade/mcp) |

> **Note**: Windsurf only supports global MCP config (`~/.codeium/mcp_config.json`), no project-level config.

Run `./set.sh` to automatically deploy skills to all detected AI agents.

---

## Directory Structure

```
.skills/
├── README.md              # This file
│
├── task-clarify/          # A. Planning
├── progress-report/
│
├── app-explore/           # B. Search & Exploration
│   └── references/        #    Platform UI references (load on demand)
├── search-triage/
├── comment-scan/
├── patrol/
│
├── content-extract/       # C. Content Extraction
├── article-extract/
├── wechat-browse/
│
├── comment-draft/         # D. Commenting
├── comment-post/
│
├── memory/                # E. Memory & Learning
│
├── app-action/            # F. Utility
├── screen-analyze/
├── device-check/
├── troubleshoot/
└── unicode-setup/
```

---

## Core Strategy: Element-First

```
FAST:  mobile_list_elements → find by text/id → click center
SLOW:  screenshot → guess coordinates → miss → retry
```

**Why?**
- Element list: ~100ms, pixel-perfect bounds
- Screenshot + vision: 2-5s, error-prone guessing

---

## Adding New Skills

### 1. Create directory

```bash
mkdir -p .skills/my-skill
```

### 2. Create SKILL.md

```yaml
---
name: my-skill
description: Clear description of what it does and when to use it. Include keywords that trigger this skill.
license: MIT
metadata:
  author: Your Name
  version: "1.0"
---

# My Skill

## When to Use This Skill

- Situation 1
- Situation 2

## Instructions

Step-by-step guidance...
```

### 3. Validate and deploy

```bash
./set.sh
```

The script validates frontmatter and deploys to detected AI agents.

---

## Deployment Options

```bash
# Default: symlinks (dev mode, changes apply immediately)
./set.sh

# Force copy mode (CI/CD or restricted permissions)
./set.sh --copy
MOBILE_AGENT_FORCE_COPY=1 ./set.sh
```

---

## External Resources

- [Agent Skills Specification](https://agentskills.io/specification) - Official format spec
- [Anthropic Skills](https://github.com/anthropics/skills) - Example skills
- [OpenAI Codex Skills](https://github.com/openai/skills) - Codex skill catalog
- [Awesome Agent Skills](https://github.com/VoltAgent/awesome-agent-skills) - Community collection
