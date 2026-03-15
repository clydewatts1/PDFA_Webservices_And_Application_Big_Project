"""Integration tests: invalid workflow linkage and temporal invariants — T020.

Tests verify the full stack: Flask test client → MCP /rpc → SQLAlchemy/SQLite.
Focus areas:
  - FK validation: dependent entities with invalid WorkflowName refs are rejected
  - Temporal invariants: one active row after multiple updates; history is populated
  - Cross-entity: roles and interactions share a workflow; deleting workflow does not
    automatically delete dependents (physical FK enforcement not in this increment)
"""
from __future__ import annotations

import json
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.app import create_app
from mcp_server.src.api.handlers.dependent_handlers import make_all_dependent_handlers
from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers
from mcp_server.src.models.base import Base, HIGH_DATE
from mcp_server.src.models.dependent import Role, RoleHist, Interaction, InteractionHist


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db_engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path}/integrity.db",
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
    for m, h in make_workflow_handlers(session_factory).items():
        app.register_jsonrpc_handler(m, h)  # type: ignore[attr-defined]
    for m, h in make_all_dependent_handlers(session_factory).items():
        app.register_jsonrpc_handler(m, h)  # type: ignore[attr-defined]
    app.config["TESTING"] = True
    return app.test_client()


def rpc(client, method: str, params: dict, rid: int = 1) -> dict:
    resp = client.post(
        "/rpc",
        data=json.dumps({"jsonrpc": "2.0", "id": rid, "method": method, "params": params}),
        content_type="application/json",
    )
    return resp.get_json()


def _wf(client, name: str = "WF"):
    rpc(client, "workflow.create", {
        "WorkflowName": name,
        "WorkflowDescription": "d",
        "WorkflowContextDescription": "c",
        "actor": "u",
    })


# ---------------------------------------------------------------------------
# Invalid workflow FK linkage
# ---------------------------------------------------------------------------

class TestInvalidWorkflowLinkage:
    def test_role_create_with_missing_workflow_rejected(self, client) -> None:
        body = rpc(client, "role.create", {
            "RoleName": "Orphan", "WorkflowName": "NoSuchWF", "actor": "u"
        })
        assert "error" in body
        assert body["error"]["data"]["code"] == "invalid_workflow_reference"

    def test_interaction_create_with_deleted_workflow_rejected(self, client) -> None:
        """Create then soft-delete the parent workflow; subsequent interaction create must fail."""
        _wf(client, "DeletedWF")
        rpc(client, "workflow.delete", {"WorkflowName": "DeletedWF", "actor": "u"}, rid=2)
        body = rpc(client, "interaction.create", {
            "InteractionName": "Step1", "WorkflowName": "DeletedWF", "actor": "u"
        }, rid=3)
        assert "error" in body
        assert body["error"]["data"]["code"] == "invalid_workflow_reference"

    def test_guard_create_with_missing_workflow_rejected(self, client) -> None:
        body = rpc(client, "guard.create", {
            "GuardName": "G", "WorkflowName": "GhostWF", "actor": "u"
        })
        assert body["error"]["data"]["code"] == "invalid_workflow_reference"

    def test_interaction_component_with_missing_workflow_rejected(self, client) -> None:
        body = rpc(client, "interaction_component.create", {
            "InteractionComponentName": "E", "WorkflowName": "NoWF", "actor": "u"
        })
        assert body["error"]["data"]["code"] == "invalid_workflow_reference"

    def test_unit_of_work_create_ignores_workflow_altogether(self, client) -> None:
        """UnitOfWork must never validate a WorkflowName FK."""
        body = rpc(client, "unit_of_work.create", {
            "UnitOfWorkID": "UOW-FREE", "actor": "u"
        })
        assert "result" in body


# ---------------------------------------------------------------------------
# Active-row invariant after multiple updates (Role)
# ---------------------------------------------------------------------------

class TestRoleTemporalInvariant:
    def test_only_one_primary_row_after_multiple_updates(self, client, session_factory) -> None:
        _wf(client, "TemporalWF")
        rpc(client, "role.create", {"RoleName": "Developer", "WorkflowName": "TemporalWF", "actor": "u"})
        for desc in ("v2", "v3", "v4"):
            rpc(client, "role.update", {
                "RoleName": "Developer", "WorkflowName": "TemporalWF",
                "RoleDescription": desc, "actor": "u",
            })

        with session_factory() as session:
            rows = session.query(Role).filter_by(RoleName="Developer", WorkflowName="TemporalWF").all()
        assert len(rows) == 1
        assert rows[0].RoleDescription == "v4"

    def test_updates_write_prior_rows_to_history(self, client, session_factory) -> None:
        _wf(client, "HistWF2")
        rpc(client, "role.create", {"RoleName": "Tester", "WorkflowName": "HistWF2", "actor": "u"})
        for desc in ("update1", "update2"):
            rpc(client, "role.update", {
                "RoleName": "Tester", "WorkflowName": "HistWF2",
                "RoleDescription": desc, "actor": "u",
            })

        with session_factory() as session:
            hist = session.query(RoleHist).filter_by(RoleName="Tester", WorkflowName="HistWF2").all()
        assert len(hist) == 2

    def test_delete_sets_delete_ind_and_closes_row(self, client, session_factory) -> None:
        _wf(client, "SoftDelWF")
        rpc(client, "role.create", {"RoleName": "ToDelete", "WorkflowName": "SoftDelWF", "actor": "u"})
        rpc(client, "role.delete", {"RoleName": "ToDelete", "WorkflowName": "SoftDelWF", "actor": "u"}, rid=2)

        with session_factory() as session:
            row = session.query(Role).filter_by(RoleName="ToDelete", WorkflowName="SoftDelWF").first()
        assert row is not None
        assert row.DeleteInd == 1
        assert row.EffToDateTime != HIGH_DATE

    def test_list_excludes_deleted_roles(self, client) -> None:
        _wf(client, "ListDelWF")
        rpc(client, "role.create", {"RoleName": "Visible", "WorkflowName": "ListDelWF", "actor": "u"})
        rpc(client, "role.create", {"RoleName": "Hidden", "WorkflowName": "ListDelWF", "actor": "u"}, rid=2)
        rpc(client, "role.delete", {"RoleName": "Hidden", "WorkflowName": "ListDelWF", "actor": "u"}, rid=3)
        body = rpc(client, "role.list", {"WorkflowName": "ListDelWF"}, rid=4)
        names = [r["RoleName"] for r in body["result"]["roles"]]
        assert "Visible" in names
        assert "Hidden" not in names


# ---------------------------------------------------------------------------
# Interaction temporal semantics
# ---------------------------------------------------------------------------

class TestInteractionTemporalSemantics:
    def test_update_creates_history_row(self, client, session_factory) -> None:
        _wf(client, "IHistWF")
        rpc(client, "interaction.create", {"InteractionName": "S1", "WorkflowName": "IHistWF", "actor": "u"})
        rpc(client, "interaction.update", {
            "InteractionName": "S1", "WorkflowName": "IHistWF",
            "InteractionDescription": "revised", "actor": "u",
        }, rid=2)

        with session_factory() as session:
            hist = session.query(InteractionHist).filter_by(InteractionName="S1", WorkflowName="IHistWF").all()
        assert len(hist) == 1

    def test_only_one_primary_interaction_after_update(self, client, session_factory) -> None:
        _wf(client, "IActiveWF")
        rpc(client, "interaction.create", {"InteractionName": "Step", "WorkflowName": "IActiveWF", "actor": "u"})
        rpc(client, "interaction.update", {
            "InteractionName": "Step", "WorkflowName": "IActiveWF",
            "InteractionType": "API", "actor": "u",
        }, rid=2)

        with session_factory() as session:
            rows = session.query(Interaction).filter_by(InteractionName="Step", WorkflowName="IActiveWF").all()
        assert len(rows) == 1
        assert rows[0].InteractionType == "API"


# ---------------------------------------------------------------------------
# UnitOfWork temporal (no FK validation)
# ---------------------------------------------------------------------------

class TestUnitOfWorkTemporal:
    def test_uow_update_creates_history(self, client, session_factory) -> None:
        from mcp_server.src.models.dependent import UnitOfWork, UnitOfWorkHist
        rpc(client, "unit_of_work.create", {"UnitOfWorkID": "UOW-T1", "UnitOfWorkType": "v1", "actor": "u"})
        rpc(client, "unit_of_work.update", {"UnitOfWorkID": "UOW-T1", "UnitOfWorkType": "v2", "actor": "u"}, rid=2)

        with session_factory() as session:
            hist = session.query(UnitOfWorkHist).filter_by(UnitOfWorkID="UOW-T1").all()
            rows = session.query(UnitOfWork).filter_by(UnitOfWorkID="UOW-T1").all()
        assert len(hist) == 1
        assert len(rows) == 1
        assert rows[0].UnitOfWorkType == "v2"
