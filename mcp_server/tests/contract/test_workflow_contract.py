"""Contract tests for workflow.create and workflow.update JSON-RPC methods — T012.

These tests verify the JSON-RPC 2.0 protocol envelope and workflow-specific error codes
using the MCP Flask test client backed by an in-memory SQLite database.
"""
from __future__ import annotations

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.app import create_app
from mcp_server.src.models.base import Base
from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mcp_client(tmp_path):
    """Create an MCP Flask test client backed by SQLite."""
    db_url = f"sqlite:///{tmp_path}/contract_test.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    app = create_app()
    for method, handler in make_workflow_handlers(session_factory).items():
        app.register_jsonrpc_handler(method, handler)  # type: ignore[attr-defined]

    app.config["TESTING"] = True
    return app.test_client()


def _rpc(client, method: str, params: dict, request_id: int = 1):
    """Helper: POST a JSON-RPC request and return parsed response body."""
    resp = client.post(
        "/rpc",
        data=json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}),
        content_type="application/json",
    )
    return resp.get_json()


# ---------------------------------------------------------------------------
# Protocol envelope tests
# ---------------------------------------------------------------------------

class TestProtocolEnvelope:
    def test_wrong_jsonrpc_version_returns_standard_code(self, mcp_client) -> None:
        resp = mcp_client.post(
            "/rpc",
            data=json.dumps({"jsonrpc": "1.0", "id": 1, "method": "workflow.create", "params": {}}),
            content_type="application/json",
        )
        body = resp.get_json()
        assert body["error"]["code"] == -32600

    def test_unknown_method_returns_standard_code(self, mcp_client) -> None:
        body = _rpc(mcp_client, "nonexistent.method", {})
        assert body["error"]["code"] == -32601

    def test_success_response_has_jsonrpc_field(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "EnvelopeTest",
            "WorkflowDescription": "desc",
            "WorkflowContextDescription": "ctx",
            "actor": "test_user",
        })
        assert body.get("jsonrpc") == "2.0"
        assert body.get("id") == 1
        assert "result" in body

    def test_error_response_has_jsonrpc_field(self, mcp_client) -> None:
        body = _rpc(mcp_client, "nonexistent.method", {})
        assert body.get("jsonrpc") == "2.0"
        assert "error" in body


# ---------------------------------------------------------------------------
# workflow.create
# ---------------------------------------------------------------------------

class TestWorkflowCreate:
    def test_create_returns_workflow_name(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "OrderProcess",
            "WorkflowDescription": "Handles orders",
            "WorkflowContextDescription": "E-commerce",
            "actor": "alice",
        })
        assert "result" in body
        assert body["result"]["WorkflowName"] == "OrderProcess"

    def test_create_returns_control_columns(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "InvoiceProcess",
            "WorkflowDescription": "Invoice flow",
            "WorkflowContextDescription": "Finance",
            "actor": "bob",
        })
        result = body["result"]
        assert result["DeleteInd"] == 0
        assert result["InsertUserName"] == "bob"
        assert "EffFromDateTime" in result
        assert "EffToDateTime" in result

    def test_create_duplicate_active_key_returns_error(self, mcp_client) -> None:
        params = {
            "WorkflowName": "UniqueWF",
            "WorkflowDescription": "desc",
            "WorkflowContextDescription": "ctx",
            "actor": "alice",
        }
        _rpc(mcp_client, "workflow.create", params)  # first create succeeds
        body = _rpc(mcp_client, "workflow.create", params, request_id=2)  # duplicate
        assert "error" in body
        assert body["error"]["data"]["code"] == "duplicate_active_key"

    def test_create_missing_workflow_name_returns_error(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.create", {
            "WorkflowDescription": "desc",
            "actor": "alice",
        })
        assert "error" in body

    def test_create_missing_actor_returns_error(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "NoActorWF",
        })
        assert "error" in body


# ---------------------------------------------------------------------------
# workflow.update
# ---------------------------------------------------------------------------

class TestWorkflowUpdate:
    def test_update_existing_workflow_succeeds(self, mcp_client) -> None:
        _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "UpdateTarget",
            "WorkflowDescription": "orig",
            "WorkflowContextDescription": "ctx",
            "actor": "alice",
        })
        body = _rpc(mcp_client, "workflow.update", {
            "WorkflowName": "UpdateTarget",
            "WorkflowDescription": "updated desc",
            "actor": "alice",
        }, request_id=2)
        assert "result" in body
        assert body["result"]["WorkflowDescription"] == "updated desc"

    def test_update_non_existent_workflow_returns_error(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.update", {
            "WorkflowName": "DoesNotExist",
            "WorkflowDescription": "x",
            "actor": "alice",
        })
        assert "error" in body
        assert body["error"]["data"]["code"] == "workflow_not_found"

    def test_update_creates_new_active_row(self, mcp_client) -> None:
        _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "VersionedWF",
            "WorkflowDescription": "v1",
            "WorkflowContextDescription": "ctx",
            "actor": "alice",
        })
        body = _rpc(mcp_client, "workflow.update", {
            "WorkflowName": "VersionedWF",
            "WorkflowDescription": "v2",
            "actor": "alice",
        }, request_id=2)
        updated = body["result"]
        assert updated["WorkflowDescription"] == "v2"
        assert updated["DeleteInd"] == 0

    def test_update_missing_workflow_name_returns_error(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.update", {
            "WorkflowDescription": "no name",
            "actor": "alice",
        })
        assert "error" in body


# ---------------------------------------------------------------------------
# workflow.get
# ---------------------------------------------------------------------------

class TestWorkflowGet:
    def test_get_existing_workflow(self, mcp_client) -> None:
        _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "GetMe",
            "WorkflowDescription": "find me",
            "WorkflowContextDescription": "ctx",
            "actor": "alice",
        })
        body = _rpc(mcp_client, "workflow.get", {"WorkflowName": "GetMe"}, request_id=2)
        assert body["result"]["WorkflowName"] == "GetMe"

    def test_get_non_existent_workflow_returns_error(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.get", {"WorkflowName": "Ghost"})
        assert "error" in body
        assert body["error"]["data"]["code"] == "workflow_not_found"


# ---------------------------------------------------------------------------
# workflow.list
# ---------------------------------------------------------------------------

class TestWorkflowList:
    def test_list_returns_only_active_rows(self, mcp_client) -> None:
        _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "ListA",
            "WorkflowDescription": "a",
            "WorkflowContextDescription": "ctx",
            "actor": "alice",
        })
        _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "ListB",
            "WorkflowDescription": "b",
            "WorkflowContextDescription": "ctx",
            "actor": "alice",
        }, request_id=2)
        body = _rpc(mcp_client, "workflow.list", {}, request_id=3)
        names = [w["WorkflowName"] for w in body["result"]["workflows"]]
        assert "ListA" in names
        assert "ListB" in names

    def test_list_empty_when_no_workflows(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.list", {})
        assert body["result"]["workflows"] == []


# ---------------------------------------------------------------------------
# workflow.delete
# ---------------------------------------------------------------------------

class TestWorkflowDelete:
    def test_delete_marks_workflow_inactive(self, mcp_client) -> None:
        _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "ToDelete",
            "WorkflowDescription": "bye",
            "WorkflowContextDescription": "ctx",
            "actor": "alice",
        })
        body = _rpc(mcp_client, "workflow.delete", {
            "WorkflowName": "ToDelete",
            "actor": "alice",
        }, request_id=2)
        assert "result" in body

    def test_deleted_workflow_not_in_list(self, mcp_client) -> None:
        _rpc(mcp_client, "workflow.create", {
            "WorkflowName": "HideMe",
            "WorkflowDescription": "x",
            "WorkflowContextDescription": "ctx",
            "actor": "alice",
        })
        _rpc(mcp_client, "workflow.delete", {
            "WorkflowName": "HideMe",
            "actor": "alice",
        }, request_id=2)
        body = _rpc(mcp_client, "workflow.list", {}, request_id=3)
        names = [w["WorkflowName"] for w in body["result"]["workflows"]]
        assert "HideMe" not in names

    def test_delete_non_existent_workflow_returns_error(self, mcp_client) -> None:
        body = _rpc(mcp_client, "workflow.delete", {
            "WorkflowName": "Nobody",
            "actor": "alice",
        })
        assert "error" in body
        assert body["error"]["data"]["code"] == "workflow_not_found"
