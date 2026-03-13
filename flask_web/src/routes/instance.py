from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, make_response, request

from flask_web.src.clients.mcp_client import MCPClient, MCPClientError

instance_bp = Blueprint("instance", __name__, url_prefix="/instance")


def _client() -> MCPClient:
    return MCPClient(base_url=os.environ.get("MCP_BASE_URL", "http://localhost:5001"))


def _actor() -> str:
    return os.environ.get("DEFAULT_ACTOR", "flask_ui_user")


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>{title}</title></head>
<body style='font-family:sans-serif;max-width:900px;margin:2rem auto'>
<nav><a href='/instance'>List</a> | <a href='/instance/new'>Create</a> | <a href='/instance/state'>Update State</a></nav>
<h1>{title}</h1>{body}</body></html>"""


@instance_bp.get("/")
def list_instances_view():
    wf = request.args.get("WorkflowName")
    params: dict[str, Any] = {"WorkflowName": wf} if wf else {}
    try:
        result = _client().call("instance.list", params)
        rows: list[dict[str, Any]] = result.get("instances", [])
    except MCPClientError as exc:
        return make_response(_page("Instances", f"<p style='color:red'>{exc}</p>"), 502)

    if not rows:
        body = "<p>No active instances found.</p>"
    else:
        head = "<tr><th>Instance</th><th>Workflow</th><th>State</th></tr>"
        lines = "".join(f"<tr><td>{r.get('InstanceName')}</td><td>{r.get('WorkflowName')}</td><td>{r.get('InstanceState')}</td></tr>" for r in rows)
        body = f"<table border='1' cellspacing='0' cellpadding='6'>{head}{lines}</table>"
    return make_response(_page("Instances", body), 200)


@instance_bp.get("/new")
def create_form():
    body = """
<form method='post' action='/instance'>
  <label>InstanceName <input name='InstanceName' required></label><br><br>
  <label>WorkflowName <input name='WorkflowName' required></label><br><br>
  <label>InstanceDescription <input name='InstanceDescription'></label><br><br>
  <label>InstanceContextDescription <input name='InstanceContextDescription'></label><br><br>
  <label>InstanceState <input name='InstanceState' value='A'></label><br><br>
  <button type='submit'>Create Instance</button>
</form>
"""
    return make_response(_page("Create Instance", body), 200)


@instance_bp.post("/")
def create_submit():
    params = {
        "InstanceName": request.form.get("InstanceName", "").strip(),
        "WorkflowName": request.form.get("WorkflowName", "").strip(),
        "InstanceDescription": request.form.get("InstanceDescription", "").strip() or None,
        "InstanceContextDescription": request.form.get("InstanceContextDescription", "").strip() or None,
        "InstanceState": request.form.get("InstanceState", "A").strip() or "A",
        "actor": _actor(),
    }
    if not params["InstanceName"] or not params["WorkflowName"]:
        return make_response(_page("Validation", "<p style='color:red'>InstanceName and WorkflowName are required.</p>"), 400)

    try:
        result = _client().call("instance.create", params)
        body = f"<p style='color:green'>Created instance <strong>{result['InstanceName']}</strong>.</p><p><a href='/instance'>Back</a></p>"
        return make_response(_page("Instance Created", body), 201)
    except MCPClientError as exc:
        return make_response(_page("Error", f"<p style='color:red'>{exc}</p>"), 409)


@instance_bp.get("/state")
def state_form():
    body = """
<form method='post' action='/instance/state'>
  <label>InstanceName <input name='InstanceName' required></label><br><br>
  <label>InstanceState <input name='InstanceState' required placeholder='A | I | P'></label><br><br>
  <button type='submit'>Update State</button>
</form>
"""
    return make_response(_page("Update Instance State", body), 200)


@instance_bp.post("/state")
def state_submit():
    params = {
        "InstanceName": request.form.get("InstanceName", "").strip(),
        "InstanceState": request.form.get("InstanceState", "").strip(),
        "actor": _actor(),
    }
    if not params["InstanceName"] or not params["InstanceState"]:
        return make_response(_page("Validation", "<p style='color:red'>InstanceName and InstanceState are required.</p>"), 400)

    try:
        result = _client().call("instance.update_state", params)
        body = f"<p style='color:green'>State updated: <strong>{result['InstanceName']}</strong> -> {result['InstanceState']}.</p><p><a href='/instance'>Back</a></p>"
        return make_response(_page("State Updated", body), 200)
    except MCPClientError as exc:
        return make_response(_page("Error", f"<p style='color:red'>{exc}</p>"), 409)
