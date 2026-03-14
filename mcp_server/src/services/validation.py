"""Validation helpers for temporal and domain-state invariants."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from mcp_server.src.lib.mcp_config import REQUIRED_TOOL_NAMES, get_required_tool_names, get_transport_contract

HIGH_DATE_LITERAL = datetime(9999, 1, 1, 0, 0, 0)


class ValidationError(ValueError):
    """Domain validation exception carrying a stable machine-readable code."""

    def __init__(self, message: str, *, code: str = "validation_error") -> None:
        super().__init__(message)
        self.code = code


def validate_temporal_window(eff_from: datetime, eff_to: datetime) -> None:
    """Validate that the temporal window end is not earlier than start."""

    if eff_to < eff_from:
        raise ValidationError("EffToDateTime must be greater than or equal to EffFromDateTime", code="invalid_temporal_window")


def validate_delete_ind(delete_ind: int) -> None:
    """Validate logical-delete indicator domain values."""

    if delete_ind not in (0, 1):
        raise ValidationError("DeleteInd must be 0 (active) or 1 (deleted)", code="invalid_delete_indicator")


def validate_instance_state(instance_state: str) -> None:
    """Validate allowed instance lifecycle state values."""

    if instance_state not in ("A", "I", "P"):
        raise ValidationError("InstanceState must be one of A, I, P", code="invalid_instance_state")


def is_active_row(delete_ind: int, eff_to: datetime) -> bool:
    """Return True when row values match active-row semantics."""

    return delete_ind == 0 and eff_to == HIGH_DATE_LITERAL


def validate_mcp_config(config: dict[str, object]) -> None:
    """Validate required MCP runtime configuration sections."""

    server_name = config.get("server_name")
    if not isinstance(server_name, str) or not server_name.strip():
        raise ValidationError("server_name is required in MCP configuration", code="missing_server_name")

    tools = config.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ValidationError("tools list is required in MCP configuration", code="missing_tools")

    mock_users = config.get("mock_users")
    if not isinstance(mock_users, dict) or not mock_users:
        raise ValidationError("mock_users map is required in MCP configuration", code="missing_mock_users")


def validate_transport_compatibility(config: dict[str, Any]) -> None:
    """Validate transport contract expectations required by milestone spec."""

    contract = get_transport_contract(config)
    if contract["http_rpc_endpoint"] != "/rpc":
        raise ValidationError("HTTP JSON-RPC endpoint must be /rpc", code="invalid_rpc_endpoint")
    if contract["sse_endpoint"] != "/sse":
        raise ValidationError("SSE endpoint must be /sse", code="invalid_sse_endpoint")

    configured_tools = get_required_tool_names(config)
    missing_tools = sorted(REQUIRED_TOOL_NAMES - configured_tools)
    if missing_tools:
        raise ValidationError(
            f"Required MCP tools missing from config: {', '.join(missing_tools)}",
            code="missing_required_tools",
        )
