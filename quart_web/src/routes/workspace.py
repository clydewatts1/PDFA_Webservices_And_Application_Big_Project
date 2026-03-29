"""Workspace/workflow-selection routes for authenticated users."""

from __future__ import annotations

import json
import logging
import time

from quart import Blueprint, current_app, render_template, request, session, redirect
from werkzeug.datastructures import MultiDict

from quart_web.src.clients.errors import MCPClientError
from quart_web.src.forms.auth import WorkspaceSelectForm


workspace_bp = Blueprint("workspace", __name__)

logger = logging.getLogger("pdfa.quart.workspace")


def _is_authenticated() -> bool:
	return bool(session.get("user_id"))


def _workflow_choices(workflows: list[dict]) -> list[tuple[str, str]]:
	choices: list[tuple[str, str]] = []
	for workflow in workflows:
		workflow_name = str(workflow.get("WorkflowName") or "").strip()
		if not workflow_name:
			continue
		description = str(workflow.get("WorkflowDescription") or "").strip()
		label = workflow_name if not description else f"{workflow_name} — {description}"
		choices.append((workflow_name, label))
	return choices


def _select_form(form_data: MultiDict | None, workflows: list[dict]) -> WorkspaceSelectForm:
	form = WorkspaceSelectForm(form_data)
	form.workflow_name.choices = _workflow_choices(workflows)
	return form


async def _fetch_workflows() -> list[dict]:
	result = await current_app.mcp_client.call_tool("workflow.list", {})
	records = result.get("records")
	if isinstance(records, list):
		return [record for record in records if isinstance(record, dict)]
	return []


@workspace_bp.get("/dashboard")
async def get_dashboard():
	"""Render workflow selection dashboard for authenticated users."""
	if not _is_authenticated():
		return redirect("/login")

	started = time.perf_counter()
	workflows: list[dict] = []
	workflow_error = ""

	try:
		workflows = await _fetch_workflows()
	except MCPClientError as exc:
		workflow_error = exc.message
		logger.warning(
			json.dumps(
				{
					"event": "quart.workspace.fetch_workflows.error",
					"tool_name": "workflow.list",
					"duration_ms": round((time.perf_counter() - started) * 1000, 2),
					"workflow_name": session.get("active_workflow_name"),
					"username": session.get("user_id"),
					"error": exc.message,
				}
			)
		)

	form = _select_form(None, workflows)

	logger.info(
		json.dumps(
			{
				"event": "quart.workspace.dashboard.rendered",
				"tool_name": "workflow.list",
				"workflow_name": session.get("active_workflow_name"),
				"username": session.get("user_id"),
				"workflow_count": len(workflows),
				"duration_ms": round((time.perf_counter() - started) * 1000, 2),
			}
		)
	)

	return await render_template(
		"workspace/dashboard.html",
		form=form,
		workflows=workflows,
		workflow_error=workflow_error,
	)


@workspace_bp.post("/dashboard")
async def post_dashboard():
	"""Persist selected workflow to session and redirect to entities dashboard."""
	if not _is_authenticated():
		return redirect("/login")

	started = time.perf_counter()
	form_data = MultiDict(await request.form)

	try:
		workflows = await _fetch_workflows()
	except MCPClientError as exc:
		logger.warning(
			json.dumps(
				{
					"event": "quart.workspace.select_workflow.error",
					"tool_name": "workflow.list",
					"duration_ms": round((time.perf_counter() - started) * 1000, 2),
					"workflow_name": session.get("active_workflow_name"),
					"username": session.get("user_id"),
					"error": exc.message,
				}
			)
		)
		workflows = []

	form = _select_form(form_data, workflows)
	if not form.validate():
		return await render_template(
			"workspace/dashboard.html",
			form=form,
			workflows=workflows,
			workflow_error="",
		), 200

	active_workflow_name = str(form.workflow_name.data or "").strip()
	session["active_workflow_name"] = active_workflow_name

	logger.info(
		json.dumps(
			{
				"event": "quart.workspace.select_workflow.success",
				"tool_name": "workflow.list",
				"username": session.get("user_id"),
				"workflow_name": active_workflow_name,
				"duration_ms": round((time.perf_counter() - started) * 1000, 2),
			}
		)
	)
	return redirect("/entities")


@workspace_bp.get("/entities")
async def get_entities_dashboard():
	"""Render entities navigation dashboard for users with active workflow context."""
	if not _is_authenticated():
		return redirect("/login")
	if not session.get("active_workflow_name"):
		return redirect("/dashboard")

	return await render_template(
		"workspace/entities.html",
		active_workflow_name=session.get("active_workflow_name"),
	)
