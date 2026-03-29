"""Interaction entity routes."""

from __future__ import annotations

import json
import logging
import time

from quart import Blueprint, current_app, redirect, render_template, request, session
from werkzeug.datastructures import MultiDict

from quart_web.src.forms.interaction import InteractionForm


interaction_bp = Blueprint("interaction", __name__)
logger = logging.getLogger("pdfa.quart.interaction")


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


@interaction_bp.get("/interactions")
async def list_interactions():
	"""Render interaction list view for the active workflow."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = session.get("active_workflow_name")
	started = time.perf_counter()

	result = await current_app.mcp_client.call_tool(
		"interaction.list",
		{"WorkflowName": active_workflow_name},
	)
	records = result.get("records") if isinstance(result, dict) else []
	if not isinstance(records, list):
		records = []
	_log_event("quart.interaction.list.completed", started, "interaction.list", record_count=len(records))

	return await render_template(
		"entities/list.html",
		entity_label="Interactions",
		entity_path="interactions",
		records=records,
		columns=["InteractionName", "WorkflowName"],
		id_field="InteractionName",
	)


@interaction_bp.get("/interactions/new")
async def get_interaction_create():
	"""Render interaction creation form."""
	context = _require_context()
	if context is not None:
		return context
	form = InteractionForm(data={"WorkflowName": session.get("active_workflow_name", "")})
	return await render_template(
		"entities/form.html",
		form=form,
		form_title="Create Interaction",
		action_url="/interactions/new",
		mcp_error="",
	)


@interaction_bp.post("/interactions/new")
async def post_interaction_create():
	"""Submit interaction creation via MCP."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	form = InteractionForm(MultiDict(await request.form), data={"WorkflowName": active_workflow_name})
	form.WorkflowName.data = active_workflow_name
	if not form.validate():
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Create Interaction",
			action_url="/interactions/new",
			mcp_error="",
		), 200

	payload = {
		"InteractionName": str(form.InteractionName.data or "").strip(),
		"WorkflowName": active_workflow_name,
		"InteractionDescription": str(form.InteractionDescription.data or "").strip(),
		"InteractionContextDescription": str(form.InteractionContextDescription.data or "").strip(),
		"InteractionType": str(form.InteractionType.data or "").strip(),
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("interaction.create", payload)
	if str(result.get("status", "success")).lower() != "success":
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Create Interaction",
			action_url="/interactions/new",
			mcp_error=_mcp_error_message(result, "Interaction create failed"),
		), 200
	_log_event("quart.interaction.create.completed", started, "interaction.create", interaction_name=payload["InteractionName"])
	return redirect("/interactions")


@interaction_bp.get("/interactions/<interaction_name>/edit")
async def get_interaction_edit(interaction_name: str):
	"""Render interaction edit form."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"interaction.get", {"InteractionName": interaction_name, "WorkflowName": active_workflow_name}
	)
	record = _extract_record(result)
	_log_event("quart.interaction.get.completed", started, "interaction.get", interaction_name=interaction_name)
	form = InteractionForm(data=record)
	return await render_template(
		"entities/form.html",
		form=form,
		form_title="Edit Interaction",
		action_url=f"/interactions/{interaction_name}/edit",
		mcp_error="",
	)


@interaction_bp.post("/interactions/<interaction_name>/edit")
async def post_interaction_edit(interaction_name: str):
	"""Submit interaction updates via MCP."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	form = InteractionForm(MultiDict(await request.form), data={"WorkflowName": active_workflow_name})
	form.WorkflowName.data = active_workflow_name
	if not form.validate():
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Edit Interaction",
			action_url=f"/interactions/{interaction_name}/edit",
			mcp_error="",
		), 200

	payload = {
		"InteractionName": str(form.InteractionName.data or interaction_name).strip(),
		"WorkflowName": active_workflow_name,
		"InteractionDescription": str(form.InteractionDescription.data or "").strip(),
		"InteractionContextDescription": str(form.InteractionContextDescription.data or "").strip(),
		"InteractionType": str(form.InteractionType.data or "").strip(),
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("interaction.update", payload)
	if str(result.get("status", "success")).lower() != "success":
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Edit Interaction",
			action_url=f"/interactions/{interaction_name}/edit",
			mcp_error=_mcp_error_message(result, "Interaction update failed"),
		), 200
	_log_event("quart.interaction.update.completed", started, "interaction.update", interaction_name=payload["InteractionName"])
	return redirect("/interactions")


@interaction_bp.get("/interactions/<interaction_name>/delete")
async def get_interaction_delete(interaction_name: str):
	"""Render interaction delete confirmation page."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"interaction.get", {"InteractionName": interaction_name, "WorkflowName": active_workflow_name}
	)
	record = _extract_record(result)
	_log_event("quart.interaction.delete.confirm", started, "interaction.get", interaction_name=interaction_name)
	return await render_template(
		"entities/delete_confirm.html",
		record=record,
		action_url=f"/interactions/{interaction_name}/delete",
		cancel_url="/interactions",
		mcp_error="",
	)


@interaction_bp.post("/interactions/<interaction_name>/delete")
async def post_interaction_delete(interaction_name: str):
	"""Submit interaction delete to MCP and redirect on success."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	payload = {
		"InteractionName": interaction_name,
		"WorkflowName": active_workflow_name,
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("interaction.delete", payload)
	if str(result.get("status", "success")).lower() != "success":
		record = {"InteractionName": interaction_name, "WorkflowName": active_workflow_name}
		return await render_template(
			"entities/delete_confirm.html",
			record=record,
			action_url=f"/interactions/{interaction_name}/delete",
			cancel_url="/interactions",
			mcp_error=_mcp_error_message(result, "Interaction delete failed"),
		), 200
	_log_event("quart.interaction.delete.completed", started, "interaction.delete", interaction_name=interaction_name)
	return redirect("/interactions")
