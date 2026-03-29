"""Workflow entity routes."""

from __future__ import annotations

import json
import logging
import time

from quart import Blueprint, current_app, redirect, render_template, request, session
from werkzeug.datastructures import MultiDict

from quart_web.src.forms.workflow import WorkflowForm


workflow_bp = Blueprint("workflow", __name__)
logger = logging.getLogger("pdfa.quart.workflow")


def _require_context():
    if not session.get("user_id"):
        return redirect("/login")
    return None


def _extract_record(result: dict) -> dict:
    record = result.get("record")
    if isinstance(record, dict):
        return record
    records = result.get("records")
    if isinstance(records, list) and records and isinstance(records[0], dict):
        return records[0]
    return {
        key: value
        for key, value in result.items()
        if key not in {"status", "message", "status_message", "ErrorMessage", "code"}
    }


def _mcp_error_message(result: dict, fallback: str) -> str:
    return str(result.get("message") or result.get("status_message") or result.get("ErrorMessage") or fallback)


def _log_event(event: str, started: float, tool_name: str, **extra: object) -> None:
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


@workflow_bp.get("/workflows")
async def list_workflows():
    """Render workflow list view."""
    context = _require_context()
    if context is not None:
        return context

    started = time.perf_counter()
    result = await current_app.mcp_client.call_tool("workflow.list", {})
    records = result.get("records") if isinstance(result, dict) else []
    if not isinstance(records, list):
        records = []
    _log_event("quart.workflow.list.completed", started, "workflow.list", record_count=len(records))

    return await render_template(
        "entities/list.html",
        entity_label="Workflows",
        entity_path="workflows",
        records=records,
        columns=["WorkflowName", "WorkflowDescription"],
        id_field="WorkflowName",
    )


@workflow_bp.get("/workflows/new")
async def get_workflow_create():
    """Render workflow creation form."""
    context = _require_context()
    if context is not None:
        return context
    form = WorkflowForm()
    return await render_template(
        "entities/form.html",
        form=form,
        form_title="Create Workflow",
        action_url="/workflows/new",
        mcp_error="",
    )


@workflow_bp.post("/workflows/new")
async def post_workflow_create():
    """Submit workflow creation via MCP."""
    context = _require_context()
    if context is not None:
        return context
    form = WorkflowForm(MultiDict(await request.form))
    if not form.validate():
        return await render_template(
            "entities/form.html",
            form=form,
            form_title="Create Workflow",
            action_url="/workflows/new",
            mcp_error="",
        ), 200

    payload = {
        "WorkflowName": str(form.WorkflowName.data or "").strip(),
        "WorkflowDescription": str(form.WorkflowDescription.data or "").strip(),
        "WorkflowContextDescription": str(form.WorkflowContextDescription.data or "").strip(),
        "WorkflowStateInd": str(form.WorkflowStateInd.data or "").strip(),
        "actor": str(session.get("user_id")),
    }
    started = time.perf_counter()
    result = await current_app.mcp_client.call_tool("workflow.create", payload)
    if str(result.get("status", "success")).lower() != "success":
        return await render_template(
            "entities/form.html",
            form=form,
            form_title="Create Workflow",
            action_url="/workflows/new",
            mcp_error=_mcp_error_message(result, "Workflow create failed"),
        ), 200
    _log_event("quart.workflow.create.completed", started, "workflow.create", workflow_name=payload["WorkflowName"])
    return redirect("/workflows")


@workflow_bp.get("/workflows/<workflow_name>/edit")
async def get_workflow_edit(workflow_name: str):
    """Render workflow edit form with existing values."""
    context = _require_context()
    if context is not None:
        return context
    started = time.perf_counter()
    result = await current_app.mcp_client.call_tool("workflow.get", {"WorkflowName": workflow_name})
    record = _extract_record(result)
    _log_event("quart.workflow.get.completed", started, "workflow.get", workflow_name=workflow_name)
    form = WorkflowForm(data=record)
    return await render_template(
        "entities/form.html",
        form=form,
        form_title="Edit Workflow",
        action_url=f"/workflows/{workflow_name}/edit",
        mcp_error="",
    )


@workflow_bp.post("/workflows/<workflow_name>/edit")
async def post_workflow_edit(workflow_name: str):
    """Submit workflow updates via MCP."""
    context = _require_context()
    if context is not None:
        return context
    form = WorkflowForm(MultiDict(await request.form))
    if not form.validate():
        return await render_template(
            "entities/form.html",
            form=form,
            form_title="Edit Workflow",
            action_url=f"/workflows/{workflow_name}/edit",
            mcp_error="",
        ), 200

    payload = {
        "WorkflowName": str(form.WorkflowName.data or workflow_name).strip(),
        "WorkflowDescription": str(form.WorkflowDescription.data or "").strip(),
        "WorkflowContextDescription": str(form.WorkflowContextDescription.data or "").strip(),
        "WorkflowStateInd": str(form.WorkflowStateInd.data or "").strip(),
        "actor": str(session.get("user_id")),
    }
    started = time.perf_counter()
    result = await current_app.mcp_client.call_tool("workflow.update", payload)
    if str(result.get("status", "success")).lower() != "success":
        return await render_template(
            "entities/form.html",
            form=form,
            form_title="Edit Workflow",
            action_url=f"/workflows/{workflow_name}/edit",
            mcp_error=_mcp_error_message(result, "Workflow update failed"),
        ), 200
    _log_event("quart.workflow.update.completed", started, "workflow.update", workflow_name=payload["WorkflowName"])
    return redirect("/workflows")


@workflow_bp.get("/workflows/<workflow_name>/delete")
async def get_workflow_delete(workflow_name: str):
    """Render workflow delete confirmation page."""
    context = _require_context()
    if context is not None:
        return context
    started = time.perf_counter()
    result = await current_app.mcp_client.call_tool("workflow.get", {"WorkflowName": workflow_name})
    record = _extract_record(result)
    _log_event("quart.workflow.delete.confirm", started, "workflow.get", workflow_name=workflow_name)
    return await render_template(
        "entities/delete_confirm.html",
        record=record,
        action_url=f"/workflows/{workflow_name}/delete",
        cancel_url="/workflows",
        mcp_error="",
    )


@workflow_bp.post("/workflows/<workflow_name>/delete")
async def post_workflow_delete(workflow_name: str):
    """Submit workflow delete to MCP and redirect to list on success."""
    context = _require_context()
    if context is not None:
        return context
    payload = {"WorkflowName": workflow_name, "actor": str(session.get("user_id"))}
    started = time.perf_counter()
    result = await current_app.mcp_client.call_tool("workflow.delete", payload)
    if str(result.get("status", "success")).lower() != "success":
        record = {"WorkflowName": workflow_name}
        return await render_template(
            "entities/delete_confirm.html",
            record=record,
            action_url=f"/workflows/{workflow_name}/delete",
            cancel_url="/workflows",
            mcp_error=_mcp_error_message(result, "Workflow delete failed"),
        ), 200
    _log_event("quart.workflow.delete.completed", started, "workflow.delete", workflow_name=workflow_name)
    return redirect("/workflows")
