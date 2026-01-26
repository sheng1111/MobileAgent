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
├── app-action/
│   └── SKILL.md
├── device-check/
│   └── SKILL.md
├── screen-analyze/
│   └── SKILL.md
├── social-media/
│   ├── SKILL.md
│   └── references/
├── troubleshoot/
│   └── SKILL.md
└── unicode-setup/
    └── SKILL.md
```

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
└── deploy-workflow/
    ├── SKILL.md
    ├── scripts/
    │   └── deploy.sh
    └── references/
        └── checklist.md
```

## Related Documentation

- Agent Skills Specification: https://agentskills.io/
- AGENTS.md - Agent behavior guidelines
- CLAUDE.md - Project overview
