from __future__ import annotations

import json

from mcp_server.src.api.errors import JsonRpcError
from mcp_server.src.wsgi_app import create_app


def test_wsgi_rpc_success_envelope() -> None:
    app = create_app(handler_map={"get_system_health": lambda _params: {"status": "SUCCESS"}})
    client = app.test_client()

    response = client.post(
        "/rpc",
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "get_system_health", "params": {}}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"status": "SUCCESS"},
    }


def test_wsgi_rpc_jsonrpc_error_stays_http_200() -> None:
    def raise_not_found(_params):
        raise JsonRpcError(code=-32601, message="Method not found", data={"method": "missing"})

    app = create_app(handler_map={"missing": raise_not_found})
    client = app.test_client()

    response = client.post(
        "/rpc",
        data=json.dumps({"jsonrpc": "2.0", "id": 2, "method": "missing", "params": {}}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.get_json()["error"]["code"] == -32601


def test_wsgi_rpc_invalid_json_returns_http_400() -> None:
    app = create_app(handler_map={})
    client = app.test_client()

    response = client.post(
        "/rpc",
        data="{not-valid-json",
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["data"]["reason"] == "invalid_json"


def test_wsgi_rpc_invalid_content_type_returns_http_400() -> None:
    app = create_app(handler_map={})
    client = app.test_client()

    response = client.post("/rpc", data="plain text", content_type="text/plain")

    assert response.status_code == 400
    assert response.get_json()["error"]["data"]["reason"] == "invalid_content_type"