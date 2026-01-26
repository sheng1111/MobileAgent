#!/usr/bin/env python3
"""
Unit tests for MobileAgent Web UI API.
Run: python -m pytest tests/test_web_api.py -v
"""

import os
import sys
import json
import time

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "web"))

import pytest
from web.app import app, tasks, tasks_lock, parse_adb_devices, create_task


@pytest.fixture
def client():
    """Create test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Clear tasks before each test
        with tasks_lock:
            tasks.clear()
        yield client


class TestHealthEndpoint:
    """Tests for /api/health endpoint."""

    def test_health_returns_success(self, client):
        """Health endpoint should return success."""
        response = client.get("/api/health")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestDevicesEndpoint:
    """Tests for /api/devices endpoint."""

    def test_devices_returns_list(self, client):
        """Devices endpoint should return a list."""
        response = client.get("/api/devices")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert isinstance(data["devices"], list)

    def test_parse_adb_devices_function(self):
        """Test parse_adb_devices function."""
        # This test depends on ADB being available
        devices = parse_adb_devices()
        assert isinstance(devices, list)

        # Each device should have required fields
        for device in devices:
            assert "serial" in device
            assert "status" in device
            assert "model" in device


class TestTasksEndpoint:
    """Tests for /api/tasks endpoints."""

    def test_get_tasks_empty(self, client):
        """Should return empty list initially."""
        response = client.get("/api/tasks")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert data["tasks"] == []

    def test_create_task_missing_data(self, client):
        """Should fail when required data is missing."""
        # Missing both device_serial and prompt
        response = client.post(
            "/api/tasks",
            data=json.dumps({}),
            content_type="application/json"
        )
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data["success"] is False

    def test_create_task_missing_serial(self, client):
        """Should fail when device_serial is missing."""
        response = client.post(
            "/api/tasks",
            data=json.dumps({"prompt": "test prompt"}),
            content_type="application/json"
        )
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data["success"] is False
        assert "device_serial" in data["error"]

    def test_create_task_missing_prompt(self, client):
        """Should fail when prompt is missing."""
        response = client.post(
            "/api/tasks",
            data=json.dumps({"device_serial": "TEST123"}),
            content_type="application/json"
        )
        data = json.loads(response.data)

        assert response.status_code == 400
        assert data["success"] is False
        assert "prompt" in data["error"]

    def test_create_task_success(self, client):
        """Should successfully create a task."""
        response = client.post(
            "/api/tasks",
            data=json.dumps({
                "device_serial": "TEST123",
                "prompt": "echo hello",
                "cli_tool": "echo"
            }),
            content_type="application/json"
        )
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["success"] is True
        assert "task_id" in data

    def test_get_task_not_found(self, client):
        """Should return 404 for non-existent task."""
        response = client.get("/api/tasks/nonexistent")
        data = json.loads(response.data)

        assert response.status_code == 404
        assert data["success"] is False

    def test_create_and_get_task(self, client):
        """Should be able to create and retrieve a task."""
        # Create task
        create_response = client.post(
            "/api/tasks",
            data=json.dumps({
                "device_serial": "TEST456",
                "prompt": "echo test",
                "cli_tool": "echo"
            }),
            content_type="application/json"
        )
        create_data = json.loads(create_response.data)
        task_id = create_data["task_id"]

        # Wait for task to execute
        time.sleep(0.5)

        # Get task
        get_response = client.get(f"/api/tasks/{task_id}")
        get_data = json.loads(get_response.data)

        assert get_response.status_code == 200
        assert get_data["success"] is True
        assert get_data["task"]["id"] == task_id
        assert get_data["task"]["device_serial"] == "TEST456"
        assert get_data["task"]["prompt"] == "echo test"

    def test_get_task_output(self, client):
        """Should be able to get task output."""
        # Create task
        create_response = client.post(
            "/api/tasks",
            data=json.dumps({
                "device_serial": "TEST789",
                "prompt": "output test",
                "cli_tool": "echo"
            }),
            content_type="application/json"
        )
        create_data = json.loads(create_response.data)
        task_id = create_data["task_id"]

        # Wait for task to execute
        time.sleep(0.5)

        # Get output
        output_response = client.get(f"/api/tasks/{task_id}/output")
        output_data = json.loads(output_response.data)

        assert output_response.status_code == 200
        assert output_data["success"] is True
        assert "status" in output_data
        assert "output" in output_data

    def test_cancel_task(self, client):
        """Should be able to cancel a pending/running task."""
        # Create a long-running task
        create_response = client.post(
            "/api/tasks",
            data=json.dumps({
                "device_serial": "TESTCANCEL",
                "prompt": "10",
                "cli_tool": "sleep"
            }),
            content_type="application/json"
        )
        create_data = json.loads(create_response.data)
        task_id = create_data["task_id"]

        # Cancel task
        delete_response = client.delete(f"/api/tasks/{task_id}")
        delete_data = json.loads(delete_response.data)

        assert delete_response.status_code == 200
        assert delete_data["success"] is True

        # Verify task is cancelled
        get_response = client.get(f"/api/tasks/{task_id}")
        get_data = json.loads(get_response.data)

        assert get_data["task"]["status"] == "cancelled"


class TestMainPage:
    """Tests for main page rendering."""

    def test_index_page_renders(self, client):
        """Index page should render successfully."""
        response = client.get("/")

        assert response.status_code == 200
        assert b"MobileAgent" in response.data
        assert b"Device Control Panel" in response.data

    def test_static_css_served(self, client):
        """Static CSS file should be served."""
        response = client.get("/static/css/style.css")

        assert response.status_code == 200
        assert b"MobileAgent" in response.data

    def test_static_js_served(self, client):
        """Static JS file should be served."""
        response = client.get("/static/js/main.js")

        assert response.status_code == 200
        assert b"refreshDevices" in response.data


class TestTaskDuplication:
    """Tests for preventing duplicate tasks on same device."""

    def test_prevent_duplicate_task(self, client):
        """Should prevent creating duplicate tasks for same device."""
        # Create first task (long running)
        first_response = client.post(
            "/api/tasks",
            data=json.dumps({
                "device_serial": "TESTDUP",
                "prompt": "10",
                "cli_tool": "sleep"
            }),
            content_type="application/json"
        )
        assert first_response.status_code == 200

        # Try to create second task on same device
        second_response = client.post(
            "/api/tasks",
            data=json.dumps({
                "device_serial": "TESTDUP",
                "prompt": "another task",
                "cli_tool": "echo"
            }),
            content_type="application/json"
        )
        second_data = json.loads(second_response.data)

        assert second_response.status_code == 409
        assert second_data["success"] is False
        assert "already has a running task" in second_data["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
