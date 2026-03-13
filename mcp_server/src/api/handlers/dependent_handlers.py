"""MCP JSON-RPC handlers for all dependent entity CRUD operations — T023.

Usage::

    from mcp_server.src.api.handlers.dependent_handlers import make_all_dependent_handlers

    for method, handler in make_all_dependent_handlers(session_factory).items():
        app.register_jsonrpc_handler(method, handler)
"""
from __future__ import annotations

from typing import Any, Callable

from sqlalchemy.orm import sessionmaker

from mcp_server.src.api.app import JsonRpcError
from mcp_server.src.services.dependent_service import (
    GUARD_CONFIG,
    INTERACTION_COMPONENT_CONFIG,
    INTERACTION_CONFIG,
    ROLE_CONFIG,
    UNIT_OF_WORK_CONFIG,
    EntityConfig,
    EntityNotFoundError,
    InvalidWorkflowReferenceError,
    create_entity,
    delete_entity,
    get_entity,
    list_entities,
    update_entity,
)
from mcp_server.src.services.workflow_service import (
    DuplicateKeyError,
    MissingFieldError,
    ServiceError,
)

Handler = Callable[[dict[str, Any]], dict[str, Any]]


def _extract_actor(params: dict[str, Any]) -> str:
    actor = params.get("actor")
    if not actor:
        raise JsonRpcError(
            code=4002,
            message="ValidationError",
            data={"code": "missing_required_field", "field": "actor"},
        )
    return actor


def _service_error_to_rpc(exc: ServiceError) -> JsonRpcError:
    code_map = {
        "duplicate_active_key": 4009,
        "entity_not_found": 4044,
        "invalid_workflow_reference": 4022,
        "missing_required_field": 4002,
    }
    rpc_code = code_map.get(exc.code, 5000)
    return JsonRpcError(
        code=rpc_code,
        message="ServiceError",
        data={"code": exc.code, "message": str(exc)},
    )


def make_entity_handlers(
    session_factory: sessionmaker,
    config: EntityConfig,
    prefix: str,
) -> dict[str, Handler]:
    """Build the 5 standard JSON-RPC handlers for *config* under *prefix*.

    Methods registered: ``{prefix}.create``, ``.update``, ``.get``, ``.list``, ``.delete``.
    """

    def _create(params: dict[str, Any]) -> dict[str, Any]:
        actor = _extract_actor(params)
        try:
            with session_factory() as session:
                return create_entity(session, config, params, actor)
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    def _update(params: dict[str, Any]) -> dict[str, Any]:
        actor = _extract_actor(params)
        try:
            with session_factory() as session:
                return update_entity(session, config, params, actor)
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    def _get(params: dict[str, Any]) -> dict[str, Any]:
        bk: dict[str, Any] = {}
        for k in config.business_keys:
            v = params.get(k)
            if not v:
                raise JsonRpcError(
                    code=4002,
                    message="ValidationError",
                    data={"code": "missing_required_field", "field": k},
                )
            bk[k] = v
        try:
            with session_factory() as session:
                return get_entity(session, config, bk)
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    def _list(params: dict[str, Any]) -> dict[str, Any]:
        filters: dict[str, Any] | None = None
        if config.requires_workflow_fk and params.get("WorkflowName"):
            filters = {"WorkflowName": params["WorkflowName"]}
        with session_factory() as session:
            return {f"{prefix}s": list_entities(session, config, filters)}

    def _delete(params: dict[str, Any]) -> dict[str, Any]:
        actor = _extract_actor(params)
        bk: dict[str, Any] = {}
        for k in config.business_keys:
            v = params.get(k)
            if not v:
                raise JsonRpcError(
                    code=4002,
                    message="ValidationError",
                    data={"code": "missing_required_field", "field": k},
                )
            bk[k] = v
        try:
            with session_factory() as session:
                return delete_entity(session, config, bk, actor)
        except ServiceError as exc:
            raise _service_error_to_rpc(exc) from exc

    return {
        f"{prefix}.create": _create,
        f"{prefix}.update": _update,
        f"{prefix}.get": _get,
        f"{prefix}.list": _list,
        f"{prefix}.delete": _delete,
    }


def make_all_dependent_handlers(session_factory: sessionmaker) -> dict[str, Handler]:
    """Return a combined handler map for all 5 dependent entity types."""
    result: dict[str, Handler] = {}
    for prefix, config in [
        ("role", ROLE_CONFIG),
        ("interaction", INTERACTION_CONFIG),
        ("guard", GUARD_CONFIG),
        ("interaction_component", INTERACTION_COMPONENT_CONFIG),
        ("unit_of_work", UNIT_OF_WORK_CONFIG),
    ]:
        result.update(make_entity_handlers(session_factory, config, prefix))
    return result
