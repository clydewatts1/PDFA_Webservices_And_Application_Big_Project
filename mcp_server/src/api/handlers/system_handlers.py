"""JSON-RPC handlers for health and mock authentication tools."""

from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.orm import Session, sessionmaker

from mcp_server.src.api.app import JsonRpcError
from mcp_server.src.services.auth_service import user_logoff, user_logon
from mcp_server.src.services.system_service import get_system_health
from mcp_server.src.services.validation import ValidationError

Handler = Callable[[dict[str, Any]], dict[str, Any]]


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
        return get_system_health(session_factory)

    def _user_logon(params: dict[str, Any]) -> dict[str, Any]:
        try:
            return user_logon(params, mock_users)
        except ValidationError as exc:
            raise _validation_error_to_rpc(exc) from exc

    def _user_logoff(params: dict[str, Any]) -> dict[str, Any]:
        try:
            return user_logoff(params)
        except ValidationError as exc:
            raise _validation_error_to_rpc(exc) from exc

    return {
        "get_system_health": _get_system_health,
        "user_logon": _user_logon,
        "user_logoff": _user_logoff,
    }
