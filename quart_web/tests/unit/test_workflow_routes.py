"""Unit tests for workflow list routes (US5)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_workflow_list_requires_authentication(app):
    client = app.test_client()

    response = await client.get("/workflows", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


@pytest.mark.asyncio
async def test_workflow_list_accessible_without_active_workflow(app):
    """Authenticated users can access /workflows without an active workflow selected."""
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"status": "success", "records": []}
    app.mcp_client = mock_mcp

    client = app.test_client()

    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        # no active_workflow_name set

    response = await client.get("/workflows", follow_redirects=False)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_workflow_create_get_accessible_without_active_workflow(app):
    """Dashboard 'Create Workflow' link must work even when no workflow exists yet."""
    client = app.test_client()

    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        # no active_workflow_name — first-run scenario from dashboard

    response = await client.get("/workflows/new", follow_redirects=False)

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Create Workflow" in body


@pytest.mark.asyncio
async def test_workflow_list_renders_rows_and_actions(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "records": [
            {"WorkflowName": "wf_alpha", "WorkflowDescription": "Alpha workflow"},
            {"WorkflowName": "wf_beta", "WorkflowDescription": "Beta workflow"},
        ],
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/workflows")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Workflows" in body
    assert "wf_alpha" in body
    assert 'href="/workflows/wf_alpha/edit"' in body
    assert 'href="/workflows/wf_alpha/delete"' in body
    mock_mcp.call_tool.assert_awaited_once_with("workflow.list", {})


@pytest.mark.asyncio
async def test_workflow_list_shows_empty_state(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"status": "success", "records": []}
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/workflows")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "No records found" in body


@pytest.mark.asyncio
async def test_workflow_create_get_renders_form(app):
    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/workflows/new")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Create Workflow" in body
    assert "WorkflowName" in body


@pytest.mark.asyncio
async def test_workflow_create_post_success_redirects(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"status": "success"}
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post(
        "/workflows/new",
        form={"WorkflowName": "wf_new", "WorkflowDescription": "New workflow"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/workflows")
    mock_mcp.call_tool.assert_awaited_once_with(
        "workflow.create",
        {
            "WorkflowName": "wf_new",
            "WorkflowDescription": "New workflow",
            "WorkflowContextDescription": "",
            "WorkflowStateInd": "",
            "actor": "alice",
        },
    )


@pytest.mark.asyncio
async def test_workflow_create_post_validation_error_rerenders(app):
    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post(
        "/workflows/new",
        form={"WorkflowName": "", "WorkflowDescription": "New workflow"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Please correct the highlighted errors" in body


@pytest.mark.asyncio
async def test_workflow_edit_get_prefills_form(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "WorkflowName": "wf_alpha",
        "WorkflowDescription": "Alpha workflow",
        "WorkflowContextDescription": "",
        "WorkflowStateInd": "active",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/workflows/wf_alpha/edit")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Edit Workflow" in body
    assert "wf_alpha" in body
    mock_mcp.call_tool.assert_awaited_once_with("workflow.get", {"WorkflowName": "wf_alpha"})


@pytest.mark.asyncio
async def test_workflow_edit_post_mcp_error_rerenders_with_message(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "error",
        "message": "Workflow update failed",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post(
        "/workflows/wf_alpha/edit",
        form={"WorkflowName": "wf_alpha", "WorkflowDescription": "Updated"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Workflow update failed" in body
    assert "Updated" in body


@pytest.mark.asyncio
async def test_workflow_delete_get_confirmation_page(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "WorkflowName": "wf_alpha",
        "WorkflowDescription": "Alpha workflow",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/workflows/wf_alpha/delete")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Confirm Delete" in body
    assert "wf_alpha" in body
    mock_mcp.call_tool.assert_awaited_once_with("workflow.get", {"WorkflowName": "wf_alpha"})


@pytest.mark.asyncio
async def test_workflow_delete_post_success_redirects(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"status": "success"}
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post("/workflows/wf_alpha/delete", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/workflows")
    mock_mcp.call_tool.assert_awaited_once_with(
        "workflow.delete",
        {"WorkflowName": "wf_alpha", "actor": "alice"},
    )
