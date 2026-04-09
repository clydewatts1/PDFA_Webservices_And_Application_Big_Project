"""Shared helpers for synchronous Flask CRUD entity routes."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from typing import Any

from flask import Blueprint, current_app, redirect, render_template, session, url_for


logger = logging.getLogger("pdfa.flask.entities")

RequireContext = Callable[[], Any | None]
PayloadBuilder = Callable[[Any, str | None], dict[str, Any]]
ParamBuilder = Callable[[str], dict[str, Any]]


def require_login() -> Any | None:
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return None


def require_workflow_context() -> Any | None:
    redirect_response = require_login()
    if redirect_response is not None:
        return redirect_response
    if not session.get("active_workflow_name"):
        return redirect(url_for("workspace.dashboard"))
    return None


def extract_record(result: dict[str, Any]) -> dict[str, Any]:
    record = result.get("record")
    if isinstance(record, dict):
        return record
    records = result.get("records")
    if isinstance(records, list) and records and isinstance(records[0], dict):
        return records[0]
    return {
        key: value
        for key, value in result.items()
        if key not in {"status", "message", "status_message", "ErrorMessage", "code", "replication"}
    }


def mcp_error_message(result: dict[str, Any], fallback: str) -> str:
    return str(result.get("message") or result.get("status_message") or result.get("ErrorMessage") or fallback)


def log_event(event: str, started: float, tool_name: str, **extra: object) -> None:
    logger.info(
        json.dumps(
            {
                "event": event,
                "tool_name": tool_name,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                "workflow_name": session.get("active_workflow_name"),
                "username": session.get("user_id"),
                **extra,
            }
        )
    )


def build_crud_blueprint(
    *,
    blueprint_name: str,
    entity_label: str,
    entity_path: str,
    id_field: str,
    columns: list[str],
    form_cls: type,
    require_context: RequireContext,
    list_params: Callable[[], dict[str, Any]],
    list_method: str,
    get_method: str,
    create_method: str,
    update_method: str,
    delete_method: str,
    build_create_payload: PayloadBuilder,
    build_update_payload: PayloadBuilder,
    build_get_params: ParamBuilder,
    build_delete_params: ParamBuilder,
) -> Blueprint:
    blueprint = Blueprint(blueprint_name, __name__)
    singular_label = entity_label[:-1] if entity_label.endswith("s") else entity_label

    @blueprint.get(f"/{entity_path}")
    def list_records():
        context = require_context()
        if context is not None:
            return context

        started = time.perf_counter()
        result = current_app.mcp_client.call(list_method, list_params())
        records = result.get("records") if isinstance(result, dict) else []
        if not isinstance(records, list):
            records = []
        log_event(f"flask.{blueprint_name}.list.completed", started, list_method, record_count=len(records))
        return render_template(
            "entities/list.html",
            entity_label=entity_label,
            entity_path=entity_path,
            records=records,
            columns=columns,
            id_field=id_field,
        )

    @blueprint.get(f"/{entity_path}/new")
    def get_create():
        context = require_context()
        if context is not None:
            return context
        form = form_cls(data={"WorkflowName": session.get("active_workflow_name", "")})
        return render_template(
            "entities/form.html",
            form=form,
            form_title=f"Create {singular_label}",
            action_url=f"/{entity_path}/new",
            mcp_error="",
        )

    @blueprint.post(f"/{entity_path}/new")
    def post_create():
        context = require_context()
        if context is not None:
            return context
        form = form_cls()
        if not form.validate_on_submit():
            return (
                render_template(
                    "entities/form.html",
                    form=form,
                    form_title=f"Create {singular_label}",
                    action_url=f"/{entity_path}/new",
                    mcp_error="",
                ),
                200,
            )

        payload = build_create_payload(form, None)
        started = time.perf_counter()
        result = current_app.mcp_client.call(create_method, payload)
        if str(result.get("status", "success")).lower() != "success":
            return (
                render_template(
                    "entities/form.html",
                    form=form,
                    form_title=f"Create {singular_label}",
                    action_url=f"/{entity_path}/new",
                    mcp_error=mcp_error_message(result, f"{singular_label} create failed"),
                ),
                200,
            )
        log_event(f"flask.{blueprint_name}.create.completed", started, create_method, entity_id=payload[id_field])
        return redirect(f"/{entity_path}")

    @blueprint.get(f"/{entity_path}/<entity_id>/edit")
    def get_edit(entity_id: str):
        context = require_context()
        if context is not None:
            return context
        started = time.perf_counter()
        result = current_app.mcp_client.call(get_method, build_get_params(entity_id))
        record = extract_record(result)
        log_event(f"flask.{blueprint_name}.get.completed", started, get_method, entity_id=entity_id)
        form = form_cls(data=record)
        return render_template(
            "entities/form.html",
            form=form,
            form_title=f"Edit {singular_label}",
            action_url=f"/{entity_path}/{entity_id}/edit",
            mcp_error="",
        )

    @blueprint.post(f"/{entity_path}/<entity_id>/edit")
    def post_edit(entity_id: str):
        context = require_context()
        if context is not None:
            return context
        form = form_cls()
        if not form.validate_on_submit():
            return (
                render_template(
                    "entities/form.html",
                    form=form,
                    form_title=f"Edit {singular_label}",
                    action_url=f"/{entity_path}/{entity_id}/edit",
                    mcp_error="",
                ),
                200,
            )

        payload = build_update_payload(form, entity_id)
        started = time.perf_counter()
        result = current_app.mcp_client.call(update_method, payload)
        if str(result.get("status", "success")).lower() != "success":
            return (
                render_template(
                    "entities/form.html",
                    form=form,
                    form_title=f"Edit {singular_label}",
                    action_url=f"/{entity_path}/{entity_id}/edit",
                    mcp_error=mcp_error_message(result, f"{singular_label} update failed"),
                ),
                200,
            )
        log_event(f"flask.{blueprint_name}.update.completed", started, update_method, entity_id=payload[id_field])
        return redirect(f"/{entity_path}")

    @blueprint.get(f"/{entity_path}/<entity_id>/delete")
    def get_delete(entity_id: str):
        context = require_context()
        if context is not None:
            return context
        started = time.perf_counter()
        result = current_app.mcp_client.call(get_method, build_get_params(entity_id))
        record = extract_record(result)
        log_event(f"flask.{blueprint_name}.delete.confirm", started, get_method, entity_id=entity_id)
        return render_template(
            "entities/delete_confirm.html",
            record=record,
            action_url=f"/{entity_path}/{entity_id}/delete",
            cancel_url=f"/{entity_path}",
            mcp_error="",
            form=None,
        )

    @blueprint.post(f"/{entity_path}/<entity_id>/delete")
    def post_delete(entity_id: str):
        context = require_context()
        if context is not None:
            return context
        started = time.perf_counter()
        result = current_app.mcp_client.call(delete_method, build_delete_params(entity_id))
        if str(result.get("status", "success")).lower() != "success":
            record = {id_field: entity_id, "WorkflowName": session.get("active_workflow_name")}
            return (
                render_template(
                    "entities/delete_confirm.html",
                    record=record,
                    action_url=f"/{entity_path}/{entity_id}/delete",
                    cancel_url=f"/{entity_path}",
                    mcp_error=mcp_error_message(result, f"{singular_label} delete failed"),
                    form=None,
                ),
                200,
            )
        log_event(f"flask.{blueprint_name}.delete.completed", started, delete_method, entity_id=entity_id)
        return redirect(f"/{entity_path}")

    return blueprint