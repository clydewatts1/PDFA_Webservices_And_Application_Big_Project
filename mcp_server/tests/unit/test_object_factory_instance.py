from __future__ import annotations

from datetime import UTC, datetime

import pytest

from mcp_server.src.lib.object_factory import ObjectFactory
from mcp_server.src.services.validation import ValidationError


def _factory() -> ObjectFactory:
	return ObjectFactory("instance_test_actor")


class TestBuildInstance:
	def test_build_instance_defaults(self) -> None:
		row = _factory().build_instance("inst-1", "wf-1")
		assert row["InstanceName"] == "inst-1"
		assert row["WorkflowName"] == "wf-1"
		assert row["InstanceState"] == "A"
		assert row["DeleteInd"] == 0

	def test_build_instance_custom_state(self) -> None:
		row = _factory().build_instance("inst-2", "wf-1", state="P")
		assert row["InstanceState"] == "P"

	def test_build_instance_invalid_state_raises(self) -> None:
		with pytest.raises(ValidationError) as exc:
			_factory().build_instance("inst-3", "wf-1", state="Z")
		assert exc.value.code == "invalid_instance_state"


class TestInstanceStateTransitions:
	def test_transition_active_to_paused_sets_state_date(self) -> None:
		current = _factory().build_instance("inst-4", "wf-1", state="A")
		next_row = _factory().transition_instance_state(current, "P")
		assert next_row["InstanceState"] == "P"
		assert isinstance(next_row["InstanceStateDate"], datetime)

	def test_transition_to_inactive_sets_end_date(self) -> None:
		current = _factory().build_instance("inst-5", "wf-1", state="A")
		next_row = _factory().transition_instance_state(current, "I")
		assert next_row["InstanceState"] == "I"
		assert isinstance(next_row["InstanceEndDate"], datetime)

	def test_transition_to_paused_sets_end_date(self) -> None:
		current = _factory().build_instance("inst-6", "wf-1", state="A")
		next_row = _factory().transition_instance_state(current, "P")
		assert isinstance(next_row["InstanceEndDate"], datetime)

	def test_transition_to_active_preserves_end_date(self) -> None:
		current = _factory().build_instance("inst-7", "wf-1", state="P")
		current["InstanceEndDate"] = datetime.now(UTC).replace(tzinfo=None)
		next_row = _factory().transition_instance_state(current, "A")
		assert next_row["InstanceState"] == "A"
		assert next_row["InstanceEndDate"] == current["InstanceEndDate"]

	def test_transition_invalid_state_raises(self) -> None:
		current = _factory().build_instance("inst-8", "wf-1", state="A")
		with pytest.raises(ValidationError) as exc:
			_factory().transition_instance_state(current, "X")
		assert exc.value.code == "invalid_instance_state"
