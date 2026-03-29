"""Unit tests for role list routes (US5)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_role_list_requires_authentication(app):
    client = app.test_client()

    response = await client.get("/roles", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


@pytest.mark.asyncio
async def test_role_list_requires_active_workflow_context(app):
    client = app.test_client()

    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"

    response = await client.get("/roles", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


@pytest.mark.asyncio
async def test_role_list_scopes_by_active_workflow_and_renders_table(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "records": [
            {"RoleName": "owner", "WorkflowName": "wf_alpha", "RoleDescription": "Owner role"}
        ],
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/roles")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Roles" in body
    assert "owner" in body
    assert 'href="/roles/owner/edit"' in body
    assert 'href="/roles/owner/delete"' in body
    mock_mcp.call_tool.assert_awaited_once_with("role.list", {"WorkflowName": "wf_alpha"})


@pytest.mark.asyncio
async def test_role_list_shows_empty_state(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"status": "success", "records": []}
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/roles")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "No records found" in body


@pytest.mark.asyncio
async def test_role_create_get_renders_form(app):
    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/roles/new")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Create Role" in body
    assert "RoleName" in body


@pytest.mark.asyncio
async def test_role_create_post_success_redirects(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"status": "success"}
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post(
        "/roles/new",
        form={"RoleName": "editor", "RoleDescription": "Editor role"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/roles")
    mock_mcp.call_tool.assert_awaited_once_with(
        "role.create",
        {
            "RoleName": "editor",
            "WorkflowName": "wf_alpha",
            "RoleDescription": "Editor role",
            "RoleContextDescription": "",
            "RoleConfiguration": "",
            "RoleConfigurationDescription": "",
            "RoleConfigurationContextDescription": "",
            "actor": "alice",
        },
    )


@pytest.mark.asyncio
async def test_role_create_post_validation_error_rerenders(app):
    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post(
        "/roles/new",
        form={"RoleName": "", "RoleDescription": "Editor role"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Please correct the highlighted errors" in body


@pytest.mark.asyncio
async def test_role_edit_get_prefills_form(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "RoleName": "editor",
        "WorkflowName": "wf_alpha",
        "RoleDescription": "Editor role",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/roles/editor/edit")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Edit Role" in body
    assert "editor" in body
    mock_mcp.call_tool.assert_awaited_once_with(
        "role.get", {"RoleName": "editor", "WorkflowName": "wf_alpha"}
    )


@pytest.mark.asyncio
async def test_role_edit_post_mcp_error_rerenders_with_message(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "error",
        "message": "Role update failed",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post(
        "/roles/editor/edit",
        form={"RoleName": "editor", "RoleDescription": "Updated role"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Role update failed" in body
    assert "Updated role" in body


@pytest.mark.asyncio
async def test_role_delete_get_confirmation_page(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "RoleName": "editor",
        "WorkflowName": "wf_alpha",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/roles/editor/delete")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Confirm Delete" in body
    assert "editor" in body
    mock_mcp.call_tool.assert_awaited_once_with(
        "role.get", {"RoleName": "editor", "WorkflowName": "wf_alpha"}
    )


@pytest.mark.asyncio
async def test_role_delete_post_success_redirects(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"status": "success"}
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post("/roles/editor/delete", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/roles")
    mock_mcp.call_tool.assert_awaited_once_with(
        "role.delete",
        {"RoleName": "editor", "WorkflowName": "wf_alpha", "actor": "alice"},
    )
