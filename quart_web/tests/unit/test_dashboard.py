"""Unit tests for entities dashboard and contextual navigation (US4)."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_entities_requires_authentication(app):
    client = app.test_client()

    response = await client.get("/entities", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


@pytest.mark.asyncio
async def test_entities_redirects_to_dashboard_when_workflow_missing(app):
    client = app.test_client()

    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"

    response = await client.get("/entities", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


@pytest.mark.asyncio
async def test_entities_renders_navigation_for_active_workflow(app):
    client = app.test_client()

    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/entities")

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Entities Dashboard" in body
    assert "Active workflow: wf_alpha" in body


@pytest.mark.asyncio
async def test_entities_page_contains_required_nav_links(app):
    client = app.test_client()

    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get("/entities")

    assert response.status_code == 200
    body = (await response.get_data()).decode()

    assert 'href="/workflows"' in body
    assert 'href="/roles"' in body
    assert 'href="/guards"' in body
    assert 'href="/interactions"' in body
    assert 'href="/interaction-components"' in body
