"""End-to-end happy path test: health → login → workflow select → role CRUD."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock

import pytest

from quart_web.src.app import create_app


@pytest.fixture()
def app():
    os.environ.setdefault("SESSION_SECRET", "test-session-secret")
    os.environ.setdefault("MCP_SERVER_URL", "http://127.0.0.1:5001/sse")
    application = create_app()
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False

    mock_mcp = AsyncMock()

    async def _call_tool(tool_name: str, arguments: dict | None = None):
        args = arguments or {}
        if tool_name == "get_system_health":
            return {"status": "success", "health_status": "CONNECTED"}
        if tool_name == "user_logon":
            return {"status": "SUCCESS", "username": "alice", "status_message": "Logon successful"}
        if tool_name == "workflow.list":
            return {
                "status": "success",
                "records": [{"WorkflowName": "wf_alpha", "WorkflowDescription": "Alpha workflow"}],
            }
        if tool_name == "role.list":
            return {
                "status": "success",
                "records": [{"RoleName": "editor", "WorkflowName": "wf_alpha", "RoleDescription": "Editor"}],
            }
        if tool_name == "role.create":
            return {"status": "success", **args}
        if tool_name == "role.get":
            return {
                "status": "success",
                "RoleName": args.get("RoleName", "editor"),
                "WorkflowName": args.get("WorkflowName", "wf_alpha"),
                "RoleDescription": "Editor",
            }
        if tool_name == "role.update":
            return {"status": "success", **args}
        if tool_name == "role.delete":
            return {"status": "success"}
        if tool_name == "user_logoff":
            return {"status": "success"}
        return {"status": "success"}

    mock_mcp.call_tool.side_effect = _call_tool
    application.mcp_client = mock_mcp
    return application


@pytest.mark.asyncio
async def test_role_crud_happy_path_end_to_end(app):
    client = app.test_client()

    health_response = await client.get("/")
    assert health_response.status_code == 200

    login_response = await client.post(
        "/login",
        form={"username": "alice", "password": "correct-password"},
        follow_redirects=False,
    )
    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/dashboard")

    dashboard_response = await client.post(
        "/dashboard",
        form={"workflow_name": "wf_alpha"},
        follow_redirects=False,
    )
    assert dashboard_response.status_code == 302
    assert dashboard_response.headers["Location"].endswith("/entities")

    role_create_response = await client.post(
        "/roles/new",
        form={"RoleName": "editor", "RoleDescription": "Editor role"},
        follow_redirects=False,
    )
    assert role_create_response.status_code == 302
    assert role_create_response.headers["Location"].endswith("/roles")

    role_edit_response = await client.post(
        "/roles/editor/edit",
        form={"RoleName": "editor", "RoleDescription": "Updated role"},
        follow_redirects=False,
    )
    assert role_edit_response.status_code == 302
    assert role_edit_response.headers["Location"].endswith("/roles")

    role_delete_response = await client.post("/roles/editor/delete", follow_redirects=False)
    assert role_delete_response.status_code == 302
    assert role_delete_response.headers["Location"].endswith("/roles")

    call_names = [call.args[0] for call in app.mcp_client.call_tool.await_args_list]
    assert "get_system_health" in call_names
    assert "user_logon" in call_names
    assert "workflow.list" in call_names
    assert "role.create" in call_names
    assert "role.update" in call_names
    assert "role.delete" in call_names
