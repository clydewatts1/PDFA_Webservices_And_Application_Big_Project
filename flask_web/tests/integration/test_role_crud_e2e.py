from __future__ import annotations


def test_role_crud_happy_path_end_to_end(client, app) -> None:
    app.mcp_client.set_response(
        "get_system_health",
        {"status": "SUCCESS", "health_status": "CONNECTED"},
    )
    app.mcp_client.set_response(
        "user_logon",
        {"status": "SUCCESS", "username": "alice", "status_message": "Logon successful"},
    )
    app.mcp_client.set_response(
        "workflow.list",
        {
            "status": "SUCCESS",
            "records": [{"WorkflowName": "wf_alpha", "WorkflowDescription": "Alpha workflow"}],
        },
    )
    app.mcp_client.set_response("role.list", {"status": "SUCCESS", "records": []})
    app.mcp_client.set_response("role.create", {"status": "SUCCESS", "RoleName": "editor"})
    app.mcp_client.set_response(
        "role.get",
        {
            "status": "SUCCESS",
            "RoleName": "editor",
            "WorkflowName": "wf_alpha",
            "RoleDescription": "Editor",
        },
    )
    app.mcp_client.set_response("role.update", {"status": "SUCCESS", "RoleName": "editor"})
    app.mcp_client.set_response("role.delete", {"status": "SUCCESS"})

    health_response = client.get("/")
    assert health_response.status_code == 200

    login_response = client.post(
        "/login",
        data={"username": "alice", "password": "correct-password"},
        follow_redirects=False,
    )
    assert login_response.status_code == 302
    assert login_response.headers["Location"].endswith("/dashboard")

    dashboard_response = client.post(
        "/dashboard",
        data={"workflow_name": "wf_alpha"},
        follow_redirects=False,
    )
    assert dashboard_response.status_code == 302
    assert dashboard_response.headers["Location"].endswith("/entities")

    role_create_response = client.post(
        "/roles/new",
        data={"RoleName": "editor", "WorkflowName": "wf_alpha", "RoleDescription": "Editor role"},
        follow_redirects=False,
    )
    assert role_create_response.status_code == 302
    assert role_create_response.headers["Location"].endswith("/roles")

    role_edit_response = client.post(
        "/roles/editor/edit",
        data={"RoleName": "editor", "WorkflowName": "wf_alpha", "RoleDescription": "Updated role"},
        follow_redirects=False,
    )
    assert role_edit_response.status_code == 302
    assert role_edit_response.headers["Location"].endswith("/roles")

    role_delete_response = client.post("/roles/editor/delete", follow_redirects=False)
    assert role_delete_response.status_code == 302
    assert role_delete_response.headers["Location"].endswith("/roles")

    call_names = [method for method, _params in app.mcp_client.calls]
    assert "get_system_health" in call_names
    assert "user_logon" in call_names
    assert "workflow.list" in call_names
    assert "role.create" in call_names
    assert "role.update" in call_names
    assert "role.delete" in call_names