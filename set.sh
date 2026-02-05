#!/bin/bash
# MobileAgent Setup Script
# Sets up Python virtual environment, MCP configuration, and deploys Skills to detected AI Agents
#
# Usage:
#   ./set.sh           # Normal setup (symlinks for skills)
#   ./set.sh --copy    # Force copy mode for skills
#   MOBILE_AGENT_FORCE_COPY=1 ./set.sh  # Alternative force copy

set -e

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --copy)
            export MOBILE_AGENT_FORCE_COPY=true
            echo "Force copy mode enabled"
            shift
            ;;
        --help|-h)
            echo "Usage: ./set.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --copy    Force copy mode for skills deployment (instead of symlinks)"
            echo "  --help    Show this help message"
            echo ""
            echo "Environment variables:"
            echo "  MOBILE_AGENT_FORCE_COPY=1    Force copy mode"
            exit 0
            ;;
    esac
done

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
MCP_DIR="${SCRIPT_DIR}/mcp"
MCP_EXAMPLE="${MCP_DIR}/mcp_setting.json.example"
MCP_CONFIG="${MCP_DIR}/mcp_setting.json"
REQUIREMENTS="${SCRIPT_DIR}/requirements.txt"
SKILLS_SOURCE="${SCRIPT_DIR}/.skills"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   MobileAgent Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Project path: ${GREEN}${SCRIPT_DIR}${NC}"
echo ""

# =============================================================================
# Check Dependencies
# =============================================================================
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} $1 found"
        return 0
    else
        echo -e "${RED}[MISSING]${NC} $1 not found"
        return 1
    fi
}

echo -e "${YELLOW}Checking dependencies...${NC}"
echo ""

MISSING_DEPS=0

check_command "python3" || MISSING_DEPS=1
check_command "node" || MISSING_DEPS=1
check_command "npm" || MISSING_DEPS=1
check_command "npx" || MISSING_DEPS=1
check_command "adb" || MISSING_DEPS=1

echo ""

if [ $MISSING_DEPS -eq 1 ]; then
    echo -e "${YELLOW}Warning: Some dependencies are missing.${NC}"
    echo "Please install them before using MobileAgent:"
    echo "  - Python 3.8+: https://www.python.org/"
    echo "  - Node.js 18+: https://nodejs.org/"
    echo "  - ADB: Install via Android SDK Platform Tools"
    echo ""
fi

# =============================================================================
# Python Virtual Environment
# =============================================================================
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
echo ""

if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}[OK]${NC} Virtual environment already exists: ${VENV_DIR}"
else
    echo -e "${BLUE}[INFO]${NC} Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}[OK]${NC} Virtual environment created: ${VENV_DIR}"
fi

# Activate virtual environment
echo -e "${BLUE}[INFO]${NC} Activating virtual environment..."
source "${VENV_DIR}/bin/activate"
echo -e "${GREEN}[OK]${NC} Virtual environment activated"

# Upgrade pip
echo -e "${BLUE}[INFO]${NC} Upgrading pip..."
"${VENV_DIR}/bin/pip" install --upgrade pip -q

# Install requirements
if [ -f "$REQUIREMENTS" ]; then
    echo -e "${BLUE}[INFO]${NC} Installing requirements..."
    "${VENV_DIR}/bin/pip" install -r "$REQUIREMENTS" -q
    echo -e "${GREEN}[OK]${NC} Requirements installed"
else
    echo -e "${YELLOW}[SKIP]${NC} No requirements.txt found"
fi

# Install uiautomator2 (recommended for selector-based automation)
echo -e "${BLUE}[INFO]${NC} Installing uiautomator2..."
"${VENV_DIR}/bin/pip" install uiautomator2 -q
echo -e "${GREEN}[OK]${NC} uiautomator2 installed"

# If device connected, auto-initialize u2
if command -v adb &> /dev/null; then
    DEVICE_COUNT=$(adb devices 2>/dev/null | grep -v "^List" | grep -v "^$" | wc -l)
    if [ "$DEVICE_COUNT" -gt 0 ]; then
        echo -e "${BLUE}[INFO]${NC} Detected ${DEVICE_COUNT} device(s), initializing uiautomator2..."
        "${VENV_DIR}/bin/python" -m uiautomator2 init 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} u2 init failed (device may need USB debugging enabled)"
        echo -e "${GREEN}[OK]${NC} uiautomator2 initialized on device"
    else
        echo -e "${YELLOW}[INFO]${NC} No device connected - run 'python -m uiautomator2 init' later"
    fi
fi

echo ""

# =============================================================================
# MCP Configuration
# =============================================================================
echo -e "${YELLOW}Configuring MCP settings...${NC}"
echo ""

mkdir -p "$MCP_DIR"

if [ ! -f "$MCP_EXAMPLE" ]; then
    echo -e "${RED}[ERROR]${NC} MCP example file not found: ${MCP_EXAMPLE}"
    echo "Creating default example file..."
    
    cat > "$MCP_EXAMPLE" << 'EOF'
{
  "_comment": "MobileAgent MCP Configuration Example - Copy to your AI Agent settings",
  "_usage": "Replace <PROJECT_PATH> with your actual project path, e.g., /home/user/MobileAgent",
  "mcpServers": {
    "mobile-mcp": {
      "command": "npx",
      "args": ["-y", "@mobilenext/mobile-mcp@latest"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "<PROJECT_PATH>"
      ]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
EOF
    echo -e "${GREEN}[OK]${NC} Default example file created"
fi

echo -e "${BLUE}[INFO]${NC} Generating MCP configuration..."
sed "s|<PROJECT_PATH>|${SCRIPT_DIR}|g" "$MCP_EXAMPLE" > "$MCP_CONFIG"
sed -i "s|MobileAgent MCP Configuration Example.*|MCP configuration ready. Project path: ${SCRIPT_DIR}|g" "$MCP_CONFIG"
echo -e "${GREEN}[OK]${NC} MCP configuration generated: ${MCP_CONFIG}"

echo ""

# =============================================================================
# Auto-configure MCP for AI Agents (Project-Level Only)
# =============================================================================
echo -e "${YELLOW}Configuring MCP for AI Agents (project-level)...${NC}"
echo ""

if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}[SKIP]${NC} jq not found - skipping JSON config auto-configuration"
    echo "       Install jq to enable auto-configuration: sudo apt install jq"
    echo ""
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# -----------------------------------------------------------------------------
# 定義通用 MCP Servers 配置
# -----------------------------------------------------------------------------

# Cursor / Roo Code MCP 格式（標準 JSON）
STANDARD_MCP_SERVERS=$(cat << EOF
{
  "mobile-mcp": {
    "command": "npx",
    "args": ["-y", "@mobilenext/mobile-mcp@latest"]
  },
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "${SCRIPT_DIR}"]
  },
  "fetch": {
    "command": "uvx",
    "args": ["mcp-server-fetch"]
  },
  "context7": {
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
EOF
)

# Claude Code MCP 格式（需要 type: "stdio"）
CLAUDE_MCP_SERVERS=$(cat << EOF
{
  "mobile-mcp": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@mobilenext/mobile-mcp@latest"]
  },
  "filesystem": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "${SCRIPT_DIR}"]
  },
  "fetch": {
    "type": "stdio",
    "command": "uvx",
    "args": ["mcp-server-fetch"]
  },
  "context7": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@upstash/context7-mcp"]
  }
}
EOF
)

# Codex TOML 格式（專案級）
CODEX_PROJECT_MCP_TOML=$(cat << EOF
# MobileAgent Project-Scoped Codex Configuration
# This config is loaded when Codex runs in this directory
# Ref: https://developers.openai.com/codex/mcp/

[mcp_servers.mobile-mcp]
command = "npx"
args = ["-y", "@mobilenext/mobile-mcp@latest"]

[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@modelcontextprotocol/server-filesystem", "${SCRIPT_DIR}"]

[mcp_servers.fetch]
command = "uvx"
args = ["mcp-server-fetch"]

[mcp_servers.context7]
command = "npx"
args = ["-y", "@upstash/context7-mcp"]
EOF
)

# 通用 JSON MCP 配置函數
configure_json_mcp() {
    local name="$1"
    local config_file="$2"
    local mcp_servers="$3"
    local config_dir=$(dirname "$config_file")

    if [ "$JQ_AVAILABLE" != "true" ]; then
        echo -e "${YELLOW}[SKIP]${NC} ${name} - jq not available"
        return 1
    fi

    echo -e "${BLUE}[${name}]${NC} Configuring ${config_file}..."
    mkdir -p "$config_dir"

    if [ -f "$config_file" ]; then
        cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        EXISTING=$(cat "$config_file")
        MERGED=$(echo "$EXISTING" | jq --argjson new "$mcp_servers" '.mcpServers = ((.mcpServers // {}) * $new)')
        echo "$MERGED" > "$config_file"
        echo -e "${GREEN}[OK]${NC} ${name} - merged MCP servers (backup created)"
    else
        echo "{\"mcpServers\": $mcp_servers}" | jq '.' > "$config_file"
        echo -e "${GREEN}[OK]${NC} ${name} - created new config"
    fi
}

# -----------------------------------------------------------------------------
# 1. Cursor: .cursor/mcp.json (專案級)
# Ref: https://cursor.com/docs/context/mcp
# -----------------------------------------------------------------------------
configure_json_mcp "Cursor" "${SCRIPT_DIR}/.cursor/mcp.json" "$STANDARD_MCP_SERVERS"

# -----------------------------------------------------------------------------
# 2. Claude Code: .mcp.json (專案級，project scope)
# Ref: https://code.claude.com/docs/en/mcp
# -----------------------------------------------------------------------------
configure_json_mcp "Claude Code" "${SCRIPT_DIR}/.mcp.json" "$CLAUDE_MCP_SERVERS"

# -----------------------------------------------------------------------------
# 3. Gemini CLI: .gemini/settings.json (專案級)
# Ref: https://google-gemini.github.io/gemini-cli/docs/get-started/configuration.html
# -----------------------------------------------------------------------------
configure_json_mcp "Gemini CLI" "${SCRIPT_DIR}/.gemini/settings.json" "$STANDARD_MCP_SERVERS"

# -----------------------------------------------------------------------------
# 4. OpenAI Codex: .codex/config.toml (專案級)
# Ref: https://developers.openai.com/codex/mcp/
# -----------------------------------------------------------------------------
CODEX_PROJECT_CONFIG="${SCRIPT_DIR}/.codex/config.toml"
CODEX_PROJECT_DIR="${SCRIPT_DIR}/.codex"

echo -e "${BLUE}[Codex]${NC} Configuring ${CODEX_PROJECT_CONFIG}..."
mkdir -p "$CODEX_PROJECT_DIR"

if [ -f "$CODEX_PROJECT_CONFIG" ]; then
    cp "$CODEX_PROJECT_CONFIG" "${CODEX_PROJECT_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
fi
# 始終重寫專案配置以確保路徑正確
echo "$CODEX_PROJECT_MCP_TOML" > "$CODEX_PROJECT_CONFIG"
echo -e "${GREEN}[OK]${NC} Codex - configured project MCP servers"

# -----------------------------------------------------------------------------
# 5. Roo Code: .roo/mcp.json (專案級)
# Ref: https://docs.roocode.com/features/mcp/using-mcp-in-roo
# -----------------------------------------------------------------------------
configure_json_mcp "Roo Code" "${SCRIPT_DIR}/.roo/mcp.json" "$STANDARD_MCP_SERVERS"

# -----------------------------------------------------------------------------
# 6. Windsurf: 不支援專案級配置
# Ref: https://docs.windsurf.com/plugins/cascade/mcp
# 注意：Windsurf 只支援全域配置 (~/.codeium/mcp_config.json)
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[INFO]${NC} Windsurf - no project-level MCP support (global only: ~/.codeium/mcp_config.json)"

echo ""

# =============================================================================
# Skills Validation and Deployment
# =============================================================================

# Extract field value from YAML frontmatter
extract_frontmatter_field() {
    local file="$1"
    local field="$2"
    local in_frontmatter=false
    local frontmatter=""
    
    while IFS= read -r line; do
        if [[ "$line" == "---" ]]; then
            if [ "$in_frontmatter" = true ]; then
                break
            else
                in_frontmatter=true
                continue
            fi
        fi
        if [ "$in_frontmatter" = true ]; then
            frontmatter+="$line"$'\n'
        fi
    done < "$file"
    
    echo "$frontmatter" | grep "^${field}:" | sed "s/^${field}:[[:space:]]*//" | head -1
}

# Validate a single skill
validate_skill() {
    local skill_dir="$1"
    local skill_name=$(basename "$skill_dir")
    local skill_file="${skill_dir}/SKILL.md"
    local has_error=false
    
    # Check if SKILL.md exists
    if [ ! -f "$skill_file" ]; then
        echo -e "       ${RED}[X]${NC} ${skill_name}: Missing SKILL.md"
        return 1
    fi
    
    # Check frontmatter
    local first_line=$(head -1 "$skill_file")
    if [ "$first_line" != "---" ]; then
        echo -e "       ${RED}[X]${NC} ${skill_name}: Missing YAML frontmatter"
        return 1
    fi
    
    # Validate name field
    local name=$(extract_frontmatter_field "$skill_file" "name")
    if [ -z "$name" ]; then
        echo -e "       ${RED}[X]${NC} ${skill_name}: Missing 'name' in frontmatter"
        return 1
    fi
    
    # Validate description field
    local description=$(extract_frontmatter_field "$skill_file" "description")
    if [ -z "$description" ]; then
        echo -e "       ${RED}[X]${NC} ${skill_name}: Missing 'description' in frontmatter"
        return 1
    fi
    
    return 0
}

# Validate all skills
validate_all_skills() {
    local skills_dir="$1"
    local total=0
    local passed=0
    
    for skill_dir in "$skills_dir"/*/; do
        if [ -d "$skill_dir" ]; then
            total=$((total + 1))
            if validate_skill "$skill_dir"; then
                passed=$((passed + 1))
            fi
        fi
    done
    
    if [ $total -eq 0 ]; then
        echo -e "${YELLOW}[WARN]${NC} No skills found"
        return 0
    fi
    
    if [ $passed -eq $total ]; then
        echo -e "${GREEN}[OK]${NC} All ${total} skill(s) validated"
        return 0
    else
        echo -e "${RED}[FAIL]${NC} ${passed}/${total} skills valid"
        return 1
    fi
}

# AI Agent detection functions
detect_cursor() {
    [ -d "$HOME/.cursor" ]
}

detect_claude() {
    command -v claude &> /dev/null || [ -d "$HOME/.claude" ]
}

detect_gemini() {
    command -v gemini &> /dev/null || [ -d "$HOME/.gemini" ]
}

detect_codex() {
    command -v codex &> /dev/null || [ -d "$HOME/.codex" ]
}

detect_windsurf() {
    [ -d "$HOME/.codeium" ] || [ -d "$HOME/.windsurf" ]
}

detect_roo() {
    [ -d "$HOME/.roo" ]
}

# 安全移除目標路徑（處理 symlink、檔案、目錄、broken symlink）
safe_remove_target() {
    local target="$1"
    
    # 若目標不存在，直接返回成功
    if [ ! -e "$target" ] && [ ! -L "$target" ]; then
        return 0
    fi
    
    # 若為 symlink（包含 broken symlink），使用 unlink
    if [ -L "$target" ]; then
        if ! unlink "$target" 2>/dev/null; then
            echo -e "       ${YELLOW}[WARN]${NC} Failed to unlink symlink: $target"
            # 嘗試 rm -f 作為備案
            rm -f "$target" 2>/dev/null || return 1
        fi
        return 0
    fi
    
    # 若為目錄，使用 rm -rf
    if [ -d "$target" ]; then
        if ! rm -rf "$target" 2>/dev/null; then
            echo -e "       ${YELLOW}[WARN]${NC} Failed to remove directory: $target"
            return 1
        fi
        return 0
    fi
    
    # 若為檔案，使用 rm -f
    if [ -f "$target" ]; then
        if ! rm -f "$target" 2>/dev/null; then
            echo -e "       ${YELLOW}[WARN]${NC} Failed to remove file: $target"
            return 1
        fi
        return 0
    fi
    
    return 0
}

# Deploy skills to target directory (symlinks preferred, copy fallback)
deploy_skills_to() {
    local agent_name="$1"
    local target_dir="$2"
    local force_copy="${MOBILE_AGENT_FORCE_COPY:-false}"

    # 確保目標目錄存在
    if ! mkdir -p "$target_dir" 2>/dev/null; then
        echo -e "${RED}[ERROR]${NC} ${agent_name}: Cannot create directory ${target_dir}"
        return 1
    fi

    local deployed=0
    local symlink_count=0
    local copy_count=0
    local failed=0

    for skill_dir in "$SKILLS_SOURCE"/*/; do
        if [ -d "$skill_dir" ] && [ -f "${skill_dir}SKILL.md" ]; then
            local skill_name=$(basename "$skill_dir")
            local dest="${target_dir}/${skill_name}"
            
            # 解析來源目錄的絕對路徑（處理來源本身是 symlink 的情況）
            local abs_skill_dir
            if [ -L "$skill_dir" ]; then
                # 來源是 symlink，取得實際路徑
                abs_skill_dir="$(readlink -f "$skill_dir")"
            else
                abs_skill_dir="$(cd "$skill_dir" && pwd)"
            fi

            # 安全移除舊的目標（處理各種情況）
            if ! safe_remove_target "$dest"; then
                echo -e "       ${RED}[X]${NC} ${skill_name}: Failed to remove old target"
                failed=$((failed + 1))
                continue
            fi

            if [ "$force_copy" = "true" ] || [ "$force_copy" = "1" ]; then
                # Force copy mode
                if cp -r "$abs_skill_dir" "$dest" 2>/dev/null; then
                    copy_count=$((copy_count + 1))
                else
                    echo -e "       ${RED}[X]${NC} ${skill_name}: Copy failed"
                    failed=$((failed + 1))
                    continue
                fi
            else
                # Try symlink first (preferred for development)
                if ln -s "$abs_skill_dir" "$dest" 2>/dev/null; then
                    symlink_count=$((symlink_count + 1))
                else
                    # Fallback to copy (Windows/CI/permission issues)
                    if cp -r "$abs_skill_dir" "$dest" 2>/dev/null; then
                        copy_count=$((copy_count + 1))
                    else
                        echo -e "       ${RED}[X]${NC} ${skill_name}: Both symlink and copy failed"
                        failed=$((failed + 1))
                        continue
                    fi
                fi
            fi
            deployed=$((deployed + 1))
        fi
    done

    # Report deployment method
    if [ $failed -gt 0 ]; then
        echo -e "${YELLOW}[WARN]${NC} ${agent_name}: ${deployed} skill(s) deployed, ${failed} failed -> ${target_dir}"
    elif [ $symlink_count -gt 0 ] && [ $copy_count -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} ${agent_name}: ${deployed} skill(s) via symlink -> ${target_dir}"
    elif [ $copy_count -gt 0 ] && [ $symlink_count -eq 0 ]; then
        echo -e "${GREEN}[OK]${NC} ${agent_name}: ${deployed} skill(s) via copy -> ${target_dir}"
    else
        echo -e "${GREEN}[OK]${NC} ${agent_name}: ${deployed} skill(s) (${symlink_count} symlink, ${copy_count} copy) -> ${target_dir}"
    fi
    return 0
}

echo -e "${YELLOW}Deploying skills to detected AI Agents...${NC}"
echo ""

# Check skills source directory
if [ ! -d "$SKILLS_SOURCE" ]; then
    echo -e "${YELLOW}[SKIP]${NC} Skills source directory not found: ${SKILLS_SOURCE}"
else
    # Validate skills
    echo -e "${BLUE}[INFO]${NC} Validating skills..."
    if ! validate_all_skills "$SKILLS_SOURCE"; then
        echo -e "${YELLOW}[WARN]${NC} Some skills have issues"
    fi
    echo ""
    
    # Detect and deploy
    echo -e "${BLUE}[INFO]${NC} Detecting AI Agents..."
    
    DEPLOYED=0
    
    if detect_cursor; then
        deploy_skills_to "Cursor" "${SCRIPT_DIR}/.cursor/skills"
        DEPLOYED=$((DEPLOYED + 1))
    fi
    
    if detect_claude; then
        deploy_skills_to "Claude Code" "${SCRIPT_DIR}/.claude/skills"
        DEPLOYED=$((DEPLOYED + 1))
    fi
    
    if detect_gemini; then
        deploy_skills_to "Gemini CLI" "${SCRIPT_DIR}/.gemini/skills"
        DEPLOYED=$((DEPLOYED + 1))
    fi
    
    if detect_codex; then
        deploy_skills_to "Codex CLI" "${SCRIPT_DIR}/.codex/skills"
        DEPLOYED=$((DEPLOYED + 1))
    fi
    
    if detect_windsurf; then
        deploy_skills_to "Windsurf" "${SCRIPT_DIR}/.windsurf/skills"
        DEPLOYED=$((DEPLOYED + 1))
    fi
    
    if detect_roo; then
        deploy_skills_to "Roo Code" "${SCRIPT_DIR}/.roo/skills"
        DEPLOYED=$((DEPLOYED + 1))
    fi
    
    if [ $DEPLOYED -eq 0 ]; then
        echo -e "${YELLOW}[INFO]${NC} No AI Agents detected"
    fi
fi

echo ""

# =============================================================================
# Create Required Directories
# =============================================================================
echo -e "${YELLOW}Creating directories...${NC}"
echo ""

mkdir -p "${SCRIPT_DIR}/outputs"
echo -e "${GREEN}[OK]${NC} outputs/"

mkdir -p "${SCRIPT_DIR}/temp/logs"
echo -e "${GREEN}[OK]${NC} temp/logs/"

echo ""

# =============================================================================
# Summary
# =============================================================================
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}   Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Project path:     ${GREEN}${SCRIPT_DIR}${NC}"
echo -e "Virtual env:      ${GREEN}${VENV_DIR}${NC}"
echo -e "MCP config:       ${GREEN}${MCP_CONFIG}${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1. Activate virtual environment:"
echo -e "   ${BLUE}source ${VENV_DIR}/bin/activate${NC}"
echo ""
echo "2. Copy MCP config to your AI Agent:"
echo -e "   ${BLUE}cat ${MCP_CONFIG}${NC}"
echo ""
echo "3. Connect your Android device:"
echo -e "   ${BLUE}adb devices${NC}"
echo ""
echo "4. (Recommended) Install DeviceKit for MCP Unicode input:"
echo -e "   ${BLUE}adb install ${SCRIPT_DIR}/apk_tools/mobilenext-devicekit.apk${NC}"
echo ""
echo "5. (Optional) Install ADBKeyboard for Python Unicode input:"
echo -e "   ${BLUE}adb install ${SCRIPT_DIR}/apk_tools/ADBKeyBoard.apk${NC}"
echo ""
echo -e "${GREEN}Happy automating!${NC}"
