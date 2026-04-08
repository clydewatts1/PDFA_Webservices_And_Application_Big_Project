"""Workspace-selection routes for authenticated Flask users."""

from __future__ import annotations

import json
import logging
import time

from flask import Blueprint, current_app, redirect, render_template, session, url_for

from flask_web.src.clients.mcp_client import MCPClientError
from flask_web.src.forms.auth import LogoutForm, WorkspaceSelectForm


workspace_bp = Blueprint("workspace", __name__)
logger = logging.getLogger("pdfa.flask.workspace")


def _is_authenticated() -> bool:
    return bool(session.get("user_id"))


def _workflow_choices(workflows: list[dict[str, object]]) -> list[tuple[str, str]]:
    choices: list[tuple[str, str]] = []
    for workflow in workflows:
        workflow_name = str(workflow.get("WorkflowName") or "").strip()
        if not workflow_name:
            continue
        description = str(workflow.get("WorkflowDescription") or "").strip()
        label = workflow_name if not description else f"{workflow_name} - {description}"
        choices.append((workflow_name, label))
    return choices


def _fetch_workflows() -> list[dict[str, object]]:
    result = current_app.mcp_client.call("workflow.list", {})
    records = result.get("records")
    if isinstance(records, list):
        return [record for record in records if isinstance(record, dict)]
    return []


@workspace_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """Render and submit workflow-selection dashboard."""

    if not _is_authenticated():
        return redirect(url_for("auth.login"))

    started = time.perf_counter()
    workflows: list[dict[str, object]] = []
    workflow_error = ""
    try:
        workflows = _fetch_workflows()
    except MCPClientError as exc:
        workflow_error = exc.message
        logger.warning(
            json.dumps(
                {
                    "event": "flask.workspace.fetch_workflows.error",
                    "tool_name": "workflow.list",
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "workflow_name": session.get("active_workflow_name"),
                    "username": session.get("user_id"),
                    "error": exc.message,
                }
            )
        )

    form = WorkspaceSelectForm()
    form.workflow_name.choices = _workflow_choices(workflows)
    if form.validate_on_submit():
        active_workflow_name = str(form.workflow_name.data or "").strip()
        session["active_workflow_name"] = active_workflow_name
        logger.info(
            json.dumps(
                {
                    "event": "flask.workspace.select_workflow.success",
                    "tool_name": "workflow.list",
                    "username": session.get("user_id"),
                    "workflow_name": active_workflow_name,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                }
            )
        )
        return redirect(url_for("workspace.entities_dashboard"))

    logger.info(
        json.dumps(
            {
                "event": "flask.workspace.dashboard.rendered",
                "tool_name": "workflow.list",
                "workflow_name": session.get("active_workflow_name"),
                "username": session.get("user_id"),
                "workflow_count": len(workflows),
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
            }
        )
    )
    return render_template(
        "workspace/dashboard.html",
        form=form,
        workflows=workflows,
        workflow_error=workflow_error,
        logout_form=LogoutForm(),
    )


@workspace_bp.get("/entities")
def entities_dashboard():
    """Render entities navigation dashboard for active workflow context."""

    if not _is_authenticated():
        return redirect(url_for("auth.login"))
    if not session.get("active_workflow_name"):
        return redirect(url_for("workspace.dashboard"))

    return render_template(
        "workspace/entities.html",
        active_workflow_name=session.get("active_workflow_name"),
        logout_form=LogoutForm(),
    )