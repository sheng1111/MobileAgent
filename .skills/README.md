# MobileAgent Skills

Unified AI Agent Skills source directory. Running `./set.sh` automatically validates and deploys skills to detected AI Agent directories.

## Supported AI Agents

| AI Agent | Project Path | Detection Method |
|----------|--------------|------------------|
| Cursor | `.cursor/skills/` | `~/.cursor/` directory exists |
| Claude Code | `.claude/skills/` | `claude` command or `~/.claude/` |
| Gemini CLI | `.gemini/skills/` | `gemini` command or `~/.gemini/` |
| Codex CLI | `.codex/skills/` | `codex` command or `~/.codex/` |
| Windsurf | `.windsurf/skills/` | `~/.codeium/` directory exists |
| Roo Code | `.roo/skills/` | `~/.roo/` directory exists |

## Directory Structure

```
.skills/
├── README.md
├── app-explore/          # Main skill: app operations + research mindset
│   ├── SKILL.md
│   └── references/       # App-specific UI patterns
│       ├── package-names.md
│       └── ui-*.md
├── app-action/           # Quick single-step operations
│   └── SKILL.md
├── patrol/               # Search & monitor keywords (海巡)
│   └── SKILL.md
├── content-extract/      # Full content extraction + NLP analysis
│   └── SKILL.md
├── device-check/         # Device connection verification
│   └── SKILL.md
├── screen-analyze/       # Screen state analysis
│   └── SKILL.md
├── troubleshoot/         # Diagnostics and fixes
│   └── SKILL.md
└── unicode-setup/        # Unicode input configuration
    └── SKILL.md
```

## Skill Overview

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| **app-explore** | App operations with research mindset | Research, browse, multi-step tasks |
| **app-action** | Quick single-step operations | Launch, tap, type, simple tasks |
| **patrol** | Systematic social media browsing | Search → browse posts → read comments → collect |
| **device-check** | Verify device connection | Before automation, connection issues |
| **screen-analyze** | Analyze current screen | Find elements, understand UI state |
| **troubleshoot** | Fix common issues | Errors, failures, debugging |
| **unicode-setup** | Configure text input | Non-ASCII text needed |

## Core Strategy: Element-First

**All skills follow the Element-First strategy for speed and accuracy.**

```
FAST & RELIABLE:
1. mobile_list_elements_on_screen (accessibility tree)
2. Find target by text/type/identifier
3. Click at element center

SLOW & ERROR-PRONE (avoid):
1. mobile_take_screenshot
2. LLM guesses coordinates from image
3. Frequent misclicks → retry loop
```

See `AGENTS.md` for detailed guidelines.

## Skill Format

Each skill must contain a `SKILL.md` file with YAML frontmatter:

```markdown
---
name: skill-name
description: Describe what this skill does and when to use it.
---

# Skill Title

Detailed instructions...
```

### Required Fields

| Field | Description |
|-------|-------------|
| `name` | Skill identifier, lowercase letters, numbers, and hyphens only |
| `description` | Describes functionality and trigger conditions, Agent uses this to decide activation |

## Adding a Skill

1. Create a new directory under `.skills/`
2. Create a `SKILL.md` file (with frontmatter)
3. Run `./set.sh` to validate and deploy

## Additional Resources

Skills can include extra directories for supporting files:

```
.skills/
└── my-skill/
    ├── SKILL.md
    ├── scripts/
    │   └── helper.py
    └── references/
        └── data.md
```

## Related Documentation

- Agent Skills Specification: https://agentskills.io/
- AGENTS.md - Agent behavior guidelines
- CLAUDE.md - Project overview
