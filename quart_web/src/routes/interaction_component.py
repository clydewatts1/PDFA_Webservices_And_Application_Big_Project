"""InteractionComponent entity routes."""

from __future__ import annotations

import json
import logging
import time

from quart import Blueprint, current_app, redirect, render_template, request, session
from werkzeug.datastructures import MultiDict

from quart_web.src.forms.interaction_component import InteractionComponentForm


interaction_component_bp = Blueprint("interaction_component", __name__)
logger = logging.getLogger("pdfa.quart.interaction_component")


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


@interaction_component_bp.get("/interaction-components")
async def list_interaction_components():
	"""Render interaction component list view for the active workflow."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = session.get("active_workflow_name")
	started = time.perf_counter()

	result = await current_app.mcp_client.call_tool(
		"interaction_component.list",
		{"WorkflowName": active_workflow_name},
	)
	records = result.get("records") if isinstance(result, dict) else []
	if not isinstance(records, list):
		records = []
	_log_event(
		"quart.interaction_component.list.completed",
		started,
		"interaction_component.list",
		record_count=len(records),
	)

	return await render_template(
		"entities/list.html",
		entity_label="Interaction Components",
		entity_path="interaction-components",
		records=records,
		columns=["InteractionComponentName", "WorkflowName"],
		id_field="InteractionComponentName",
	)


@interaction_component_bp.get("/interaction-components/new")
async def get_interaction_component_create():
	"""Render interaction component creation form."""
	context = _require_context()
	if context is not None:
		return context
	form = InteractionComponentForm(data={"WorkflowName": session.get("active_workflow_name", "")})
	return await render_template(
		"entities/form.html",
		form=form,
		form_title="Create Interaction Component",
		action_url="/interaction-components/new",
		mcp_error="",
	)


@interaction_component_bp.post("/interaction-components/new")
async def post_interaction_component_create():
	"""Submit interaction component creation via MCP."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	form = InteractionComponentForm(MultiDict(await request.form), data={"WorkflowName": active_workflow_name})
	form.WorkflowName.data = active_workflow_name
	if not form.validate():
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Create Interaction Component",
			action_url="/interaction-components/new",
			mcp_error="",
		), 200

	payload = {
		"InteractionComponentName": str(form.InteractionComponentName.data or "").strip(),
		"WorkflowName": active_workflow_name,
		"InteractionComponentRelationShip": str(form.InteractionComponentRelationShip.data or "").strip(),
		"InteractionComponentDescription": str(form.InteractionComponentDescription.data or "").strip(),
		"InteractionComponentContextDescription": str(
			form.InteractionComponentContextDescription.data or ""
		).strip(),
		"SourceName": str(form.SourceName.data or "").strip(),
		"TargetName": str(form.TargetName.data or "").strip(),
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("interaction_component.create", payload)
	if str(result.get("status", "success")).lower() != "success":
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Create Interaction Component",
			action_url="/interaction-components/new",
			mcp_error=_mcp_error_message(result, "Interaction component create failed"),
		), 200
	_log_event(
		"quart.interaction_component.create.completed",
		started,
		"interaction_component.create",
		component_name=payload["InteractionComponentName"],
	)
	return redirect("/interaction-components")


@interaction_component_bp.get("/interaction-components/<component_name>/edit")
async def get_interaction_component_edit(component_name: str):
	"""Render interaction component edit form."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"interaction_component.get",
		{"InteractionComponentName": component_name, "WorkflowName": active_workflow_name},
	)
	record = _extract_record(result)
	_log_event(
		"quart.interaction_component.get.completed",
		started,
		"interaction_component.get",
		component_name=component_name,
	)
	form = InteractionComponentForm(data=record)
	return await render_template(
		"entities/form.html",
		form=form,
		form_title="Edit Interaction Component",
		action_url=f"/interaction-components/{component_name}/edit",
		mcp_error="",
	)


@interaction_component_bp.post("/interaction-components/<component_name>/edit")
async def post_interaction_component_edit(component_name: str):
	"""Submit interaction component updates via MCP."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	form = InteractionComponentForm(MultiDict(await request.form), data={"WorkflowName": active_workflow_name})
	form.WorkflowName.data = active_workflow_name
	if not form.validate():
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Edit Interaction Component",
			action_url=f"/interaction-components/{component_name}/edit",
			mcp_error="",
		), 200

	payload = {
		"InteractionComponentName": str(form.InteractionComponentName.data or component_name).strip(),
		"WorkflowName": active_workflow_name,
		"InteractionComponentRelationShip": str(form.InteractionComponentRelationShip.data or "").strip(),
		"InteractionComponentDescription": str(form.InteractionComponentDescription.data or "").strip(),
		"InteractionComponentContextDescription": str(
			form.InteractionComponentContextDescription.data or ""
		).strip(),
		"SourceName": str(form.SourceName.data or "").strip(),
		"TargetName": str(form.TargetName.data or "").strip(),
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("interaction_component.update", payload)
	if str(result.get("status", "success")).lower() != "success":
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Edit Interaction Component",
			action_url=f"/interaction-components/{component_name}/edit",
			mcp_error=_mcp_error_message(result, "Interaction component update failed"),
		), 200
	_log_event(
		"quart.interaction_component.update.completed",
		started,
		"interaction_component.update",
		component_name=payload["InteractionComponentName"],
	)
	return redirect("/interaction-components")


@interaction_component_bp.get("/interaction-components/<component_name>/delete")
async def get_interaction_component_delete(component_name: str):
	"""Render interaction component delete confirmation page."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"interaction_component.get",
		{"InteractionComponentName": component_name, "WorkflowName": active_workflow_name},
	)
	record = _extract_record(result)
	_log_event(
		"quart.interaction_component.delete.confirm",
		started,
		"interaction_component.get",
		component_name=component_name,
	)
	return await render_template(
		"entities/delete_confirm.html",
		record=record,
		action_url=f"/interaction-components/{component_name}/delete",
		cancel_url="/interaction-components",
		mcp_error="",
	)


@interaction_component_bp.post("/interaction-components/<component_name>/delete")
async def post_interaction_component_delete(component_name: str):
	"""Submit interaction component delete to MCP and redirect on success."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	payload = {
		"InteractionComponentName": component_name,
		"WorkflowName": active_workflow_name,
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("interaction_component.delete", payload)
	if str(result.get("status", "success")).lower() != "success":
		record = {"InteractionComponentName": component_name, "WorkflowName": active_workflow_name}
		return await render_template(
			"entities/delete_confirm.html",
			record=record,
			action_url=f"/interaction-components/{component_name}/delete",
			cancel_url="/interaction-components",
			mcp_error=_mcp_error_message(result, "Interaction component delete failed"),
		), 200
	_log_event(
		"quart.interaction_component.delete.completed",
		started,
		"interaction_component.delete",
		component_name=component_name,
	)
	return redirect("/interaction-components")
