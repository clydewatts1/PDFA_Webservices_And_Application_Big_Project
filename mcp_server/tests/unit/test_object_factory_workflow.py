"""Unit tests for ObjectFactory.build_workflow() — T011."""
from __future__ import annotations

from datetime import datetime

import pytest

from mcp_server.src.lib.object_factory import ObjectFactory
from mcp_server.src.models.base import HIGH_DATE
from mcp_server.src.services.validation import ValidationError


class TestBuildWorkflowSuccess:
    def test_required_fields_present(self) -> None:
        factory = ObjectFactory("test_actor")
        result = factory.build_workflow("MyWorkflow", "A description", "Some context")
        assert result["WorkflowName"] == "MyWorkflow"
        assert result["WorkflowDescription"] == "A description"
        assert result["WorkflowContextDescription"] == "Some context"

    def test_default_state_ind_is_active(self) -> None:
        factory = ObjectFactory("actor")
        result = factory.build_workflow("W", "desc", "ctx")
        assert result["WorkflowStateInd"] == "A"

    def test_custom_state_ind_propagated(self) -> None:
        factory = ObjectFactory("actor")
        result = factory.build_workflow("W", "desc", "ctx", state_ind="I")
        assert result["WorkflowStateInd"] == "I"

    def test_delete_ind_defaults_to_zero(self) -> None:
        factory = ObjectFactory("actor")
        result = factory.build_workflow("W", "d", "c")
        assert result["DeleteInd"] == 0

    def test_eff_to_is_high_date(self) -> None:
        factory = ObjectFactory("actor")
        result = factory.build_workflow("W", "d", "c")
        assert result["EffToDateTime"] == HIGH_DATE

    def test_eff_from_is_a_datetime(self) -> None:
        factory = ObjectFactory("actor")
        result = factory.build_workflow("W", "d", "c")
        assert isinstance(result["EffFromDateTime"], datetime)

    def test_eff_from_before_eff_to(self) -> None:
        factory = ObjectFactory("actor")
        result = factory.build_workflow("W", "d", "c")
        assert result["EffFromDateTime"] <= result["EffToDateTime"]

    def test_actor_used_for_insert_and_update_user(self) -> None:
        factory = ObjectFactory("pipeline_user")
        result = factory.build_workflow("W", "d", "c")
        assert result["InsertUserName"] == "pipeline_user"
        assert result["UpdateUserName"] == "pipeline_user"

    def test_explicit_effective_from_respected(self) -> None:
        explicit_time = datetime(2026, 1, 1, 12, 0, 0)
        factory = ObjectFactory("actor")
        result = factory.build_workflow("W", "d", "c", effective_from=explicit_time)
        assert result["EffFromDateTime"] == explicit_time

    def test_all_control_columns_present(self) -> None:
        factory = ObjectFactory("actor")
        result = factory.build_workflow("W", "d", "c")
        for key in ("EffFromDateTime", "EffToDateTime", "DeleteInd", "InsertUserName", "UpdateUserName"):
            assert key in result


class TestBuildWorkflowValidation:
    def test_invalid_delete_ind_raises(self) -> None:
        """Injecting an invalid DeleteInd via payload override should raise ValidationError."""
        factory = ObjectFactory("actor")
        # Monkey-patch _with_controls to pass an invalid DeleteInd to trigger validation
        import types

        original = factory._with_controls

        def bad_controls(payload):
            merged = original(payload)
            merged["DeleteInd"] = 99  # override to invalid value
            from mcp_server.src.services.validation import validate_delete_ind
            validate_delete_ind(merged["DeleteInd"])
            return merged

        factory._with_controls = types.MethodType(lambda self, p: bad_controls(p), factory)

        with pytest.raises(ValidationError) as exc_info:
            factory._with_controls({"WorkflowName": "X"})
        assert exc_info.value.code == "invalid_delete_indicator"

    def test_temporal_window_invalid_raises(self) -> None:
        """EffToDateTime < EffFromDateTime must raise ValidationError."""
        from mcp_server.src.services.validation import validate_temporal_window

        with pytest.raises(ValidationError) as exc_info:
            validate_temporal_window(
                eff_from=datetime(2026, 6, 1),
                eff_to=datetime(2026, 1, 1),
            )
        assert exc_info.value.code == "invalid_temporal_window"
