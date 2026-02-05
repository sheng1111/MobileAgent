#!/usr/bin/env python3
"""
MobileAgent Web UI - Flask Backend
Provides REST API for device management and task execution.
"""

import os
import re
import sys
import signal
import subprocess
import threading
import uuid
from datetime import datetime
from flask import Flask, render_template, jsonify, request

# Add web directory to path for imports
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WEB_DIR)

from config import PROJECT_ROOT, HOST, PORT, DEBUG, AUTO_REFRESH_INTERVAL
from models import get_cli_options, build_command, get_default_model
import database as db

app = Flask(__name__)

# In-memory storage for running processes (not persisted)
running_processes = {}
processes_lock = threading.Lock()


# =============================================================================
# Output Cleaning
# =============================================================================

# Patterns for cleaning verbose output
BASE64_PATTERN = re.compile(
    r'"data":\s*"[A-Za-z0-9+/=]{100,}"',
    re.MULTILINE
)
BASE64_IMAGE_PATTERN = re.compile(
    r'data:image/[a-z]+;base64,[A-Za-z0-9+/=]{100,}',
    re.MULTILINE
)
LONG_BASE64_PATTERN = re.compile(
    r'[A-Za-z0-9+/=]{500,}',
    re.MULTILINE
)

# Pattern to match MCP tool JSON responses (multiline JSON blocks)
MCP_JSON_RESPONSE_PATTERN = re.compile(
    r'(\w+\.\w+\([^)]+\) success in [\d.]+m?s:)\n\{[\s\S]*?\n\}',
    re.MULTILINE
)

# Pattern to match long element lists in JSON
ELEMENT_LIST_PATTERN = re.compile(
    r'"text":\s*"Found these elements on screen: \[.*?\]"',
    re.DOTALL
)


def compactMcpResponse(match):
    """Compact MCP tool response to a single line summary."""
    full_match = match.group(0)
    header = match.group(1)
    
    # Extract key info from JSON
    if '"text":' in full_match:
        # Find the text content
        text_match = re.search(r'"text":\s*"([^"]*)"', full_match)
        if text_match:
            text = text_match.group(1)
            # Truncate long text
            if len(text) > 200:
                text = text[:200] + '...'
            return f'{header} "{text}"'
    
    return header + ' [response truncated]'


def compactElementList(match):
    """Compact long element list to summary."""
    full_match = match.group(0)
    # Count elements
    element_count = full_match.count('type')
    return f'"text": "Found {element_count} elements on screen [details truncated]"'


def extractFinalAnswer(output):
    """
    Extract the AI's final answer from output.
    Only search in the AI response portion, not in the prompt instruction.
    Returns (found, content) tuple.
    """
    if not output:
        return False, ""
    
    start_tag = "<<FINAL_ANSWER>>"
    end_tag = "<<END_FINAL_ANSWER>>"
    
    # Find where AI response starts (after MCP ready or first thinking block)
    ai_start_markers = ['mcp startup: ready:', 'mcp: ready', '\nthinking\n']
    ai_start = 0
    for marker in ai_start_markers:
        idx = output.find(marker)
        if idx != -1:
            ai_start = max(ai_start, idx)
    
    # Search only in AI response portion
    ai_response = output[ai_start:]
    
    # Find the LAST FINAL_ANSWER in AI response (the real one, not template)
    start_idx = ai_response.rfind(start_tag)
    if start_idx == -1:
        return False, ""
    
    content_start = start_idx + len(start_tag)
    end_idx = ai_response.find(end_tag, content_start)
    if end_idx == -1:
        return False, ""
    
    content = ai_response[content_start:end_idx].strip()
    
    # Skip if it's the template text from prompt instruction
    if content == "Your final answer or result here (be concise but complete)":
        return False, ""
    
    return True, content


def determineTaskStatus(output, return_code):
    """
    Determine task status from AI's FINAL_ANSWER content.
    Only check for TASK_FAILED/AWAITING_INPUT in the actual AI response,
    not in the prompt instruction template.
    """
    found, content = extractFinalAnswer(output)
    
    if found:
        # Check content of FINAL_ANSWER for status indicators
        if content.startswith("TASK_FAILED"):
            return "failed", "Task reported failure in output"
        elif content.startswith("AWAITING_INPUT"):
            return "awaiting", None
        else:
            # Has valid FINAL_ANSWER, task completed
            return "completed", None
    
    # No valid FINAL_ANSWER found
    if return_code == 0:
        # Process succeeded but no clear answer - mark as completed with note
        return "completed", None
    else:
        return "failed", f"Exit code: {return_code}"


def cleanOutputForStorage(output):
    """
    Clean CLI output to improve readability and reduce storage.
    - Remove base64 screenshot data
    - Compact verbose MCP tool JSON responses
    - Truncate long element lists
    """
    if not output:
        return output
    
    # Remove base64 image data
    cleaned = BASE64_PATTERN.sub('"data": "[IMAGE_DATA_REMOVED]"', output)
    cleaned = BASE64_IMAGE_PATTERN.sub('[IMAGE_DATA_REMOVED]', cleaned)
    cleaned = LONG_BASE64_PATTERN.sub('[LONG_DATA_REMOVED]', cleaned)
    
    # Compact MCP JSON responses
    cleaned = MCP_JSON_RESPONSE_PATTERN.sub(compactMcpResponse, cleaned)
    
    # Compact long element lists
    cleaned = ELEMENT_LIST_PATTERN.sub(compactElementList, cleaned)
    
    return cleaned


# =============================================================================
# Device Management
# =============================================================================

def parse_adb_devices():
    """
    Execute 'adb devices -l' and parse the output.
    Returns list of device dicts with serial, status, model, etc.
    """
    try:
        result = subprocess.run(
            ["adb", "devices", "-l"],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return []

        devices = []
        lines = result.stdout.strip().split("\n")

        # Skip header line "List of devices attached"
        for line in lines[1:]:
            if not line.strip():
                continue

            parts = line.split()
            if len(parts) < 2:
                continue

            serial = parts[0]
            status = parts[1]

            # Extract model from "model:XXX" part
            model = "Unknown"
            for part in parts[2:]:
                if part.startswith("model:"):
                    model = part.replace("model:", "").replace("_", " ")
                    break

            devices.append({
                "serial": serial,
                "status": "online" if status == "device" else status,
                "model": model
            })

        return devices

    except subprocess.TimeoutExpired:
        return []
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error parsing adb devices: {e}")
        return []


# =============================================================================
# Task Management
# =============================================================================

def run_task(task_id, command, device_serial):
    """
    Execute a task in a subprocess.
    Updates task status and captures output.
    """
    # Update status to running
    db.update_task_status(
        task_id,
        status="running",
        started_at=datetime.now().isoformat()
    )

    try:
        # Execute command via shell with new session for process group management
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=PROJECT_ROOT,
            start_new_session=True
        )

        # Store process reference
        with processes_lock:
            running_processes[task_id] = process

        # Capture output
        output_lines = []
        for line in process.stdout:
            output_lines.append(line)
            # Clean output on every update for consistent display
            output_text = cleanOutputForStorage("".join(output_lines))
            db.update_task_output(task_id, output_text)

        process.wait()

        # Remove from running processes
        with processes_lock:
            running_processes.pop(task_id, None)

        # Update final status based on both return code and output content
        # Clean output for storage
        output_text = cleanOutputForStorage("".join(output_lines))

        # Determine task status from AI's FINAL_ANSWER, not from prompt instruction
        final_status, error_msg = determineTaskStatus(output_text, process.returncode)

        db.update_task_status(
            task_id,
            status=final_status,
            output=output_text,
            error=error_msg,
            finished_at=datetime.now().isoformat()
        )

    except Exception as e:
        with processes_lock:
            running_processes.pop(task_id, None)

        db.update_task_status(
            task_id,
            status="failed",
            error=str(e),
            finished_at=datetime.now().isoformat()
        )


def create_task(device_serial, prompt, cli_tool, model=None):
    """
    Create and start a new task.
    Returns task_id.
    """
    task_id = str(uuid.uuid4())[:8]

    # Use default model if not specified
    if not model:
        model = get_default_model(cli_tool)

    # Build command
    command = build_command(cli_tool, model, prompt)

    # Save to database
    db.create_task(task_id, device_serial, prompt, command, cli_tool, model)

    # Start task in background thread
    thread = threading.Thread(
        target=run_task,
        args=(task_id, command, device_serial),
        daemon=True
    )
    thread.start()

    return task_id


def cancel_task(task_id):
    """Cancel a running task."""
    task = db.get_task(task_id)

    if not task:
        return False, "Task not found"

    if task["status"] not in ["pending", "running"]:
        return False, "Task is not running"

    # Terminate process and all its child processes
    with processes_lock:
        process = running_processes.get(task_id)
        if process:
            try:
                # Get process group ID (equals PID since we use start_new_session=True)
                pgid = os.getpgid(process.pid)
                # Try SIGTERM first for graceful shutdown
                os.killpg(pgid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Timeout, force kill with SIGKILL
                    os.killpg(pgid, signal.SIGKILL)
                    process.wait(timeout=2)
            except ProcessLookupError:
                # Process already terminated
                pass
            except Exception as e:
                # Fallback: kill process directly
                try:
                    process.kill()
                    process.wait(timeout=2)
                except:
                    pass
            running_processes.pop(task_id, None)

    db.update_task_status(
        task_id,
        status="cancelled",
        finished_at=datetime.now().isoformat()
    )

    return True, "Task cancelled"


# =============================================================================
# API Routes
# =============================================================================

@app.route("/")
def index():
    """Serve main page."""
    return render_template("index.html")


@app.route("/api/config", methods=["GET"])
def api_get_config():
    """Get UI configuration."""
    return jsonify({
        "success": True,
        "config": {
            "autoRefreshInterval": AUTO_REFRESH_INTERVAL,
        }
    })


@app.route("/api/devices", methods=["GET"])
def api_get_devices():
    """Get list of connected devices with their current tasks."""
    devices = parse_adb_devices()

    # Add task info to each device
    for device in devices:
        task = db.get_device_running_task(device["serial"])
        if task:
            device["task"] = {
                "id": task["id"],
                "prompt": task["prompt"],
                "status": task["status"]
            }
        else:
            device["task"] = None

    return jsonify({
        "success": True,
        "devices": devices
    })


@app.route("/api/cli-options", methods=["GET"])
def api_cli_options():
    """Get available CLI tools and their models."""
    return jsonify({
        "success": True,
        "options": get_cli_options()
    })


@app.route("/api/tasks", methods=["GET"])
def api_get_tasks():
    """Get all tasks."""
    tasks = db.get_all_tasks()

    return jsonify({
        "success": True,
        "tasks": tasks
    })


@app.route("/api/tasks", methods=["POST"])
def api_create_task():
    """Create a new task."""
    data = request.json

    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    device_serial = data.get("device_serial")
    prompt = data.get("prompt")
    cli_tool = data.get("cli_tool", "gemini")
    model = data.get("model")

    if not device_serial:
        return jsonify({"success": False, "error": "device_serial is required"}), 400

    if not prompt:
        return jsonify({"success": False, "error": "prompt is required"}), 400

    # Check if device already has a running task
    existing_task = db.get_device_running_task(device_serial)
    if existing_task:
        return jsonify({
            "success": False,
            "error": f"Device already has a running task: {existing_task['id']}"
        }), 409

    task_id = create_task(device_serial, prompt, cli_tool, model)

    return jsonify({
        "success": True,
        "task_id": task_id
    })


@app.route("/api/tasks/<task_id>", methods=["GET"])
def api_get_task(task_id):
    """Get a specific task."""
    task = db.get_task(task_id)

    if not task:
        return jsonify({"success": False, "error": "Task not found"}), 404

    return jsonify({
        "success": True,
        "task": task
    })


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def api_cancel_task(task_id):
    """Cancel a task."""
    success, message = cancel_task(task_id)

    if not success:
        return jsonify({"success": False, "error": message}), 400

    return jsonify({"success": True, "message": message})


@app.route("/api/tasks/<task_id>/output", methods=["GET"])
def api_get_task_output(task_id):
    """Get task output (for streaming updates)."""
    task = db.get_task(task_id)

    if not task:
        return jsonify({"success": False, "error": "Task not found"}), 404

    # 計算執行時間
    duration = None
    if task.get("started_at"):
        started = datetime.fromisoformat(task["started_at"])
        if task.get("finished_at"):
            finished = datetime.fromisoformat(task["finished_at"])
            duration = (finished - started).total_seconds()
        else:
            # 任務還在執行中，計算到目前為止的時間
            duration = (datetime.now() - started).total_seconds()

    return jsonify({
        "success": True,
        "status": task["status"],
        "output": task["output"],
        "error": task["error"],
        "started_at": task.get("started_at"),
        "finished_at": task.get("finished_at"),
        "duration": duration
    })


@app.route("/api/tasks/clear", methods=["POST"])
def api_clear_tasks():
    """Clear all task history."""
    count = db.clear_all_tasks()
    return jsonify({
        "success": True,
        "count": count,
        "message": f"Cleared {count} tasks"
    })


@app.route("/api/health", methods=["GET"])
def api_health():
    """Health check endpoint."""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


# =============================================================================
# Main
# =============================================================================

if __name__ == "__main__":
    # Initialize database
    db.init_database()

    print("Starting MobileAgent Web UI...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Database: {db.DATABASE_PATH}")
    print(f"Auto-refresh interval: {AUTO_REFRESH_INTERVAL}s")
    print(f"Access the UI at: http://localhost:{PORT}")

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        threaded=True
    )
