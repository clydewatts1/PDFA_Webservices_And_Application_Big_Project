"""Role entity routes."""

from __future__ import annotations

import json
import logging
import time

from quart import Blueprint, current_app, redirect, render_template, request, session
from werkzeug.datastructures import MultiDict

from quart_web.src.forms.role import RoleForm


role_bp = Blueprint("role", __name__)
logger = logging.getLogger("pdfa.quart.role")


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


@role_bp.get("/roles")
async def list_roles():
	"""Render role list view for the active workflow."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = session.get("active_workflow_name")

	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"role.list",
		{"WorkflowName": active_workflow_name},
	)
	records = result.get("records") if isinstance(result, dict) else []
	if not isinstance(records, list):
		records = []
	_log_event("quart.role.list.completed", started, "role.list", record_count=len(records))

	return await render_template(
		"entities/list.html",
		entity_label="Roles",
		entity_path="roles",
		records=records,
		columns=["RoleName", "WorkflowName", "RoleDescription"],
		id_field="RoleName",
	)


@role_bp.get("/roles/new")
async def get_role_create():
	"""Render role creation form."""
	context = _require_context()
	if context is not None:
		return context
	form = RoleForm(data={"WorkflowName": session.get("active_workflow_name", "")})
	return await render_template(
		"entities/form.html",
		form=form,
		form_title="Create Role",
		action_url="/roles/new",
		mcp_error="",
	)


@role_bp.post("/roles/new")
async def post_role_create():
	"""Submit role creation via MCP."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	form = RoleForm(MultiDict(await request.form), data={"WorkflowName": active_workflow_name})
	form.WorkflowName.data = active_workflow_name
	if not form.validate():
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Create Role",
			action_url="/roles/new",
			mcp_error="",
		), 200

	payload = {
		"RoleName": str(form.RoleName.data or "").strip(),
		"WorkflowName": active_workflow_name,
		"RoleDescription": str(form.RoleDescription.data or "").strip(),
		"RoleContextDescription": str(form.RoleContextDescription.data or "").strip(),
		"RoleConfiguration": str(form.RoleConfiguration.data or "").strip(),
		"RoleConfigurationDescription": str(form.RoleConfigurationDescription.data or "").strip(),
		"RoleConfigurationContextDescription": str(form.RoleConfigurationContextDescription.data or "").strip(),
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("role.create", payload)
	if str(result.get("status", "success")).lower() != "success":
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Create Role",
			action_url="/roles/new",
			mcp_error=_mcp_error_message(result, "Role create failed"),
		), 200
	_log_event("quart.role.create.completed", started, "role.create", role_name=payload["RoleName"])
	return redirect("/roles")


@role_bp.get("/roles/<role_name>/edit")
async def get_role_edit(role_name: str):
	"""Render role edit form."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"role.get", {"RoleName": role_name, "WorkflowName": active_workflow_name}
	)
	record = _extract_record(result)
	_log_event("quart.role.get.completed", started, "role.get", role_name=role_name)
	form = RoleForm(data=record)
	return await render_template(
		"entities/form.html",
		form=form,
		form_title="Edit Role",
		action_url=f"/roles/{role_name}/edit",
		mcp_error="",
	)


@role_bp.post("/roles/<role_name>/edit")
async def post_role_edit(role_name: str):
	"""Submit role updates via MCP."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	form = RoleForm(MultiDict(await request.form), data={"WorkflowName": active_workflow_name})
	form.WorkflowName.data = active_workflow_name
	if not form.validate():
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Edit Role",
			action_url=f"/roles/{role_name}/edit",
			mcp_error="",
		), 200

	payload = {
		"RoleName": str(form.RoleName.data or role_name).strip(),
		"WorkflowName": active_workflow_name,
		"RoleDescription": str(form.RoleDescription.data or "").strip(),
		"RoleContextDescription": str(form.RoleContextDescription.data or "").strip(),
		"RoleConfiguration": str(form.RoleConfiguration.data or "").strip(),
		"RoleConfigurationDescription": str(form.RoleConfigurationDescription.data or "").strip(),
		"RoleConfigurationContextDescription": str(form.RoleConfigurationContextDescription.data or "").strip(),
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("role.update", payload)
	if str(result.get("status", "success")).lower() != "success":
		return await render_template(
			"entities/form.html",
			form=form,
			form_title="Edit Role",
			action_url=f"/roles/{role_name}/edit",
			mcp_error=_mcp_error_message(result, "Role update failed"),
		), 200
	_log_event("quart.role.update.completed", started, "role.update", role_name=payload["RoleName"])
	return redirect("/roles")


@role_bp.get("/roles/<role_name>/delete")
async def get_role_delete(role_name: str):
	"""Render role delete confirmation page."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool(
		"role.get", {"RoleName": role_name, "WorkflowName": active_workflow_name}
	)
	record = _extract_record(result)
	_log_event("quart.role.delete.confirm", started, "role.get", role_name=role_name)
	return await render_template(
		"entities/delete_confirm.html",
		record=record,
		action_url=f"/roles/{role_name}/delete",
		cancel_url="/roles",
		mcp_error="",
	)


@role_bp.post("/roles/<role_name>/delete")
async def post_role_delete(role_name: str):
	"""Submit role delete to MCP and redirect on success."""
	context = _require_context()
	if context is not None:
		return context
	active_workflow_name = str(session.get("active_workflow_name"))
	payload = {
		"RoleName": role_name,
		"WorkflowName": active_workflow_name,
		"actor": str(session.get("user_id")),
	}
	started = time.perf_counter()
	result = await current_app.mcp_client.call_tool("role.delete", payload)
	if str(result.get("status", "success")).lower() != "success":
		record = {"RoleName": role_name, "WorkflowName": active_workflow_name}
		return await render_template(
			"entities/delete_confirm.html",
			record=record,
			action_url=f"/roles/{role_name}/delete",
			cancel_url="/roles",
			mcp_error=_mcp_error_message(result, "Role delete failed"),
		), 200
	_log_event("quart.role.delete.completed", started, "role.delete", role_name=role_name)
	return redirect("/roles")
