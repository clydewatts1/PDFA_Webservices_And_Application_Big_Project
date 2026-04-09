from __future__ import annotations


def test_role_list_requires_workflow_context(client) -> None:
    with client.session_transaction() as session:
        session["user_id"] = "alice"

    response = client.get("/roles", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_role_create_redirects_to_list_on_success(client, app) -> None:
    app.mcp_client.set_response("role.create", {"status": "SUCCESS", "RoleName": "editor"})

    with client.session_transaction() as session:
        session["user_id"] = "alice"
        session["active_workflow_name"] = "wf_alpha"

    response = client.post(
        "/roles/new",
        data={"RoleName": "editor", "WorkflowName": "wf_alpha", "RoleDescription": "Editor role"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/roles")
    assert app.mcp_client.calls[-1][0] == "role.create"