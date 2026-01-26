#!/bin/bash
# MobileAgent Setup Script
# 設定 Python 虛擬環境、MCP 設定、並部署 Skills 到偵測到的 AI Agents

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 取得腳本所在目錄（專案根目錄）
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
# 檢查相依套件
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
# Python 虛擬環境
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

# 啟動虛擬環境
echo -e "${BLUE}[INFO]${NC} Activating virtual environment..."
source "${VENV_DIR}/bin/activate"
echo -e "${GREEN}[OK]${NC} Virtual environment activated"

# 升級 pip
echo -e "${BLUE}[INFO]${NC} Upgrading pip..."
"${VENV_DIR}/bin/pip" install --upgrade pip -q

# 安裝相依套件
if [ -f "$REQUIREMENTS" ]; then
    echo -e "${BLUE}[INFO]${NC} Installing requirements..."
    "${VENV_DIR}/bin/pip" install -r "$REQUIREMENTS" -q
    echo -e "${GREEN}[OK]${NC} Requirements installed"
else
    echo -e "${YELLOW}[SKIP]${NC} No requirements.txt found"
fi

echo ""

# =============================================================================
# MCP 設定
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
# 自動設定 AI CLI 工具的 MCP
# =============================================================================
echo -e "${YELLOW}Configuring MCP for AI CLI tools...${NC}"
echo ""

if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}[SKIP]${NC} jq not found - skipping auto-configuration"
    echo "       Install jq to enable auto-configuration: sudo apt install jq"
    echo ""
else
    # Gemini CLI MCP 格式
    GEMINI_MCP_SERVERS=$(cat << EOF
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

    # -------------------------------------------------------------------------
    # Gemini CLI: .gemini/settings.json
    # -------------------------------------------------------------------------
    GEMINI_CONFIG="${SCRIPT_DIR}/.gemini/settings.json"
    GEMINI_DIR="${SCRIPT_DIR}/.gemini"

    echo -e "${BLUE}[Gemini CLI]${NC} Configuring ${GEMINI_CONFIG}..."
    mkdir -p "$GEMINI_DIR"

    if [ -f "$GEMINI_CONFIG" ]; then
        cp "$GEMINI_CONFIG" "${GEMINI_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
        EXISTING=$(cat "$GEMINI_CONFIG")
        MERGED=$(echo "$EXISTING" | jq --argjson new "$GEMINI_MCP_SERVERS" '.mcpServers = ((.mcpServers // {}) * $new)')
        echo "$MERGED" > "$GEMINI_CONFIG"
        echo -e "${GREEN}[OK]${NC} Gemini CLI - merged MCP servers (backup created)"
    else
        echo "{\"mcpServers\": $GEMINI_MCP_SERVERS}" | jq '.' > "$GEMINI_CONFIG"
        echo -e "${GREEN}[OK]${NC} Gemini CLI - created new config"
    fi

    # -------------------------------------------------------------------------
    # Claude Code: .mcp.json
    # -------------------------------------------------------------------------
    CLAUDE_CONFIG="${SCRIPT_DIR}/.mcp.json"

    echo -e "${BLUE}[Claude Code]${NC} Configuring ${CLAUDE_CONFIG}..."

    if [ -f "$CLAUDE_CONFIG" ]; then
        cp "$CLAUDE_CONFIG" "${CLAUDE_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
        EXISTING=$(cat "$CLAUDE_CONFIG")
        MERGED=$(echo "$EXISTING" | jq --argjson new "$CLAUDE_MCP_SERVERS" '.mcpServers = ((.mcpServers // {}) * $new)')
        echo "$MERGED" > "$CLAUDE_CONFIG"
        echo -e "${GREEN}[OK]${NC} Claude Code - merged MCP servers (backup created)"
    else
        echo "{\"mcpServers\": $CLAUDE_MCP_SERVERS}" | jq '.' > "$CLAUDE_CONFIG"
        echo -e "${GREEN}[OK]${NC} Claude Code - created new config"
    fi

    # -------------------------------------------------------------------------
    # Codex: ~/.codex/config.toml
    # -------------------------------------------------------------------------
    CODEX_CONFIG="$HOME/.codex/config.toml"
    CODEX_DIR="$HOME/.codex"

    echo -e "${BLUE}[Codex]${NC} Configuring ${CODEX_CONFIG}..."
    mkdir -p "$CODEX_DIR"

    CODEX_MCP_TOML=$(cat << EOF

# MobileAgent MCP Servers (auto-generated by set.sh)
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

    if [ -f "$CODEX_CONFIG" ]; then
        cp "$CODEX_CONFIG" "${CODEX_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)"
        if grep -q "mcp_servers.mobile-mcp" "$CODEX_CONFIG" 2>/dev/null; then
            echo -e "${YELLOW}[SKIP]${NC} Codex - MobileAgent servers already configured"
        else
            echo "$CODEX_MCP_TOML" >> "$CODEX_CONFIG"
            echo -e "${GREEN}[OK]${NC} Codex - appended MCP servers (backup created)"
        fi
    else
        echo "# Codex Configuration" > "$CODEX_CONFIG"
        echo "$CODEX_MCP_TOML" >> "$CODEX_CONFIG"
        echo -e "${GREEN}[OK]${NC} Codex - created new config"
    fi

    echo ""
fi

# =============================================================================
# Skills 驗證與部署
# =============================================================================

# 從 YAML frontmatter 提取欄位值
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

# 驗證單一 skill
validate_skill() {
    local skill_dir="$1"
    local skill_name=$(basename "$skill_dir")
    local skill_file="${skill_dir}/SKILL.md"
    local has_error=false
    
    # 檢查 SKILL.md 是否存在
    if [ ! -f "$skill_file" ]; then
        echo -e "       ${RED}[X]${NC} ${skill_name}: Missing SKILL.md"
        return 1
    fi
    
    # 檢查 frontmatter
    local first_line=$(head -1 "$skill_file")
    if [ "$first_line" != "---" ]; then
        echo -e "       ${RED}[X]${NC} ${skill_name}: Missing YAML frontmatter"
        return 1
    fi
    
    # 驗證 name 欄位
    local name=$(extract_frontmatter_field "$skill_file" "name")
    if [ -z "$name" ]; then
        echo -e "       ${RED}[X]${NC} ${skill_name}: Missing 'name' in frontmatter"
        return 1
    fi
    
    # 驗證 description 欄位
    local description=$(extract_frontmatter_field "$skill_file" "description")
    if [ -z "$description" ]; then
        echo -e "       ${RED}[X]${NC} ${skill_name}: Missing 'description' in frontmatter"
        return 1
    fi
    
    return 0
}

# 驗證所有 skills
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

# AI Agent 偵測函數
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

# 部署 skills 到指定目錄
deploy_skills_to() {
    local agent_name="$1"
    local target_dir="$2"
    
    mkdir -p "$target_dir"
    
    local deployed=0
    for skill_dir in "$SKILLS_SOURCE"/*/; do
        if [ -d "$skill_dir" ]; then
            local skill_name=$(basename "$skill_dir")
            local dest="${target_dir}/${skill_name}"
            
            if [ -f "${skill_dir}SKILL.md" ]; then
                rm -rf "$dest"
                cp -r "$skill_dir" "$dest"
                deployed=$((deployed + 1))
            fi
        fi
    done
    
    echo -e "${GREEN}[OK]${NC} ${agent_name}: ${deployed} skill(s) -> ${target_dir}"
    return 0
}

echo -e "${YELLOW}Deploying skills to detected AI Agents...${NC}"
echo ""

# 檢查 skills 來源目錄
if [ ! -d "$SKILLS_SOURCE" ]; then
    echo -e "${YELLOW}[SKIP]${NC} Skills source directory not found: ${SKILLS_SOURCE}"
else
    # 驗證 skills
    echo -e "${BLUE}[INFO]${NC} Validating skills..."
    if ! validate_all_skills "$SKILLS_SOURCE"; then
        echo -e "${YELLOW}[WARN]${NC} Some skills have issues"
    fi
    echo ""
    
    # 偵測並部署
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
# 建立必要目錄
# =============================================================================
echo -e "${YELLOW}Creating directories...${NC}"
echo ""

mkdir -p "${SCRIPT_DIR}/outputs"
echo -e "${GREEN}[OK]${NC} outputs/"

mkdir -p "${SCRIPT_DIR}/temp/logs"
echo -e "${GREEN}[OK]${NC} temp/logs/"

echo ""

# =============================================================================
# 總結
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
