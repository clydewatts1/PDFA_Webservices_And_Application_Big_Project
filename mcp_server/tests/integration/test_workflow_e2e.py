"""Integration tests: full workflow lifecycle through MCP server with SQLite — T013.

Tests the flow: [Flask test client] -> [MCP /rpc endpoint] -> [SQLAlchemy / SQLite]
covering the complete create → get → update → delete lifecycle and temporal semantics.
"""
from __future__ import annotations

import json
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.app import create_app
from mcp_server.src.models.base import Base
from mcp_server.src.models.workflow import Workflow, WorkflowHist
from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db_engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path}/integration.db",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture()
def session_factory(db_engine):
    return sessionmaker(bind=db_engine, autocommit=False, autoflush=False)


@pytest.fixture()
def client(session_factory):
    app = create_app()
    for method, handler in make_workflow_handlers(session_factory).items():
        app.register_jsonrpc_handler(method, handler)  # type: ignore[attr-defined]
    app.config["TESTING"] = True
    return app.test_client()


def rpc(client, method: str, params: dict, request_id: int = 1) -> dict:
    resp = client.post(
        "/rpc",
        data=json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}),
        content_type="application/json",
    )
    return resp.get_json()


# ---------------------------------------------------------------------------
# Full Workflow Lifecycle
# ---------------------------------------------------------------------------

class TestWorkflowLifecycle:
    def test_create_then_get(self, client) -> None:
        rpc(client, "workflow.create", {
            "WorkflowName": "LifecycleWF",
            "WorkflowDescription": "initial",
            "WorkflowContextDescription": "integration test",
            "actor": "integration_user",
        })
        body = rpc(client, "workflow.get", {"WorkflowName": "LifecycleWF"}, request_id=2)
        assert body["result"]["WorkflowName"] == "LifecycleWF"
        assert body["result"]["WorkflowDescription"] == "initial"

    def test_update_produces_new_description(self, client) -> None:
        rpc(client, "workflow.create", {
            "WorkflowName": "UpdateWF",
            "WorkflowDescription": "v1",
            "WorkflowContextDescription": "ctx",
            "actor": "user",
        })
        rpc(client, "workflow.update", {
            "WorkflowName": "UpdateWF",
            "WorkflowDescription": "v2",
            "actor": "user",
        }, request_id=2)
        body = rpc(client, "workflow.get", {"WorkflowName": "UpdateWF"}, request_id=3)
        assert body["result"]["WorkflowDescription"] == "v2"

    def test_delete_makes_workflow_unfindable(self, client) -> None:
        rpc(client, "workflow.create", {
            "WorkflowName": "DeleteWF",
            "WorkflowDescription": "x",
            "WorkflowContextDescription": "ctx",
            "actor": "user",
        })
        rpc(client, "workflow.delete", {"WorkflowName": "DeleteWF", "actor": "user"}, request_id=2)
        body = rpc(client, "workflow.get", {"WorkflowName": "DeleteWF"}, request_id=3)
        assert "error" in body

    def test_duplicate_create_fails(self, client) -> None:
        params = {
            "WorkflowName": "DupWF",
            "WorkflowDescription": "d",
            "WorkflowContextDescription": "c",
            "actor": "user",
        }
        rpc(client, "workflow.create", params)
        body = rpc(client, "workflow.create", params, request_id=2)
        assert "error" in body
        assert body["error"]["data"]["code"] == "duplicate_active_key"


# ---------------------------------------------------------------------------
# Temporal / History Semantics
# ---------------------------------------------------------------------------

class TestTemporalSemantics:
    def test_update_writes_prior_row_to_hist(self, client, session_factory) -> None:
        """After update, the old active row must appear in Workflow_Hist."""
        rpc(client, "workflow.create", {
            "WorkflowName": "HistWF",
            "WorkflowDescription": "original",
            "WorkflowContextDescription": "ctx",
            "actor": "user",
        })
        rpc(client, "workflow.update", {
            "WorkflowName": "HistWF",
            "WorkflowDescription": "revised",
            "actor": "user",
        }, request_id=2)

        with session_factory() as session:
            hist_rows = session.query(WorkflowHist).filter_by(WorkflowName="HistWF").all()
        assert len(hist_rows) == 1
        assert hist_rows[0].WorkflowDescription == "original"

    def test_update_closes_prior_current_row(self, client, session_factory) -> None:
        """After update, only one active row must exist per WorkflowName."""
        from mcp_server.src.models.base import HIGH_DATE
        rpc(client, "workflow.create", {
            "WorkflowName": "CloseWF",
            "WorkflowDescription": "first",
            "WorkflowContextDescription": "ctx",
            "actor": "user",
        })
        rpc(client, "workflow.update", {
            "WorkflowName": "CloseWF",
            "WorkflowDescription": "second",
            "actor": "user",
        }, request_id=2)

        with session_factory() as session:
            active = (
                session.query(Workflow)
                .filter_by(WorkflowName="CloseWF", DeleteInd=0)
                .filter(Workflow.EffToDateTime == HIGH_DATE)
                .all()
            )
        assert len(active) == 1
        assert active[0].WorkflowDescription == "second"

    def test_list_excludes_closed_rows(self, client, session_factory) -> None:
        """After update of ClosedRow_WF, list must return only the latest active row."""
        rpc(client, "workflow.create", {
            "WorkflowName": "ClosedRowWF",
            "WorkflowDescription": "v1",
            "WorkflowContextDescription": "ctx",
            "actor": "user",
        })
        rpc(client, "workflow.update", {
            "WorkflowName": "ClosedRowWF",
            "WorkflowDescription": "v2",
            "actor": "user",
        }, request_id=2)
        body = rpc(client, "workflow.list", {}, request_id=3)
        matching = [w for w in body["result"]["workflows"] if w["WorkflowName"] == "ClosedRowWF"]
        assert len(matching) == 1
        assert matching[0]["WorkflowDescription"] == "v2"

    def test_delete_sets_delete_ind_and_closes_row(self, client, session_factory) -> None:
        """After delete, the Workflow current row must have DeleteInd=1 and EffToDateTime != HIGH_DATE."""
        from mcp_server.src.models.base import HIGH_DATE
        rpc(client, "workflow.create", {
            "WorkflowName": "SoftDeleteWF",
            "WorkflowDescription": "d",
            "WorkflowContextDescription": "c",
            "actor": "user",
        })
        rpc(client, "workflow.delete", {"WorkflowName": "SoftDeleteWF", "actor": "user"}, request_id=2)

        with session_factory() as session:
            row = session.query(Workflow).filter_by(WorkflowName="SoftDeleteWF").first()
        assert row is not None
        assert row.DeleteInd == 1
        assert row.EffToDateTime != HIGH_DATE


# ---------------------------------------------------------------------------
# Active Row Invariant
# ---------------------------------------------------------------------------

class TestActiveRowInvariant:
    def test_only_one_active_row_after_multiple_updates(self, client, session_factory) -> None:
        from mcp_server.src.models.base import HIGH_DATE
        rpc(client, "workflow.create", {
            "WorkflowName": "MultiUpdateWF",
            "WorkflowDescription": "v1",
            "WorkflowContextDescription": "ctx",
            "actor": "user",
        })
        for v in ("v2", "v3", "v4"):
            rpc(client, "workflow.update", {
                "WorkflowName": "MultiUpdateWF",
                "WorkflowDescription": v,
                "actor": "user",
            }, request_id=int(v[1]) + 1)

        with session_factory() as session:
            active = (
                session.query(Workflow)
                .filter_by(WorkflowName="MultiUpdateWF", DeleteInd=0)
                .filter(Workflow.EffToDateTime == HIGH_DATE)
                .all()
            )
        assert len(active) == 1
        assert active[0].WorkflowDescription == "v4"
