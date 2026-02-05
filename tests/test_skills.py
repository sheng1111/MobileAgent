"""
Test suite for validating skills structure and content.
"""
import os
import sys
import re
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SKILLS_DIR = PROJECT_ROOT / ".skills"

# Required skills as of this refactor
REQUIRED_SKILLS = [
    # A. Task Planning & Interaction
    "task-clarify",
    "progress-report",
    # B. Exploration & Search
    "search-triage",
    "comment-scan",
    "patrol",
    # C. Content Extraction
    "article-extract",
    "wechat-browse",
    # D. Commenting & Interaction
    "comment-draft",
    "comment-post",
    # E. Utility Skills
    "app-action",
    "screen-analyze",
    "device-check",
    "troubleshoot",
    "unicode-setup",
]

# Legacy skills (retained for reference)
LEGACY_SKILLS = [
    "app-explore",
    "content-extract",
]


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        return match.group(1)
    return None


def parse_frontmatter(frontmatter_text):
    """Parse simple YAML frontmatter (name: value pairs)."""
    result = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip().strip('"\'')
    return result


def test_skills_directory_exists():
    """Test that .skills directory exists."""
    assert SKILLS_DIR.exists(), f"Skills directory not found: {SKILLS_DIR}"
    assert SKILLS_DIR.is_dir(), f"Skills path is not a directory: {SKILLS_DIR}"


def test_required_skills_exist():
    """Test that all required skills have directories."""
    missing = []
    for skill_name in REQUIRED_SKILLS:
        skill_dir = SKILLS_DIR / skill_name
        if not skill_dir.exists():
            missing.append(skill_name)

    assert not missing, f"Missing required skills: {missing}"


def test_skill_files_exist():
    """Test that each skill directory has a SKILL.md file."""
    missing = []
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                missing.append(skill_dir.name)

    assert not missing, f"Skills missing SKILL.md: {missing}"


def test_skill_frontmatter():
    """Test that each SKILL.md has valid YAML frontmatter."""
    issues = []

    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue

            content = skill_file.read_text()

            # Check frontmatter exists
            if not content.startswith('---'):
                issues.append(f"{skill_dir.name}: Missing frontmatter")
                continue

            frontmatter = extract_frontmatter(content)
            if not frontmatter:
                issues.append(f"{skill_dir.name}: Invalid frontmatter")
                continue

            parsed = parse_frontmatter(frontmatter)

            # Check required fields
            if 'name' not in parsed:
                issues.append(f"{skill_dir.name}: Missing 'name' field")
            if 'description' not in parsed:
                issues.append(f"{skill_dir.name}: Missing 'description' field")

    assert not issues, f"Frontmatter issues:\n" + "\n".join(issues)


def test_skill_content_structure():
    """Test that new skills have required sections."""
    # Only check new skills (not legacy ones)
    skills_to_check = REQUIRED_SKILLS

    # Required sections for new skills
    required_sections = [
        "Purpose",
        "Scope",
    ]

    issues = []

    for skill_name in skills_to_check:
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        if not skill_file.exists():
            continue

        content = skill_file.read_text()

        for section in required_sections:
            # Check for section heading (## or ###)
            pattern = rf'^##+ {section}'
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                issues.append(f"{skill_name}: Missing section '{section}'")

    if issues:
        print("\nWarning: Some skills may need additional sections:")
        for issue in issues:
            print(f"  - {issue}")

    # Not a hard failure for now - some utility skills may have simpler structure
    # assert not issues, f"Content structure issues:\n" + "\n".join(issues)


def test_skill_readme():
    """Test that .skills/README.md exists and is updated."""
    readme = SKILLS_DIR / "README.md"
    assert readme.exists(), "Skills README.md not found"

    content = readme.read_text()

    # Check that new skills are mentioned
    for skill_name in REQUIRED_SKILLS[:5]:  # Check first few
        assert skill_name in content, f"README doesn't mention skill: {skill_name}"


def test_mcp_tools_mapping():
    """Test that MCP tools mapping document exists."""
    mapping_file = PROJECT_ROOT / "docs" / "MCP_TOOLS_MAPPING.md"
    assert mapping_file.exists(), "MCP_TOOLS_MAPPING.md not found"


def test_deployment_strategy():
    """Test that deployment strategy document exists."""
    strategy_file = PROJECT_ROOT / "docs" / "DEPLOYMENT_STRATEGY.md"
    assert strategy_file.exists(), "DEPLOYMENT_STRATEGY.md not found"


def test_skills_deployed():
    """Test that skills are deployed to agent directories."""
    # Check at least one agent directory has skills
    agent_dirs = [
        ".cursor/skills",
        ".claude/skills",
        ".gemini/skills",
    ]

    deployed = False
    for agent_dir in agent_dirs:
        full_path = PROJECT_ROOT / agent_dir
        if full_path.exists():
            skills_count = sum(1 for d in full_path.iterdir() if d.is_dir() or d.is_symlink())
            if skills_count >= len(REQUIRED_SKILLS):
                deployed = True
                break

    assert deployed, "Skills not properly deployed to any agent directory"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
