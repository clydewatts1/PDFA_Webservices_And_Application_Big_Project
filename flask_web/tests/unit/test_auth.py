from __future__ import annotations


def test_login_success_redirects_to_dashboard(client, app) -> None:
    app.mcp_client.set_response(
        "user_logon",
        {"status": "SUCCESS", "username": "alice", "status_message": "Logon successful"},
    )

    response = client.post(
        "/login",
        data={"username": "alice", "password": "correct-password"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    assert app.mcp_client.calls[0][0] == "user_logon"


def test_login_denied_renders_message(client, app) -> None:
    app.mcp_client.set_response(
        "user_logon",
        {"status": "DENIED", "status_message": "Login denied"},
    )

    response = client.post(
        "/login",
        data={"username": "alice", "password": "wrong-password"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Login denied" in response.data