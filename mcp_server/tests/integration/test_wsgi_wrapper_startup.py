from __future__ import annotations

from mcp_server.src.wsgi_app import create_app


def test_wrapper_health_endpoint_reports_ready() -> None:
    app = create_app(handler_map={"get_system_health": lambda _params: {"status": "SUCCESS"}})
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["rpc_path"] == "/rpc"
    assert payload["registered_method_count"] == 1