"""MCP JSON-RPC handlers for Workflow CRUD — T016.

Usage::

    from mcp_server.src.api.handlers.workflow_handlers import make_workflow_handlers

    for method, handler in make_workflow_handlers(session_factory).items():
        app.register_jsonrpc_handler(method, handler)
"""
from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.app import JsonRpcError
from mcp_server.src.lib.tool_result import attach_success_metadata
from mcp_server.src.services.workflow_service import (
    ServiceError,
    MissingFieldError,
    create_workflow,
    delete_workflow,
    get_workflow,
    list_workflows,
    update_workflow,
)

Handler = Callable[[dict[str, Any]], dict[str, Any]]


def _normalize_crud_result(payload: dict[str, Any], status_message: str) -> dict[str, Any]:
    """Attach normalized CRUD result semantics across transport handlers."""

    return attach_success_metadata(payload, status_message=status_message)


def _extract_actor(params: dict[str, Any]) -> str:
    actor = params.get("actor")
    if not actor:
        raise JsonRpcError(code=4002, message="ValidationError", data={"code": "missing_required_field", "field": "actor"})
    return actor


def _service_error_to_rpc(exc: ServiceError) -> JsonRpcError:
    """Convert a domain ServiceError to the appropriate JSON-RPC error code."""
    http_code_map = {
        "duplicate_active_key": 4009,     # Conflict
        "workflow_not_found": 4044,         # Not found
        "missing_required_field": 4002,   # Bad request
        "invalid_pagination": 4002,
    }
    rpc_code = http_code_map.get(exc.code, 5000)
    return JsonRpcError(code=rpc_code, message="ServiceError", data={"code": exc.code, "message": str(exc)})


def make_workflow_handlers(session_factory: sessionmaker) -> dict[str, Handler]:
    """Return a mapping of JSON-RPC method names to handler callables.

    Each handler receives the *params* dict from the JSON-RPC request.
    The session is opened and closed within each handler call.
    """

    def _workflow_create(params: dict[str, Any]) -> dict[str, Any]:
        actor = _extract_actor(params)
        try:
            with session_factory() as session:
                return _normalize_crud_result(create_workflow(session, params, actor), "workflow.create completed")
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    def _workflow_update(params: dict[str, Any]) -> dict[str, Any]:
        actor = _extract_actor(params)
        try:
            with session_factory() as session:
                return _normalize_crud_result(update_workflow(session, params, actor), "workflow.update completed")
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    def _workflow_get(params: dict[str, Any]) -> dict[str, Any]:
        workflow_name = params.get("WorkflowName")
        if not workflow_name:
            raise JsonRpcError(code=4002, message="ValidationError", data={"code": "missing_required_field", "field": "WorkflowName"})
        try:
            with session_factory() as session:
                return _normalize_crud_result(get_workflow(session, workflow_name), "workflow.get completed")
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    def _workflow_list(params: dict[str, Any]) -> dict[str, Any]:
        limit = params.get("limit")
        offset = params.get("offset")
        try:
            with session_factory() as session:
                return _normalize_crud_result(
                    {"workflows": list_workflows(session, limit=limit, offset=offset)},
                    "workflow.list completed",
                )
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    def _workflow_delete(params: dict[str, Any]) -> dict[str, Any]:
        actor = _extract_actor(params)
        workflow_name = params.get("WorkflowName")
        if not workflow_name:
            raise JsonRpcError(code=4002, message="ValidationError", data={"code": "missing_required_field", "field": "WorkflowName"})
        try:
            with session_factory() as session:
                return _normalize_crud_result(delete_workflow(session, workflow_name, actor), "workflow.delete completed")
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    return {
        "workflow.create": _workflow_create,
        "workflow.update": _workflow_update,
        "workflow.get": _workflow_get,
        "workflow.list": _workflow_list,
        "workflow.delete": _workflow_delete,
    }
