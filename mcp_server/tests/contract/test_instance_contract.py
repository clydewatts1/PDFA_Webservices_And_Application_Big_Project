from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.app import create_app
from mcp_server.src.api.handlers.dependent_handlers import make_all_dependent_handlers
from mcp_server.src.api.handlers.instance_handlers import make_instance_handlers
from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers
from mcp_server.src.models.base import Base


@pytest.fixture()
def mcp_client(tmp_path):
    db_url = f"sqlite:///{tmp_path}/contract_instance.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    sf = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    app = create_app()
    for m, h in make_workflow_handlers(sf).items():
        app.register_jsonrpc_handler(m, h)  # type: ignore[attr-defined]
    for m, h in make_all_dependent_handlers(sf).items():
        app.register_jsonrpc_handler(m, h)  # type: ignore[attr-defined]
    for m, h in make_instance_handlers(sf).items():
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


def _seed_workflow_and_dependents(client, wf: str = "WFI") -> None:
    rpc(client, "workflow.create", {
        "WorkflowName": wf,
        "WorkflowDescription": "d",
        "WorkflowContextDescription": "c",
        "actor": "seed",
    })
    rpc(client, "role.create", {"RoleName": "R1", "WorkflowName": wf, "actor": "seed"}, rid=2)
    rpc(client, "interaction.create", {"InteractionName": "I1", "WorkflowName": wf, "actor": "seed"}, rid=3)
    rpc(client, "guard.create", {"GuardName": "G1", "WorkflowName": wf, "actor": "seed"}, rid=4)
    rpc(client, "interaction_component.create", {
        "InteractionComponentName": "C1", "WorkflowName": wf, "actor": "seed"
    }, rid=5)


class TestInstanceCreate:
    def test_create_instance_success(self, mcp_client) -> None:
        _seed_workflow_and_dependents(mcp_client, "WF-C1")
        body = rpc(mcp_client, "instance.create", {
            "InstanceName": "INST-001",
            "WorkflowName": "WF-C1",
            "actor": "alice",
        })
        assert "result" in body
        assert body["result"]["InstanceName"] == "INST-001"
        assert body["result"]["WorkflowName"] == "WF-C1"

    def test_create_replication_counts_returned(self, mcp_client) -> None:
        _seed_workflow_and_dependents(mcp_client, "WF-C2")
        body = rpc(mcp_client, "instance.create", {
            "InstanceName": "INST-002",
            "WorkflowName": "WF-C2",
            "actor": "alice",
        })
        repl = body["result"]["replication"]
        assert repl["roles"] == 1
        assert repl["interactions"] == 1
        assert repl["guards"] == 1
        assert repl["interaction_components"] == 1

    def test_create_duplicate_instance_name_returns_error(self, mcp_client) -> None:
        _seed_workflow_and_dependents(mcp_client, "WF-C3")
        params = {"InstanceName": "INST-DUP", "WorkflowName": "WF-C3", "actor": "alice"}
        rpc(mcp_client, "instance.create", params)
        body = rpc(mcp_client, "instance.create", params, rid=2)
        assert "error" in body
        assert body["error"]["data"]["code"] == "duplicate_active_key"

    def test_create_missing_workflow_returns_error(self, mcp_client) -> None:
        body = rpc(mcp_client, "instance.create", {
            "InstanceName": "INST-404",
            "WorkflowName": "NO-WF",
            "actor": "alice",
        })
        assert "error" in body


class TestInstanceStateAndList:
    def test_update_state_success(self, mcp_client) -> None:
        _seed_workflow_and_dependents(mcp_client, "WF-S1")
        rpc(mcp_client, "instance.create", {"InstanceName": "INST-S1", "WorkflowName": "WF-S1", "actor": "u"})
        body = rpc(mcp_client, "instance.update_state", {
            "InstanceName": "INST-S1",
            "InstanceState": "P",
            "actor": "u",
        }, rid=2)
        assert body["result"]["InstanceState"] == "P"

    def test_update_state_invalid_value_returns_error(self, mcp_client) -> None:
        _seed_workflow_and_dependents(mcp_client, "WF-S2")
        rpc(mcp_client, "instance.create", {"InstanceName": "INST-S2", "WorkflowName": "WF-S2", "actor": "u"})
        body = rpc(mcp_client, "instance.update_state", {
            "InstanceName": "INST-S2",
            "InstanceState": "Z",
            "actor": "u",
        }, rid=2)
        assert "error" in body
        assert body["error"]["data"]["code"] == "invalid_instance_state"

    def test_get_instance(self, mcp_client) -> None:
        _seed_workflow_and_dependents(mcp_client, "WF-G1")
        rpc(mcp_client, "instance.create", {"InstanceName": "INST-G1", "WorkflowName": "WF-G1", "actor": "u"})
        body = rpc(mcp_client, "instance.get", {"InstanceName": "INST-G1"}, rid=2)
        assert body["result"]["InstanceName"] == "INST-G1"

    def test_list_instances_filtered_by_workflow(self, mcp_client) -> None:
        _seed_workflow_and_dependents(mcp_client, "WF-L1")
        _seed_workflow_and_dependents(mcp_client, "WF-L2")
        rpc(mcp_client, "instance.create", {"InstanceName": "I1", "WorkflowName": "WF-L1", "actor": "u"})
        rpc(mcp_client, "instance.create", {"InstanceName": "I2", "WorkflowName": "WF-L2", "actor": "u"}, rid=2)
        body = rpc(mcp_client, "instance.list", {"WorkflowName": "WF-L1"}, rid=3)
        names = [i["InstanceName"] for i in body["result"]["instances"]]
        assert "I1" in names
        assert "I2" not in names
