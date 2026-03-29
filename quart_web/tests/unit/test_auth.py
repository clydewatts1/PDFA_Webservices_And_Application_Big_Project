"""Unit tests for auth routes (US2)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

@pytest.mark.asyncio
async def test_get_login_renders_form(app):
    client = app.test_client()

    response = await client.get("/login")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Login" in body
    assert 'name="username"' in body
    assert 'name="password"' in body


@pytest.mark.asyncio
async def test_post_login_success_sets_session_and_redirects(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "SUCCESS",
        "username": "alice",
        "status_message": "Logon successful",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    response = await client.post(
        "/login",
        form={"username": "alice", "password": "correct-password"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    mock_mcp.call_tool.assert_awaited_once_with(
        "user_logon",
        {"username": "alice", "password": "correct-password"},
    )

    async with client.session_transaction() as sess:
        assert sess.get("user_id") == "alice"


@pytest.mark.asyncio
async def test_post_login_denied_re_renders_with_error(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "DENIED",
        "status_message": "Invalid username or password",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    response = await client.post(
        "/login",
        form={"username": "alice", "password": "bad-password"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Invalid username or password" in body

    async with client.session_transaction() as sess:
        assert sess.get("user_id") is None


@pytest.mark.asyncio
async def test_post_login_missing_username_re_renders_without_crashing(app):
    mock_mcp = AsyncMock()
    app.mcp_client = mock_mcp

    client = app.test_client()
    response = await client.post(
        "/login",
        form={"username": "", "password": "anything"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Username is required" in body
    mock_mcp.call_tool.assert_not_awaited()


@pytest.mark.asyncio
async def test_post_logout_calls_mcp_and_clears_session(app):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {
        "status": "SUCCESS",
        "status_message": "Logoff successful",
    }
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_1"

    response = await client.post("/logout", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    mock_mcp.call_tool.assert_awaited_once_with("user_logoff", {"username": "alice"})

    async with client.session_transaction() as sess:
        assert sess.get("user_id") is None
        assert sess.get("active_workflow_name") is None


@pytest.mark.asyncio
async def test_csrf_enforced_for_post_login(app):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()

    response = await client.post(
        "/login",
        form={"username": "alice", "password": "correct-password"},
        follow_redirects=False,
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_csrf_enforced_for_post_logout(app):
    app.config["WTF_CSRF_ENABLED"] = True
    client = app.test_client()

    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"

    response = await client.post("/logout", follow_redirects=False)
    assert response.status_code == 400
