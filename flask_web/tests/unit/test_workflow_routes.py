from __future__ import annotations


def test_workflow_list_renders_records(client, app) -> None:
    app.mcp_client.set_response(
        "workflow.list",
        {
            "status": "SUCCESS",
            "records": [{"WorkflowName": "wf_alpha", "WorkflowDescription": "Alpha workflow"}],
        },
    )

    with client.session_transaction() as session:
        session["user_id"] = "alice"

    response = client.get("/workflows")

    assert response.status_code == 200
    assert b"Alpha workflow" in response.data