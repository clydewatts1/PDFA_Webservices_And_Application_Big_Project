from __future__ import annotations

import json

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.app import create_app
from mcp_server.src.api.handlers.dependent_handlers import make_all_dependent_handlers
from mcp_server.src.api.handlers.instance_handlers import make_instance_handlers
from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers
from mcp_server.src.models.base import Base, HIGH_DATE
from mcp_server.src.models.dependent import Guard, Interaction, InteractionComponent, Role, UnitOfWork
from mcp_server.src.models.instance import Instance, InstanceHist


@pytest.fixture()
def db_engine(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/instance_e2e.db", connect_args={"check_same_thread": False})
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
    for m, h in make_instance_handlers(session_factory).items():
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


def _seed_baseline(client, wf: str = "WF-E2E") -> None:
    rpc(client, "workflow.create", {
        "WorkflowName": wf,
        "WorkflowDescription": "d",
        "WorkflowContextDescription": "c",
        "actor": "seed",
    })
    rpc(client, "role.create", {"RoleName": "R-A", "WorkflowName": wf, "actor": "seed"}, rid=2)
    rpc(client, "interaction.create", {"InteractionName": "I-A", "WorkflowName": wf, "actor": "seed"}, rid=3)
    rpc(client, "guard.create", {"GuardName": "G-A", "WorkflowName": wf, "actor": "seed"}, rid=4)
    rpc(client, "interaction_component.create", {"InteractionComponentName": "C-A", "WorkflowName": wf, "actor": "seed"}, rid=5)
    rpc(client, "unit_of_work.create", {"UnitOfWorkID": "UOW-A", "actor": "seed"}, rid=6)


class TestInstanceReplicationE2E:
    def test_instance_create_replicates_expected_entities(self, client, session_factory) -> None:
        _seed_baseline(client, "WF-R1")
        body = rpc(client, "instance.create", {
            "InstanceName": "INST-R1",
            "WorkflowName": "WF-R1",
            "actor": "alice",
        })
        assert "result" in body

        with session_factory() as session:
            role_rows = session.query(Role).filter_by(WorkflowName="WF-R1", InstanceName="INST-R1", DeleteInd=0).all()
            interaction_rows = session.query(Interaction).filter_by(WorkflowName="WF-R1", InstanceName="INST-R1", DeleteInd=0).all()
            guard_rows = session.query(Guard).filter_by(WorkflowName="WF-R1", InstanceName="INST-R1", DeleteInd=0).all()
            ic_rows = session.query(InteractionComponent).filter_by(WorkflowName="WF-R1", InstanceName="INST-R1", DeleteInd=0).all()
            uow_rows = session.query(UnitOfWork).filter_by(DeleteInd=0).all()
        assert len(role_rows) == 1
        assert len(interaction_rows) == 1
        assert len(guard_rows) == 1
        assert len(ic_rows) == 1
        assert len(uow_rows) == 1

    def test_replicated_rows_are_instance_scoped(self, client, session_factory) -> None:
        _seed_baseline(client, "WF-R2")
        rpc(client, "instance.create", {"InstanceName": "INST-A", "WorkflowName": "WF-R2", "actor": "u"})
        rpc(client, "instance.create", {"InstanceName": "INST-B", "WorkflowName": "WF-R2", "actor": "u"}, rid=2)

        with session_factory() as session:
            inst_a_roles = session.query(Role).filter_by(WorkflowName="WF-R2", InstanceName="INST-A", DeleteInd=0).all()
            inst_b_roles = session.query(Role).filter_by(WorkflowName="WF-R2", InstanceName="INST-B", DeleteInd=0).all()
        assert len(inst_a_roles) == 1
        assert len(inst_b_roles) == 1
        assert inst_a_roles[0].RoleName == inst_b_roles[0].RoleName

    def test_duplicate_instance_name_rejected(self, client) -> None:
        _seed_baseline(client, "WF-R3")
        rpc(client, "instance.create", {"InstanceName": "INST-D", "WorkflowName": "WF-R3", "actor": "u"})
        body = rpc(client, "instance.create", {"InstanceName": "INST-D", "WorkflowName": "WF-R3", "actor": "u"}, rid=2)
        assert "error" in body

    def test_create_fails_when_workflow_missing(self, client) -> None:
        body = rpc(client, "instance.create", {"InstanceName": "INST-X", "WorkflowName": "NOPE", "actor": "u"})
        assert "error" in body

    def test_update_state_creates_history_and_new_current_row(self, client, session_factory) -> None:
        _seed_baseline(client, "WF-R4")
        rpc(client, "instance.create", {"InstanceName": "INST-S", "WorkflowName": "WF-R4", "actor": "u"})
        rpc(client, "instance.update_state", {"InstanceName": "INST-S", "InstanceState": "P", "actor": "u"}, rid=2)

        with session_factory() as session:
            current = (
                session.query(Instance)
                .filter_by(InstanceName="INST-S", DeleteInd=0)
                .filter(Instance.EffToDateTime == HIGH_DATE)
                .all()
            )
            hist = session.query(InstanceHist).filter_by(InstanceName="INST-S").all()
        assert len(current) == 1
        assert current[0].InstanceState == "P"
        assert len(hist) == 1

    def test_update_state_invalid_value_fails(self, client) -> None:
        _seed_baseline(client, "WF-R5")
        rpc(client, "instance.create", {"InstanceName": "INST-BAD", "WorkflowName": "WF-R5", "actor": "u"})
        body = rpc(client, "instance.update_state", {"InstanceName": "INST-BAD", "InstanceState": "Z", "actor": "u"}, rid=2)
        assert "error" in body

    def test_atomic_rollback_on_replication_failure(self, client, session_factory, monkeypatch) -> None:
        _seed_baseline(client, "WF-R6")
        from mcp_server.src.services import instance_service

        original = instance_service._replicate_rows

        def fail_once(*args, **kwargs):
            raise RuntimeError("forced replication failure")

        monkeypatch.setattr(instance_service, "_replicate_rows", fail_once)
        body = rpc(client, "instance.create", {"InstanceName": "INST-ROLL", "WorkflowName": "WF-R6", "actor": "u"})
        assert "error" in body

        with session_factory() as session:
            inst = session.query(Instance).filter_by(InstanceName="INST-ROLL").all()
            repl = session.query(Role).filter_by(InstanceName="INST-ROLL").all()
        assert len(inst) == 0
        assert len(repl) == 0

        monkeypatch.setattr(instance_service, "_replicate_rows", original)
