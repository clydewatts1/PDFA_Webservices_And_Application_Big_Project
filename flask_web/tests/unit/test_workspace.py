from __future__ import annotations


def test_dashboard_requires_login(client) -> None:
    response = client.get("/dashboard", follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_dashboard_renders_workflows_for_authenticated_user(client, app) -> None:
    app.mcp_client.set_response(
        "workflow.list",
        {
            "status": "SUCCESS",
            "records": [{"WorkflowName": "wf_alpha", "WorkflowDescription": "Alpha workflow"}],
        },
    )

    with client.session_transaction() as session:
        session["user_id"] = "alice"

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"wf_alpha" in response.data


def test_dashboard_post_sets_active_workflow(client, app) -> None:
    app.mcp_client.set_response(
        "workflow.list",
        {
            "status": "SUCCESS",
            "records": [{"WorkflowName": "wf_alpha", "WorkflowDescription": "Alpha workflow"}],
        },
    )

    with client.session_transaction() as session:
        session["user_id"] = "alice"

    response = client.post("/dashboard", data={"workflow_name": "wf_alpha"}, follow_redirects=False)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/entities")
    with client.session_transaction() as session:
        assert session["active_workflow_name"] == "wf_alpha"