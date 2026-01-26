"""
MobileAgent Web UI - SQLite Database
Handles persistent storage for tasks history.
"""

import sqlite3
import threading
from datetime import datetime
from contextlib import contextmanager

from config import DATABASE_PATH, MAX_TASK_HISTORY, MAX_OUTPUT_LENGTH


# Thread-local storage for database connections
_local = threading.local()


def get_connection():
    """Get thread-local database connection."""
    if not hasattr(_local, "connection"):
        _local.connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        _local.connection.row_factory = sqlite3.Row
    return _local.connection


@contextmanager
def get_cursor():
    """Context manager for database cursor."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e


def init_database():
    """Initialize database tables."""
    with get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                device_serial TEXT NOT NULL,
                prompt TEXT NOT NULL,
                command TEXT NOT NULL,
                cli_tool TEXT NOT NULL,
                model TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                output TEXT DEFAULT '',
                error TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            )
        """)

        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_device_serial
            ON tasks(device_serial)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status
            ON tasks(status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_created_at
            ON tasks(created_at DESC)
        """)


def create_task(task_id, device_serial, prompt, command, cli_tool, model):
    """Insert a new task into database."""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO tasks (id, device_serial, prompt, command, cli_tool, model, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
        """, (task_id, device_serial, prompt, command, cli_tool, model, datetime.now().isoformat()))


def update_task_status(task_id, status, output=None, error=None, started_at=None, finished_at=None):
    """Update task status and related fields."""
    with get_cursor() as cursor:
        updates = ["status = ?"]
        params = [status]

        if output is not None:
            # Truncate output if too long
            if len(output) > MAX_OUTPUT_LENGTH:
                output = output[:MAX_OUTPUT_LENGTH] + "\n... (truncated)"
            updates.append("output = ?")
            params.append(output)

        if error is not None:
            updates.append("error = ?")
            params.append(error)

        if started_at is not None:
            updates.append("started_at = ?")
            params.append(started_at)

        if finished_at is not None:
            updates.append("finished_at = ?")
            params.append(finished_at)

        params.append(task_id)

        cursor.execute(f"""
            UPDATE tasks SET {', '.join(updates)} WHERE id = ?
        """, params)


def update_task_output(task_id, output):
    """Update task output (for streaming)."""
    with get_cursor() as cursor:
        # Truncate if needed
        if len(output) > MAX_OUTPUT_LENGTH:
            output = output[:MAX_OUTPUT_LENGTH] + "\n... (truncated)"

        cursor.execute("UPDATE tasks SET output = ? WHERE id = ?", (output, task_id))


def get_task(task_id):
    """Get a single task by ID."""
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_all_tasks(limit=None):
    """Get all tasks ordered by created_at desc."""
    limit = limit or MAX_TASK_HISTORY
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM tasks
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]


def get_device_running_task(device_serial):
    """Get running or pending task for a device."""
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM tasks
            WHERE device_serial = ? AND status IN ('pending', 'running')
            ORDER BY created_at DESC
            LIMIT 1
        """, (device_serial,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_tasks_by_status(status):
    """Get tasks by status."""
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM tasks
            WHERE status = ?
            ORDER BY created_at DESC
        """, (status,))
        return [dict(row) for row in cursor.fetchall()]


def delete_task(task_id):
    """Delete a task from database."""
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def cleanup_old_tasks():
    """Remove old tasks beyond MAX_TASK_HISTORY limit."""
    with get_cursor() as cursor:
        # Get IDs of tasks to keep
        cursor.execute("""
            SELECT id FROM tasks
            ORDER BY created_at DESC
            LIMIT ?
        """, (MAX_TASK_HISTORY,))
        keep_ids = [row['id'] for row in cursor.fetchall()]

        if keep_ids:
            placeholders = ','.join(['?' for _ in keep_ids])
            cursor.execute(f"""
                DELETE FROM tasks WHERE id NOT IN ({placeholders})
            """, keep_ids)
            return cursor.rowcount
        return 0


def clear_all_tasks():
    """Delete all tasks from database."""
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM tasks")
        return cursor.rowcount
