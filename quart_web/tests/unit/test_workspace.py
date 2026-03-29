"""Unit tests for workspace selection routes (US3)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
async def test_get_dashboard_requires_authentication(app):
    client = app.test_client()

    response = await client.get("/dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


@pytest.mark.asyncio
async def test_post_dashboard_requires_authentication(app):
    client = app.test_client()

    response = await client.post("/dashboard", form={"workflow_name": "wf_alpha"}, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


@pytest.mark.asyncio
async def test_get_dashboard_renders_workflow_choices(app):
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

    response = await client.get("/dashboard")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Select Workflow" in body
    assert "wf_alpha" in body
    assert "wf_beta" in body
    mock_mcp.call_tool.assert_awaited_once_with("workflow.list", {})


@pytest.mark.asyncio
async def test_post_dashboard_sets_active_workflow_and_redirects(app):
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

    response = await client.post(
        "/dashboard",
        form={"workflow_name": "wf_beta"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/entities")

    async with client.session_transaction() as sess:
        assert sess.get("active_workflow_name") == "wf_beta"


@pytest.mark.asyncio
async def test_get_dashboard_shows_empty_state_when_no_workflows(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "success",
        "records": [],
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"

    response = await client.get("/dashboard")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "No workflows found" in body
    assert "Create Workflow" in body
