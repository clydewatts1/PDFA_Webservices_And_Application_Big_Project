"""Unit tests for ObjectFactory build methods for dependent entities — T018."""
from __future__ import annotations

from datetime import datetime

import pytest

from mcp_server.src.lib.object_factory import ObjectFactory
from mcp_server.src.models.base import HIGH_DATE


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _factory() -> ObjectFactory:
    return ObjectFactory("unit_test_actor")


def _assert_control_columns(result: dict) -> None:
    assert result["DeleteInd"] == 0
    assert result["EffToDateTime"] == HIGH_DATE
    assert isinstance(result["EffFromDateTime"], datetime)
    assert result["InsertUserName"] == "unit_test_actor"
    assert result["UpdateUserName"] == "unit_test_actor"


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------

class TestBuildRole:
    def test_minimal_required_fields(self) -> None:
        r = _factory().build_role("Reviewer", "ApprovalWF")
        assert r["RoleName"] == "Reviewer"
        assert r["WorkflowName"] == "ApprovalWF"

    def test_all_optional_fields_propagated(self) -> None:
        r = _factory().build_role(
            "Approver", "ApprovalWF",
            description="Approver desc",
            context_description="ctx",
            configuration='{"level": 1}',
            configuration_description="cfg desc",
            configuration_context_description="cfg ctx",
        )
        assert r["RoleDescription"] == "Approver desc"
        assert r["RoleContextDescription"] == "ctx"
        assert r["RoleConfiguration"] == '{"level": 1}'
        assert r["RoleConfigurationDescription"] == "cfg desc"
        assert r["RoleConfigurationContextDescription"] == "cfg ctx"

    def test_control_columns_present(self) -> None:
        _assert_control_columns(_factory().build_role("R", "W"))

    def test_optional_fields_default_to_none(self) -> None:
        r = _factory().build_role("R", "W")
        assert r["RoleDescription"] is None
        assert r["RoleConfiguration"] is None


# ---------------------------------------------------------------------------
# Interaction
# ---------------------------------------------------------------------------

class TestBuildInteraction:
    def test_required_fields(self) -> None:
        r = _factory().build_interaction("SubmitStep", "OrderWF")
        assert r["InteractionName"] == "SubmitStep"
        assert r["WorkflowName"] == "OrderWF"

    def test_interaction_type_propagated(self) -> None:
        r = _factory().build_interaction("Click", "WF", interaction_type="UI")
        assert r["InteractionType"] == "UI"

    def test_interaction_type_defaults_to_none(self) -> None:
        r = _factory().build_interaction("Click", "WF")
        assert r["InteractionType"] is None

    def test_control_columns_present(self) -> None:
        _assert_control_columns(_factory().build_interaction("I", "W"))


# ---------------------------------------------------------------------------
# Guard
# ---------------------------------------------------------------------------

class TestBuildGuard:
    def test_required_fields(self) -> None:
        r = _factory().build_guard("AgeCheck", "KYC_WF")
        assert r["GuardName"] == "AgeCheck"
        assert r["WorkflowName"] == "KYC_WF"

    def test_guard_type_and_config_propagated(self) -> None:
        r = _factory().build_guard(
            "LimitCheck", "PaymentWF",
            guard_type="AMOUNT",
            configuration='{"max": 1000}',
        )
        assert r["GuardType"] == "AMOUNT"
        assert r["GuardConfiguration"] == '{"max": 1000}'

    def test_control_columns_present(self) -> None:
        _assert_control_columns(_factory().build_guard("G", "W"))


# ---------------------------------------------------------------------------
# InteractionComponent
# ---------------------------------------------------------------------------

class TestBuildInteractionComponent:
    def test_required_fields(self) -> None:
        r = _factory().build_interaction_component("Link1", "FlowWF")
        assert r["InteractionComponentName"] == "Link1"
        assert r["WorkflowName"] == "FlowWF"

    def test_source_and_target_propagated(self) -> None:
        r = _factory().build_interaction_component(
            "Edge1", "FlowWF", source_name="NodeA", target_name="NodeB"
        )
        assert r["SourceName"] == "NodeA"
        assert r["TargetName"] == "NodeB"

    def test_relationship_propagated(self) -> None:
        r = _factory().build_interaction_component("Edge2", "FlowWF", relationship="TRIGGERS")
        assert r["InteractionComponentRelationShip"] == "TRIGGERS"

    def test_control_columns_present(self) -> None:
        _assert_control_columns(_factory().build_interaction_component("C", "W"))


# ---------------------------------------------------------------------------
# UnitOfWork
# ---------------------------------------------------------------------------

class TestBuildUnitOfWork:
    def test_required_id_field(self) -> None:
        r = _factory().build_unit_of_work("UOW-001")
        assert r["UnitOfWorkID"] == "UOW-001"

    def test_type_and_payload_propagated(self) -> None:
        r = _factory().build_unit_of_work("UOW-002", unit_type="HTTP", payload='{"url":"http://x"}')
        assert r["UnitOfWorkType"] == "HTTP"
        assert r["UnitOfWorkPayLoad"] == '{"url":"http://x"}'

    def test_no_workflow_name_in_result(self) -> None:
        r = _factory().build_unit_of_work("UOW-003")
        assert "WorkflowName" not in r

    def test_control_columns_present(self) -> None:
        _assert_control_columns(_factory().build_unit_of_work("UOW-004"))

    def test_type_and_payload_default_to_none(self) -> None:
        r = _factory().build_unit_of_work("UOW-005")
        assert r["UnitOfWorkType"] is None
        assert r["UnitOfWorkPayLoad"] is None
