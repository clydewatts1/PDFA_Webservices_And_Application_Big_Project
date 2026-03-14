"""JSON-RPC handlers for health and mock authentication tools."""

from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.orm import Session, sessionmaker

from mcp_server.src.api.app import JsonRpcError
from mcp_server.src.services.auth_service import user_logoff, user_logon
from mcp_server.src.services.system_service import get_system_health
from mcp_server.src.services.validation import ValidationError

Handler = Callable[[dict[str, Any]], dict[str, Any]]


def _normalize_system_result(result: dict[str, Any], default_message: str) -> dict[str, Any]:
    """Ensure health/auth handlers always return status and status_message keys."""

    normalized = dict(result)
    normalized.setdefault("status", "SUCCESS")
    normalized.setdefault("status_message", default_message)
    return normalized


def _validation_error_to_rpc(exc: ValidationError) -> JsonRpcError:
    return JsonRpcError(
        code=4002,
        message="ValidationError",
        data={"code": exc.code, "message": str(exc)},
    )


def make_system_handlers(
    session_factory: sessionmaker[Session],
    mock_users: dict[str, str],
) -> dict[str, Handler]:
    """Build health and mock-auth handlers for runtime registration."""

    def _get_system_health(params: dict[str, Any]) -> dict[str, Any]:
        del params
        return _normalize_system_result(get_system_health(session_factory), "Health check completed")

    def _user_logon(params: dict[str, Any]) -> dict[str, Any]:
        try:
            return _normalize_system_result(user_logon(params, mock_users), "Logon handled")
        except ValidationError as exc:
            raise _validation_error_to_rpc(exc) from exc

    def _user_logoff(params: dict[str, Any]) -> dict[str, Any]:
        try:
            return _normalize_system_result(user_logoff(params), "Logoff handled")
        except ValidationError as exc:
            raise _validation_error_to_rpc(exc) from exc

    return {
        "get_system_health": _get_system_health,
        "user_logon": _user_logon,
        "user_logoff": _user_logoff,
    }
