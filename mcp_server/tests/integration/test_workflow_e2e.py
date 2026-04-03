"""Integration tests for workflow lifecycle and MySQL migration execution.

Tests the flow: [Flask test client] -> [MCP /rpc endpoint] -> [SQLAlchemy / MySQL]
covering migration execution plus create → get → update → delete lifecycle and temporal semantics.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers
from mcp_server.src.models.base import Base
from mcp_server.src.models.workflow import Workflow, WorkflowHist
from mcp_server.tests.conftest import build_test_client


REPO_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def session_factory(mysql_session_factory):
    return mysql_session_factory


@pytest.fixture()
def client(session_factory):
    return build_test_client(session_factory, make_workflow_handlers(session_factory))


def rpc(client, method: str, params: dict, request_id: int = 1) -> dict:
    resp = client.post(
        "/rpc",
        data=json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}),
        content_type="application/json",
    )
    return resp.get_json()


# ---------------------------------------------------------------------------
# Migration execution
# ---------------------------------------------------------------------------

class TestMigrationExecution:
    def test_migration_baseline_to_head_executes_on_mysql(self, mysql_test_engine, mysql_test_db_url, monkeypatch) -> None:
        Base.metadata.drop_all(mysql_test_engine, checkfirst=True)
        with mysql_test_engine.begin() as connection:
            connection.execute(text("DROP TABLE IF EXISTS alembic_version"))

        config = Config(str(REPO_ROOT / "database" / "alembic.ini"))
        monkeypatch.setenv("DB_URL", mysql_test_db_url)

        try:
            command.upgrade(config, "head")

            with mysql_test_engine.begin() as connection:
                revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                table_names = {
                    row[0]
                    for row in connection.execute(
                        text("SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()")
                    )
                }

            assert revision == "0001_current_history_tables"
            assert {"Workflow", "Workflow_Hist", "Instance", "Instance_Hist"}.issubset(table_names)
        finally:
            Base.metadata.drop_all(mysql_test_engine, checkfirst=True)
            with mysql_test_engine.begin() as connection:
                connection.execute(text("DROP TABLE IF EXISTS alembic_version"))


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
        """After update, the old current row must appear in Workflow_Hist."""
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

    def test_update_keeps_only_one_primary_row(self, client, session_factory) -> None:
        """After update, Workflow must keep only one row for the business key."""
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
            rows = session.query(Workflow).filter_by(WorkflowName="CloseWF").all()
        assert len(rows) == 1
        assert rows[0].WorkflowDescription == "second"

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
        matching = [w for w in body["result"]["records"] if w["WorkflowName"] == "ClosedRowWF"]
        assert len(matching) == 1
        assert matching[0]["WorkflowDescription"] == "v2"

    def test_delete_updates_the_single_primary_row(self, client, session_factory) -> None:
        """After delete, the single Workflow row must be marked deleted and closed."""
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
    def test_only_one_primary_row_after_multiple_updates(self, client, session_factory) -> None:
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
            rows = session.query(Workflow).filter_by(WorkflowName="MultiUpdateWF").all()
        assert len(rows) == 1
        assert rows[0].WorkflowDescription == "v4"
