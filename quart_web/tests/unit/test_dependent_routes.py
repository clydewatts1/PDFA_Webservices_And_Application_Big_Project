"""Unit tests for interaction/guard/component list routes (US5)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "tool_name", "record", "field_name", "edit_href", "delete_href"),
    [
        (
            "/interactions",
            "interaction.list",
            {"InteractionName": "approve", "WorkflowName": "wf_alpha"},
            "approve",
            '/interactions/approve/edit',
            '/interactions/approve/delete',
        ),
        (
            "/guards",
            "guard.list",
            {"GuardName": "is_admin", "WorkflowName": "wf_alpha"},
            "is_admin",
            '/guards/is_admin/edit',
            '/guards/is_admin/delete',
        ),
        (
            "/interaction-components",
            "interaction_component.list",
            {"InteractionComponentName": "notify_user", "WorkflowName": "wf_alpha"},
            "notify_user",
            '/interaction-components/notify_user/edit',
            '/interaction-components/notify_user/delete',
        ),
    ],
)
async def test_dependent_list_routes_scope_and_render(app, path, tool_name, record, field_name, edit_href, delete_href):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.return_value = {"status": "success", "records": [record]}
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.get(path)

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert field_name in body
    assert f'href="{edit_href}"' in body
    assert f'href="{delete_href}"' in body
    mock_mcp.call_tool.assert_awaited_once_with(tool_name, {"WorkflowName": "wf_alpha"})


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/interactions", "/guards", "/interaction-components"])
async def test_dependent_list_routes_require_context(app, path):
    client = app.test_client()

    response = await client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")

    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"

    response = await client.get(path, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "new_path",
        "edit_path",
        "create_tool",
        "update_tool",
        "get_tool",
        "name_field",
        "name_value",
        "description_field",
    ),
    [
        (
            "/interactions/new",
            "/interactions/approve/edit",
            "interaction.create",
            "interaction.update",
            "interaction.get",
            "InteractionName",
            "approve",
            "InteractionDescription",
        ),
        (
            "/guards/new",
            "/guards/is_admin/edit",
            "guard.create",
            "guard.update",
            "guard.get",
            "GuardName",
            "is_admin",
            "GuardDescription",
        ),
        (
            "/interaction-components/new",
            "/interaction-components/notify_user/edit",
            "interaction_component.create",
            "interaction_component.update",
            "interaction_component.get",
            "InteractionComponentName",
            "notify_user",
            "InteractionComponentDescription",
        ),
    ],
)
async def test_dependent_create_and_edit_routes(app, new_path, edit_path, create_tool, update_tool, get_tool, name_field, name_value, description_field):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.side_effect = [
        {"status": "success"},
        {
            "status": "success",
            name_field: name_value,
            "WorkflowName": "wf_alpha",
            description_field: "Loaded description",
        },
        {"status": "success"},
    ]
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    create_response = await client.post(
        new_path,
        form={name_field: name_value, description_field: "Created description"},
        follow_redirects=False,
    )
    assert create_response.status_code == 302

    edit_get_response = await client.get(edit_path)
    assert edit_get_response.status_code == 200
    edit_get_body = (await edit_get_response.get_data()).decode()
    assert "Edit" in edit_get_body
    assert name_value in edit_get_body

    edit_post_response = await client.post(
        edit_path,
        form={name_field: name_value, description_field: "Updated description"},
        follow_redirects=False,
    )
    assert edit_post_response.status_code == 302

    assert mock_mcp.call_tool.await_args_list[0].args[0] == create_tool
    assert mock_mcp.call_tool.await_args_list[1].args[0] == get_tool
    assert mock_mcp.call_tool.await_args_list[2].args[0] == update_tool


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("new_path", "name_field", "description_field"),
    [
        ("/interactions/new", "InteractionName", "InteractionDescription"),
        ("/guards/new", "GuardName", "GuardDescription"),
        ("/interaction-components/new", "InteractionComponentName", "InteractionComponentDescription"),
    ],
)
async def test_dependent_create_validation_error_rerenders(app, new_path, name_field, description_field):
    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    response = await client.post(
        new_path,
        form={name_field: "", description_field: "Invalid"},
        follow_redirects=False,
    )

    assert response.status_code == 200
    body = (await response.get_data()).decode()
    assert "Please correct the highlighted errors" in body


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "get_path",
        "post_path",
        "get_tool",
        "delete_tool",
        "payload",
        "redirect_suffix",
        "display_name",
    ),
    [
        (
            "/interactions/approve/delete",
            "/interactions/approve/delete",
            "interaction.get",
            "interaction.delete",
            {"InteractionName": "approve", "WorkflowName": "wf_alpha", "actor": "alice"},
            "/interactions",
            "approve",
        ),
        (
            "/guards/is_admin/delete",
            "/guards/is_admin/delete",
            "guard.get",
            "guard.delete",
            {"GuardName": "is_admin", "WorkflowName": "wf_alpha", "actor": "alice"},
            "/guards",
            "is_admin",
        ),
        (
            "/interaction-components/notify_user/delete",
            "/interaction-components/notify_user/delete",
            "interaction_component.get",
            "interaction_component.delete",
            {
                "InteractionComponentName": "notify_user",
                "WorkflowName": "wf_alpha",
                "actor": "alice",
            },
            "/interaction-components",
            "notify_user",
        ),
    ],
)
async def test_dependent_delete_confirmation_and_submit(
    app,
    get_path,
    post_path,
    get_tool,
    delete_tool,
    payload,
    redirect_suffix,
    display_name,
):
    mock_mcp = AsyncMock()
    mock_mcp.call_tool.side_effect = [
        {"status": "success", **{k: v for k, v in payload.items() if k != "actor"}},
        {"status": "success"},
    ]
    app.mcp_client = mock_mcp

    client = app.test_client()
    async with client.session_transaction() as sess:
        sess["user_id"] = "alice"
        sess["active_workflow_name"] = "wf_alpha"

    get_response = await client.get(get_path)
    assert get_response.status_code == 200
    get_body = (await get_response.get_data()).decode()
    assert "Confirm Delete" in get_body
    assert display_name in get_body

    post_response = await client.post(post_path, follow_redirects=False)
    assert post_response.status_code == 302
    assert post_response.headers["Location"].endswith(redirect_suffix)

    assert mock_mcp.call_tool.await_args_list[0].args[0] == get_tool
    assert mock_mcp.call_tool.await_args_list[1].args[0] == delete_tool
