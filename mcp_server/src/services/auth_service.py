"""Mock authentication service backed by YAML-defined in-memory users."""

from __future__ import annotations

from typing import Any

from mcp_server.src.lib.tool_result import success_result
from mcp_server.src.services.validation import ValidationError


def _required_string(params: dict[str, Any], field: str) -> str:
    value = params.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} is required", code="missing_required_field")
    return value.strip()


def user_logon(params: dict[str, Any], mock_users: dict[str, str]) -> dict[str, Any]:
    """Validate username/password against configured mock users."""

    username = _required_string(params, "username")
    password = _required_string(params, "password")

    expected_password = mock_users.get(username)
    if expected_password is None or expected_password != password:
        return {
            "status": "DENIED",
            "status_message": "Invalid username or password",
            "ErrorMessage": "Credentials denied",
            "username": username,
        }

    return success_result(
        status_message="Logon successful",
        payload={"username": username, "ErrorMessage": ""},
    )


def user_logoff(params: dict[str, Any]) -> dict[str, Any]:
    """Return mock logoff status for provided username."""

    username = _required_string(params, "username")
    return success_result(
        status_message="Logoff successful",
        payload={"username": username, "ErrorMessage": ""},
    )
