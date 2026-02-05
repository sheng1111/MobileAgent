# Skills Deployment Strategy: Copy vs Symbolic Links

## Executive Summary

**Recommendation:** Use symbolic links for development, with copy fallback for cross-platform compatibility.

---

## Background

The `set.sh` script deploys skills from `.skills/` to various AI agent directories:
- `.cursor/skills/`
- `.claude/skills/`
- `.gemini/skills/`
- `.codex/skills/`
- `.windsurf/skills/`
- `.roo/skills/`

Currently, deployment uses `cp -r` (copy), creating independent copies.

---

## Analysis

### Option A: Copy (Current Approach)

**Advantages:**
- Works on all platforms (Linux, macOS, Windows)
- No permission issues
- Works in containers and CI/CD
- Each agent has isolated copy (no cross-interference)

**Disadvantages:**
- Multiple copies can drift out of sync
- Must re-run `set.sh` after every skill change
- Wastes disk space (minor)
- Easy to forget to sync

### Option B: Symbolic Links

**Advantages:**
- Single source of truth - changes reflect immediately
- No drift between copies
- Faster iteration during development
- Better for git (only `.skills/` needs tracking)

**Disadvantages:**
- Windows requires admin/developer mode for symlinks
- Some CI/CD systems don't follow symlinks well
- Some editors/tools may not resolve symlinks properly
- Cross-filesystem symlinks can fail

### Option C: Hybrid (Recommended)

Use symlinks by default, fall back to copy if symlink creation fails.

**Advantages:**
- Best of both worlds
- Works in development (symlinks)
- Works in CI/CD (fallback to copy)
- Self-healing on different platforms

---

## Platform Considerations

### Linux
- Full symlink support
- No special permissions needed
- Recommended: Use symlinks

### macOS
- Full symlink support
- No special permissions needed
- Recommended: Use symlinks

### Windows
- Requires Developer Mode OR admin privileges for symlinks
- Without privileges, symlink creation fails silently
- Recommended: Try symlinks, fallback to copy

### CI/CD / Containers
- Symlinks may not work across mount boundaries
- Some tools strip symlinks during copy/archive
- Recommended: Copy fallback essential

---

## Relationship with Codex TOML Config

The Codex CLI uses TOML format (`~/.codex/config.toml`) for MCP configuration:

```toml
[mcp_servers.mobile-mcp]
command = "npx"
args = ["-y", "@mobilenext/mobile-mcp@latest"]
```

**Important distinction:**
- MCP config (`config.toml`): Tells agent which tools are available
- Skills deployment: Tells agent how to use those tools

These are separate concerns:
- Changing from copy to symlink does NOT affect TOML format
- TOML handles tool discovery, skills handle behavior
- Both coexist independently

---

## Implementation

### Recommended Changes to `set.sh`

```bash
# Deploy skills using symlinks (with copy fallback)
deploy_skills_to() {
    local agent_name="$1"
    local target_dir="$2"
    local use_symlink="${3:-true}"

    mkdir -p "$target_dir"

    local deployed=0
    local method="symlink"

    for skill_dir in "$SKILLS_SOURCE"/*/; do
        if [ -d "$skill_dir" ] && [ -f "${skill_dir}SKILL.md" ]; then
            local skill_name=$(basename "$skill_dir")
            local dest="${target_dir}/${skill_name}"

            # Remove existing (whether file, dir, or symlink)
            rm -rf "$dest"

            if [ "$use_symlink" = true ]; then
                # Try symlink first
                if ln -s "$skill_dir" "$dest" 2>/dev/null; then
                    deployed=$((deployed + 1))
                else
                    # Fallback to copy
                    cp -r "$skill_dir" "$dest"
                    method="copy (symlink failed)"
                    deployed=$((deployed + 1))
                fi
            else
                # Force copy mode
                cp -r "$skill_dir" "$dest"
                method="copy"
                deployed=$((deployed + 1))
            fi
        fi
    done

    echo -e "${GREEN}[OK]${NC} ${agent_name}: ${deployed} skill(s) via ${method} -> ${target_dir}"
}
```

### Verification Script

After deployment, verify skills are accessible:

```bash
verify_skills() {
    local target_dir="$1"
    local count=0

    for skill_dir in "$target_dir"/*/; do
        if [ -f "${skill_dir}SKILL.md" ]; then
            count=$((count + 1))
        elif [ -L "$skill_dir" ] && [ -f "$(readlink -f "$skill_dir")/SKILL.md" ]; then
            count=$((count + 1))
        fi
    done

    echo "$count"
}
```

---

## Risk Mitigation

### If Symlinks Don't Work

1. Run `set.sh --copy` to force copy mode
2. Add `MOBILE_AGENT_FORCE_COPY=1` environment variable
3. Script automatically falls back to copy

### If Skills Get Out of Sync

1. Re-run `set.sh` to re-sync
2. With symlinks, this is unnecessary (changes auto-propagate)

### If Agent Can't Find Skills

1. Check target directory exists
2. Verify symlinks resolve: `readlink -f .claude/skills/patrol`
3. Check file permissions
4. Try copy mode as fallback

---

## Testing Checklist

- [ ] Skills deploy to all detected agents
- [ ] Symlinks resolve correctly (Linux/macOS)
- [ ] Fallback to copy works (Windows/CI)
- [ ] Skill changes reflect immediately (symlink mode)
- [ ] Validation passes after deployment
- [ ] Agents can discover and use skills

---

## Conclusion

Adopting the hybrid approach provides:
1. **Development efficiency** - immediate skill updates via symlinks
2. **Cross-platform support** - copy fallback ensures compatibility
3. **Single source of truth** - `.skills/` is the canonical location
4. **No breaking changes** - existing workflows continue to work

The TOML format for Codex remains unchanged; this only affects how skill files are deployed, not how MCP tools are configured.
