"""Temporary Flask routes for Workflow create/list — T017.

These routes act as a thin UI layer: they call the MCP server via MCPClient
and render minimal HTML responses for manual testing/demonstration.

Environment variables consumed:
  - MCP_BASE_URL  (defaults to http://localhost:5001)
  - DEFAULT_ACTOR (defaults to "flask_ui_user")
"""
from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, make_response, request

from flask_web.src.clients.mcp_client import MCPClient, MCPClientError

workflow_bp = Blueprint("workflow", __name__, url_prefix="/workflow")


def _get_client() -> MCPClient:
    """Construct an MCP client using configured base URL."""

    base_url = os.environ.get("MCP_BASE_URL", "http://localhost:5001")
    return MCPClient(base_url=base_url)


def _actor() -> str:
    """Return the default actor used for UI-triggered write operations."""

    return os.environ.get("DEFAULT_ACTOR", "flask_ui_user")


def _html_page(title: str, body: str) -> str:
    """Render a minimal HTML wrapper for temporary workflow views."""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{title}</title>
<style>
  body {{ font-family: sans-serif; max-width: 800px; margin: 2rem auto; padding: 0 1rem; }}
  table {{ border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
  th {{ background: #f0f0f0; }}
  .error {{ color: #c00; }}
  .success {{ color: #060; }}
  form {{ margin-top: 1.5rem; }}
  label {{ display: block; margin: 0.5rem 0 0.2rem; }}
  input, textarea {{ width: 100%; box-sizing: border-box; padding: 0.3rem; }}
  button {{ margin-top: 0.8rem; padding: 0.4rem 1rem; }}
  nav a {{ margin-right: 1rem; }}
</style>
</head>
<body>
<nav><a href="/workflow">List Workflows</a><a href="/workflow/new">Create Workflow</a></nav>
<h1>{title}</h1>
{body}
</body>
</html>"""


# ---------------------------------------------------------------------------
# GET /workflow  — list all active workflows
# ---------------------------------------------------------------------------

@workflow_bp.get("/")
def list_workflows_view():
    """List active workflows by calling MCP workflow.list."""

    client = _get_client()
    try:
        result = client.call("workflow.list", {})
        workflows: list[dict[str, Any]] = result.get("workflows", [])
    except MCPClientError as exc:
        body = f'<p class="error">Error fetching workflows: {exc}</p>'
        return make_response(_html_page("Workflows", body), 502)

    if not workflows:
        rows_html = "<p>No active workflows found.</p>"
    else:
        header = "<tr><th>Name</th><th>Description</th><th>State</th><th>Created By</th></tr>"
        rows = "".join(
            f"<tr><td>{w.get('WorkflowName','')}</td>"
            f"<td>{w.get('WorkflowDescription','')}</td>"
            f"<td>{w.get('WorkflowStateInd','')}</td>"
            f"<td>{w.get('InsertUserName','')}</td></tr>"
            for w in workflows
        )
        rows_html = f"<table>{header}{rows}</table>"

    body = rows_html
    return make_response(_html_page("Workflows", body), 200)


# ---------------------------------------------------------------------------
# GET /workflow/new  — create form
# ---------------------------------------------------------------------------

@workflow_bp.get("/new")
def create_workflow_form():
    """Render the create-workflow form."""

    body = """
<form method="POST" action="/workflow">
  <label>Workflow Name <input name="WorkflowName" required /></label>
  <label>Description <textarea name="WorkflowDescription" rows="3"></textarea></label>
  <label>Context Description <textarea name="WorkflowContextDescription" rows="3"></textarea></label>
  <label>State Indicator <input name="WorkflowStateInd" value="A" /></label>
  <button type="submit">Create</button>
</form>"""
    return make_response(_html_page("Create Workflow", body), 200)


# ---------------------------------------------------------------------------
# POST /workflow  — submit create form
# ---------------------------------------------------------------------------

@workflow_bp.post("/")
def create_workflow_submit():
    """Submit workflow.create via MCP and show success/error feedback."""

    form = request.form
    params = {
        "WorkflowName": form.get("WorkflowName", "").strip(),
        "WorkflowDescription": form.get("WorkflowDescription", "").strip() or None,
        "WorkflowContextDescription": form.get("WorkflowContextDescription", "").strip() or None,
        "WorkflowStateInd": form.get("WorkflowStateInd", "A").strip() or "A",
        "actor": _actor(),
    }

    if not params["WorkflowName"]:
        body = '<p class="error">WorkflowName is required.</p>'
        return make_response(_html_page("Create Workflow", body), 400)

    client = _get_client()
    try:
        result = client.call("workflow.create", params)
        body = (
            f'<p class="success">Workflow <strong>{result["WorkflowName"]}</strong> created successfully.</p>'
            f'<p><a href="/workflow">Back to list</a></p>'
        )
        return make_response(_html_page("Workflow Created", body), 201)
    except MCPClientError as exc:
        body = f'<p class="error">Error creating workflow: {exc}</p>'
        return make_response(_html_page("Error", body), 409)
