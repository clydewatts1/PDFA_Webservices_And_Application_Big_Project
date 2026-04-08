from __future__ import annotations

from flask_web.src.clients.mcp_client import MCPClientError


def test_landing_renders_healthy_state(client, app) -> None:
    app.mcp_client.set_response(
        "get_system_health",
        {"status": "SUCCESS", "health_status": "CONNECTED"},
    )

    response = client.get("/")

    assert response.status_code == 200
    assert b"MCP Healthy" in response.data
    assert app.mcp_client.calls[0][0] == "get_system_health"


def test_landing_renders_unhealthy_state_on_transport_error(client, app) -> None:
    app.mcp_client.set_response(
        "get_system_health",
        MCPClientError(code=502, message="wrapper unavailable", data={}, status_code=502),
    )

    response = client.get("/")

    assert response.status_code == 200
    assert b"MCP Unavailable" in response.data
    assert b"wrapper unavailable" in response.data