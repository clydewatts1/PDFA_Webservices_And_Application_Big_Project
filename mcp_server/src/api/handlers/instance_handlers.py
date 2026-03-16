"""JSON-RPC handlers for instance lifecycle operations."""

from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.errors import JsonRpcError
from mcp_server.src.services.instance_service import (
    InstanceNotFoundError,
    create_instance,
    get_instance,
    list_instances,
    update_instance_state,
)
from mcp_server.src.services.validation import ValidationError
from mcp_server.src.services.workflow_service import ServiceError

Handler = Callable[[dict[str, Any]], dict[str, Any]]


def _extract_actor(params: dict[str, Any]) -> str:
    """Extract the required actor field from JSON-RPC params."""

    actor = params.get("actor")
    if not actor:
        raise JsonRpcError(code=-32602, message="Invalid params", data={"reason": "missing_required_field", "field": "actor"})
    return actor


def _service_error_to_rpc(exc: Exception) -> JsonRpcError:
    """Map service and validation exceptions to JSON-RPC errors."""

    if isinstance(exc, ValidationError):
        return JsonRpcError(code=-32602, message="Invalid params", data={"reason": exc.code, "code": exc.code, "message": str(exc)})
    if isinstance(exc, ServiceError):
        code_map = {
            "duplicate_active_key": 4009,
            "workflow_not_found": 4044,
            "instance_not_found": 4044,
            "missing_required_field": -32602,
        }
        return JsonRpcError(code=code_map.get(exc.code, 5000), message="ServiceError", data={"code": exc.code, "message": str(exc)})
    return JsonRpcError(code=5000, message="Internal error", data={"reason": str(exc)})


def make_instance_handlers(session_factory: sessionmaker) -> dict[str, Handler]:
    """Build instance method handlers for JSON-RPC registration."""

    def _create(params: dict[str, Any]) -> dict[str, Any]:
        """Handle instance.create calls."""

        actor = _extract_actor(params)
        try:
            with session_factory() as session:
                return create_instance(session, params, actor)
        except Exception as exc:
            raise _service_error_to_rpc(exc) from exc

    def _update_state(params: dict[str, Any]) -> dict[str, Any]:
        """Handle instance.update_state calls."""

        actor = _extract_actor(params)
        try:
            with session_factory() as session:
                return update_instance_state(session, params, actor)
        except Exception as exc:
            raise _service_error_to_rpc(exc) from exc

    def _get(params: dict[str, Any]) -> dict[str, Any]:
        """Handle instance.get calls."""

        name = params.get("InstanceName")
        if not name:
            raise JsonRpcError(code=-32602, message="Invalid params", data={"reason": "missing_required_field", "field": "InstanceName"})
        try:
            with session_factory() as session:
                return get_instance(session, name)
        except Exception as exc:
            raise _service_error_to_rpc(exc) from exc

    def _list(params: dict[str, Any]) -> dict[str, Any]:
        """Handle instance.list calls."""

        try:
            with session_factory() as session:
                return {"instances": list_instances(session, params.get("WorkflowName"))}
        except Exception as exc:
            raise _service_error_to_rpc(exc) from exc

    return {
        "instance.create": _create,
        "instance.update_state": _update_state,
        "instance.get": _get,
        "instance.list": _list,
    }
