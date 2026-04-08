from __future__ import annotations


def test_guard_list_renders_records(client, app) -> None:
    app.mcp_client.set_response(
        "guard.list",
        {"status": "SUCCESS", "records": [{"GuardName": "g1", "WorkflowName": "wf_alpha"}]},
    )

    with client.session_transaction() as session:
        session["user_id"] = "alice"
        session["active_workflow_name"] = "wf_alpha"

    response = client.get("/guards")

    assert response.status_code == 200
    assert b"g1" in response.data