"""Contract tests for dependent entity JSON-RPC methods — T019.

Uses an in-memory SQLite DB via the MCP Flask test client.
All 5 entity types are covered; Role is tested most thoroughly as the
canonical representative, with focused tests for each other entity type.
"""
from __future__ import annotations

import json
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.app import create_app
from mcp_server.src.api.handlers.dependent_handlers import make_all_dependent_handlers
from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers
from mcp_server.src.models.base import Base


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mcp_client(tmp_path):
    db_url = f"sqlite:///{tmp_path}/contract_dep.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    sf = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    app = create_app()
    # Register workflow handlers (needed for FK validation)
    for m, h in make_workflow_handlers(sf).items():
        app.register_jsonrpc_handler(m, h)  # type: ignore[attr-defined]
    for m, h in make_all_dependent_handlers(sf).items():
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


def _create_parent_workflow(client, name: str = "ParentWF") -> None:
    rpc(client, "workflow.create", {
        "WorkflowName": name,
        "WorkflowDescription": "parent",
        "WorkflowContextDescription": "ctx",
        "actor": "test",
    })


# ---------------------------------------------------------------------------
# Role — full CRUD contract
# ---------------------------------------------------------------------------

class TestRoleCreate:
    def test_create_returns_role_name(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client)
        body = rpc(mcp_client, "role.create", {
            "RoleName": "Manager",
            "WorkflowName": "ParentWF",
            "actor": "alice",
        })
        assert body["result"]["RoleName"] == "Manager"

    def test_create_returns_control_columns(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client)
        body = rpc(mcp_client, "role.create", {
            "RoleName": "Designer",
            "WorkflowName": "ParentWF",
            "actor": "bob",
        })
        assert body["result"]["DeleteInd"] == 0
        assert body["result"]["InsertUserName"] == "bob"

    def test_create_invalid_workflow_ref_returns_error(self, mcp_client) -> None:
        body = rpc(mcp_client, "role.create", {
            "RoleName": "Orphan",
            "WorkflowName": "DoesNotExist",
            "actor": "alice",
        })
        assert "error" in body
        assert body["error"]["data"]["code"] == "invalid_workflow_reference"

    def test_create_duplicate_active_key_returns_error(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "DupWF")
        params = {"RoleName": "Dup", "WorkflowName": "DupWF", "actor": "alice"}
        rpc(mcp_client, "role.create", params)
        body = rpc(mcp_client, "role.create", params, rid=2)
        assert "error" in body
        assert body["error"]["data"]["code"] == "duplicate_active_key"

    def test_create_missing_role_name_returns_error(self, mcp_client) -> None:
        body = rpc(mcp_client, "role.create", {"WorkflowName": "ParentWF", "actor": "alice"})
        assert "error" in body

    def test_create_missing_actor_returns_error(self, mcp_client) -> None:
        body = rpc(mcp_client, "role.create", {"RoleName": "X", "WorkflowName": "Y"})
        assert "error" in body


class TestRoleUpdate:
    def test_update_existing_role(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client)
        rpc(mcp_client, "role.create", {"RoleName": "ToUpdate", "WorkflowName": "ParentWF", "actor": "alice"})
        body = rpc(mcp_client, "role.update", {
            "RoleName": "ToUpdate",
            "WorkflowName": "ParentWF",
            "RoleDescription": "updated",
            "actor": "alice",
        }, rid=2)
        assert body["result"]["RoleDescription"] == "updated"

    def test_update_non_existent_role_returns_error(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client)
        body = rpc(mcp_client, "role.update", {
            "RoleName": "Ghost", "WorkflowName": "ParentWF", "actor": "alice"
        })
        assert "error" in body
        assert body["error"]["data"]["code"] == "entity_not_found"


class TestRoleGetListDelete:
    def test_get_existing_role(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client)
        rpc(mcp_client, "role.create", {"RoleName": "Fetched", "WorkflowName": "ParentWF", "actor": "u"})
        body = rpc(mcp_client, "role.get", {"RoleName": "Fetched", "WorkflowName": "ParentWF"}, rid=2)
        assert body["result"]["RoleName"] == "Fetched"

    def test_get_non_existent_returns_error(self, mcp_client) -> None:
        body = rpc(mcp_client, "role.get", {"RoleName": "Ghost", "WorkflowName": "WF"})
        assert "error" in body

    def test_list_returns_active_roles(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "ListWF")
        rpc(mcp_client, "role.create", {"RoleName": "RA", "WorkflowName": "ListWF", "actor": "u"})
        rpc(mcp_client, "role.create", {"RoleName": "RB", "WorkflowName": "ListWF", "actor": "u"}, rid=2)
        body = rpc(mcp_client, "role.list", {"WorkflowName": "ListWF"}, rid=3)
        names = [r["RoleName"] for r in body["result"]["roles"]]
        assert "RA" in names and "RB" in names

    def test_delete_removes_from_list(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "DelWF")
        rpc(mcp_client, "role.create", {"RoleName": "RDel", "WorkflowName": "DelWF", "actor": "u"})
        rpc(mcp_client, "role.delete", {"RoleName": "RDel", "WorkflowName": "DelWF", "actor": "u"}, rid=2)
        body = rpc(mcp_client, "role.list", {"WorkflowName": "DelWF"}, rid=3)
        names = [r["RoleName"] for r in body["result"]["roles"]]
        assert "RDel" not in names


# ---------------------------------------------------------------------------
# Interaction — focused tests
# ---------------------------------------------------------------------------

class TestInteractionContract:
    def test_create_success(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "IWF")
        body = rpc(mcp_client, "interaction.create", {
            "InteractionName": "Click",
            "WorkflowName": "IWF",
            "InteractionType": "UI",
            "actor": "u",
        })
        assert body["result"]["InteractionName"] == "Click"
        assert body["result"]["InteractionType"] == "UI"

    def test_create_invalid_workflow_returns_error(self, mcp_client) -> None:
        body = rpc(mcp_client, "interaction.create", {
            "InteractionName": "X", "WorkflowName": "NoneWF", "actor": "u"
        })
        assert "error" in body
        assert body["error"]["data"]["code"] == "invalid_workflow_reference"

    def test_update_interaction(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "IWF2")
        rpc(mcp_client, "interaction.create", {"InteractionName": "Step1", "WorkflowName": "IWF2", "actor": "u"})
        body = rpc(mcp_client, "interaction.update", {
            "InteractionName": "Step1", "WorkflowName": "IWF2",
            "InteractionDescription": "updated", "actor": "u",
        }, rid=2)
        assert body["result"]["InteractionDescription"] == "updated"


# ---------------------------------------------------------------------------
# Guard — focused tests
# ---------------------------------------------------------------------------

class TestGuardContract:
    def test_create_success(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "GWF")
        body = rpc(mcp_client, "guard.create", {
            "GuardName": "LimitCheck",
            "WorkflowName": "GWF",
            "GuardType": "AMOUNT",
            "actor": "u",
        })
        assert body["result"]["GuardName"] == "LimitCheck"
        assert body["result"]["GuardType"] == "AMOUNT"

    def test_create_missing_workflow_name_returns_error(self, mcp_client) -> None:
        body = rpc(mcp_client, "guard.create", {"GuardName": "G", "actor": "u"})
        assert "error" in body

    def test_delete_guard(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "GWF2")
        rpc(mcp_client, "guard.create", {"GuardName": "GDel", "WorkflowName": "GWF2", "actor": "u"})
        body = rpc(mcp_client, "guard.delete", {"GuardName": "GDel", "WorkflowName": "GWF2", "actor": "u"}, rid=2)
        assert "result" in body


# ---------------------------------------------------------------------------
# InteractionComponent — focused tests
# ---------------------------------------------------------------------------

class TestInteractionComponentContract:
    def test_create_success(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "ICWF")
        body = rpc(mcp_client, "interaction_component.create", {
            "InteractionComponentName": "Edge1",
            "WorkflowName": "ICWF",
            "SourceName": "Start",
            "TargetName": "End",
            "actor": "u",
        })
        assert body["result"]["InteractionComponentName"] == "Edge1"
        assert body["result"]["SourceName"] == "Start"

    def test_create_invalid_workflow_ref_returns_error(self, mcp_client) -> None:
        body = rpc(mcp_client, "interaction_component.create", {
            "InteractionComponentName": "E", "WorkflowName": "NoWF", "actor": "u"
        })
        assert body["error"]["data"]["code"] == "invalid_workflow_reference"

    def test_list_filtered_by_workflow(self, mcp_client) -> None:
        _create_parent_workflow(mcp_client, "ICWF2")
        rpc(mcp_client, "interaction_component.create", {
            "InteractionComponentName": "IC1", "WorkflowName": "ICWF2", "actor": "u"
        })
        body = rpc(mcp_client, "interaction_component.list", {"WorkflowName": "ICWF2"}, rid=2)
        assert any(ic["InteractionComponentName"] == "IC1" for ic in body["result"]["interaction_components"])


# ---------------------------------------------------------------------------
# UnitOfWork — focused tests (no workflow FK)
# ---------------------------------------------------------------------------

class TestUnitOfWorkContract:
    def test_create_success_no_workflow_required(self, mcp_client) -> None:
        body = rpc(mcp_client, "unit_of_work.create", {
            "UnitOfWorkID": "UOW-001",
            "UnitOfWorkType": "HTTP",
            "actor": "u",
        })
        assert body["result"]["UnitOfWorkID"] == "UOW-001"

    def test_create_does_not_validate_workflow(self, mcp_client) -> None:
        """UnitOfWork has no workflow FK — must succeed without a parent workflow."""
        body = rpc(mcp_client, "unit_of_work.create", {
            "UnitOfWorkID": "UOW-002",
            "actor": "u",
        })
        assert "result" in body
        assert "error" not in body

    def test_create_duplicate_uow_id_returns_error(self, mcp_client) -> None:
        rpc(mcp_client, "unit_of_work.create", {"UnitOfWorkID": "UOW-DUP", "actor": "u"})
        body = rpc(mcp_client, "unit_of_work.create", {"UnitOfWorkID": "UOW-DUP", "actor": "u"}, rid=2)
        assert body["error"]["data"]["code"] == "duplicate_active_key"

    def test_update_unit_of_work(self, mcp_client) -> None:
        rpc(mcp_client, "unit_of_work.create", {"UnitOfWorkID": "UOW-UPD", "UnitOfWorkType": "v1", "actor": "u"})
        body = rpc(mcp_client, "unit_of_work.update", {
            "UnitOfWorkID": "UOW-UPD", "UnitOfWorkType": "v2", "actor": "u"
        }, rid=2)
        assert body["result"]["UnitOfWorkType"] == "v2"

    def test_list_unit_of_works(self, mcp_client) -> None:
        rpc(mcp_client, "unit_of_work.create", {"UnitOfWorkID": "UOW-L1", "actor": "u"})
        body = rpc(mcp_client, "unit_of_work.list", {}, rid=2)
        ids = [u["UnitOfWorkID"] for u in body["result"]["unit_of_works"]]
        assert "UOW-L1" in ids
