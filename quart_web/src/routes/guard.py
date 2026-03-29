"""Guard entity routes."""

from __future__ import annotations

import json
import logging
import time

from quart import Blueprint, current_app, redirect, render_template, request, session
from werkzeug.datastructures import MultiDict

from quart_web.src.forms.guard import GuardForm


guard_bp = Blueprint("guard", __name__)
logger = logging.getLogger("pdfa.quart.guard")


def _require_context():
	if not session.get("user_id"):
		return redirect("/login")
	active_workflow_name = session.get("active_workflow_name")
	if not active_workflow_name:
		return redirect("/dashboard")
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


@guard_bp.get("/guards")
async def list_guards():
	"""Render guard list view for the active workflow."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = session.get("active_workflow_name")
	started = time.perf_counter()

	result = await current_app.mcp_client.call_tool(
		"guard.list",
		{"WorkflowName": active_workflow_name},
	)
	records = result.get("records") if isinstance(result, dict) else []
	if not isinstance(records, list):
		records = []
	_log_event("quart.guard.list.completed", started, "guard.list", record_count=len(records))

	return await render_template(
		"entities/list.html",
		entity_label="Guards",
		entity_path="guards",
		records=records,
		columns=["GuardName", "WorkflowName"],
		id_field="GuardName",
	)


@guard_bp.get("/guards/new")
async def get_guard_create():
	"""Render guard creation form."""
	context = _require_context()
	if context is not None:
		return context
	form = GuardForm(data={"WorkflowName": session.get("active_workflow_name", "")})
	return await render_template(
		"entities/form.html",
		form=form,
		form_title="Create Guard",
		action_url="/guards/new",
		mcp_error="",
	)


@guard_bp.post("/guards/new")
async def post_guard_create():
	"""Submit guard creation via MCP."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	form = GuardForm(MultiDict(await request.form), data={"WorkflowName": active_workflow_name})
	form.WorkflowName.data = active_workflow_name
	if not form.validate():
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Create Guard",
			action_url="/guards/new",
			mcp_error="",
		), 200

	payload = {
		"GuardName": str(form.GuardName.data or "").strip(),
		"WorkflowName": active_workflow_name,
		"GuardDescription": str(form.GuardDescription.data or "").strip(),
		"GuardContextDescription": str(form.GuardContextDescription.data or "").strip(),
		"GuardType": str(form.GuardType.data or "").strip(),
		"GuardConfiguration": str(form.GuardConfiguration.data or "").strip(),
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("guard.create", payload)
	if str(result.get("status", "success")).lower() != "success":
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Create Guard",
			action_url="/guards/new",
			mcp_error=_mcp_error_message(result, "Guard create failed"),
		), 200
	_log_event("quart.guard.create.completed", started, "guard.create", guard_name=payload["GuardName"])
	return redirect("/guards")


@guard_bp.get("/guards/<guard_name>/edit")
async def get_guard_edit(guard_name: str):
	"""Render guard edit form."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"guard.get", {"GuardName": guard_name, "WorkflowName": active_workflow_name}
	)
	record = _extract_record(result)
	_log_event("quart.guard.get.completed", started, "guard.get", guard_name=guard_name)
	form = GuardForm(data=record)
	return await render_template(
		"entities/form.html",
		form=form,
		form_title="Edit Guard",
		action_url=f"/guards/{guard_name}/edit",
		mcp_error="",
	)


@guard_bp.post("/guards/<guard_name>/edit")
async def post_guard_edit(guard_name: str):
	"""Submit guard updates via MCP."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	form = GuardForm(MultiDict(await request.form), data={"WorkflowName": active_workflow_name})
	form.WorkflowName.data = active_workflow_name
	if not form.validate():
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Edit Guard",
			action_url=f"/guards/{guard_name}/edit",
			mcp_error="",
		), 200

	payload = {
		"GuardName": str(form.GuardName.data or guard_name).strip(),
		"WorkflowName": active_workflow_name,
		"GuardDescription": str(form.GuardDescription.data or "").strip(),
		"GuardContextDescription": str(form.GuardContextDescription.data or "").strip(),
		"GuardType": str(form.GuardType.data or "").strip(),
		"GuardConfiguration": str(form.GuardConfiguration.data or "").strip(),
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("guard.update", payload)
	if str(result.get("status", "success")).lower() != "success":
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Edit Guard",
			action_url=f"/guards/{guard_name}/edit",
			mcp_error=_mcp_error_message(result, "Guard update failed"),
		), 200
	_log_event("quart.guard.update.completed", started, "guard.update", guard_name=payload["GuardName"])
	return redirect("/guards")


@guard_bp.get("/guards/<guard_name>/delete")
async def get_guard_delete(guard_name: str):
	"""Render guard delete confirmation page."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"guard.get", {"GuardName": guard_name, "WorkflowName": active_workflow_name}
	)
	record = _extract_record(result)
	_log_event("quart.guard.delete.confirm", started, "guard.get", guard_name=guard_name)
	return await render_template(
		"entities/delete_confirm.html",
		record=record,
		action_url=f"/guards/{guard_name}/delete",
		cancel_url="/guards",
		mcp_error="",
	)


@guard_bp.post("/guards/<guard_name>/delete")
async def post_guard_delete(guard_name: str):
	"""Submit guard delete to MCP and redirect on success."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	payload = {
		"GuardName": guard_name,
		"WorkflowName": active_workflow_name,
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("guard.delete", payload)
	if str(result.get("status", "success")).lower() != "success":
		record = {"GuardName": guard_name, "WorkflowName": active_workflow_name}
		return await render_template(
			"entities/delete_confirm.html",
			record=record,
			action_url=f"/guards/{guard_name}/delete",
			cancel_url="/guards",
			mcp_error=_mcp_error_message(result, "Guard delete failed"),
		), 200
	_log_event("quart.guard.delete.completed", started, "guard.delete", guard_name=guard_name)
	return redirect("/guards")
