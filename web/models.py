"""
MobileAgent Web UI - CLI Tools and Models Configuration

Edit this file to add/update CLI tools and their available models.
Each CLI tool has a name, command template, and list of models.

Model format:
    {"id": "model-id", "name": "Display Name", "default": True/False}

Command templates use placeholders:
    {model} - Model ID
    {prompt} - User prompt
"""

# =============================================================================
# Final Answer Instruction
# =============================================================================
# This instruction is appended to user prompts to ensure AI outputs
# a structured final answer that the Web UI can parse and display.

FINAL_ANSWER_INSTRUCTION = """

[SYSTEM INSTRUCTION - OUTPUT FORMAT]
When you complete the task, you MUST output your final result in this exact format:
<<FINAL_ANSWER>>
Your final answer or result here (be concise but complete)
<<END_FINAL_ANSWER>>

Rules:
1. LANGUAGE: Respond in the SAME language as the user's task. If user's task is in Chinese, reply in Chinese. If in English, reply in English.
2. If the task was completed successfully, describe the result.
3. If the task failed, output: TASK_FAILED: <reason>
4. If asking the user a question or needing clarification, output: AWAITING_INPUT: <your question>
5. Always include this block at the END of your response, after all actions are done.
[END SYSTEM INSTRUCTION]
"""


# =============================================================================
# CLI Tools Configuration
# =============================================================================

CLI_TOOLS = {
    "gemini": {
        "name": "Gemini CLI",
        "command": 'gemini -m {model} -p "{prompt}" --yolo',
        "models": [
            {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "default": True},
            {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro"},
            {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash-Lite"},
            {"id": "gemini-3-flash-preview", "name": "Gemini 3 Flash (Preview)"},
            {"id": "gemini-3-pro-preview", "name": "Gemini 3 Pro (Preview)"},
        ]
    },
    "claude": {
        "name": "Claude Code",
        "command": 'claude --model {model} -p "{prompt}" --dangerously-skip-permissions',
        "models": [
            {"id": "sonnet", "name": "Claude Sonnet 4.5", "default": True},
            {"id": "opus", "name": "Claude Opus 4.5"},
            {"id": "haiku", "name": "Claude Haiku 4.5"},
        ]
    },
    "codex": {
        "name": "OpenAI Codex",
        "command": 'codex -m {model} "{prompt}"',
        "models": [
            {"id": "gpt-5.1-codex", "name": "GPT-5.1 Codex", "default": True},
            {"id": "gpt-5.1-codex-max", "name": "GPT-5.1 Codex Max"},
            {"id": "gpt-5.2-codex", "name": "GPT-5.2 Codex"},
            {"id": "codex-mini-latest", "name": "Codex Mini"},
        ]
    },
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_cli_options():
    """
    Get CLI options formatted for API response.
    Returns dict with tool info and models list.
    """
    options = {}
    for tool_id, tool_config in CLI_TOOLS.items():
        options[tool_id] = {
            "name": tool_config["name"],
            "models": tool_config["models"]
        }
    return options


def get_default_model(cli_tool):
    """Get the default model for a CLI tool."""
    if cli_tool not in CLI_TOOLS:
        return None

    for model in CLI_TOOLS[cli_tool]["models"]:
        if model.get("default"):
            return model["id"]

    # Return first model if no default specified
    if CLI_TOOLS[cli_tool]["models"]:
        return CLI_TOOLS[cli_tool]["models"][0]["id"]

    return None


def build_command(cli_tool, model, prompt):
    """
    Build the command string for a CLI tool.
    Appends FINAL_ANSWER_INSTRUCTION to ensure structured output.
    Returns the formatted command string.
    """
    if cli_tool not in CLI_TOOLS:
        return f'{cli_tool} "{prompt}"'

    tool_config = CLI_TOOLS[cli_tool]
    command_template = tool_config["command"]

    # Use default model if not specified
    if not model:
        model = get_default_model(cli_tool)

    # Append final answer instruction to prompt
    enhanced_prompt = prompt + FINAL_ANSWER_INSTRUCTION

    # Escape quotes in prompt for shell safety
    enhanced_prompt = enhanced_prompt.replace('"', '\\"')

    return command_template.format(model=model, prompt=enhanced_prompt)


def validate_model(cli_tool, model):
    """Check if a model is valid for the given CLI tool."""
    if cli_tool not in CLI_TOOLS:
        return False

    model_ids = [m["id"] for m in CLI_TOOLS[cli_tool]["models"]]
    return model in model_ids
