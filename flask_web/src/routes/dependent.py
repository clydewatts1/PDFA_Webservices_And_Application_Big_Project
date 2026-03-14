"""Temporary Flask routes for dependent entity create/list — T024.

All five entity types share a unified blueprint that renders minimal HTML
for manual testing.  Each entity is accessible at:

    GET  /entities/<entity>            — list active rows (filterable by WorkflowName)
    GET  /entities/<entity>/new        — create form
    POST /entities/<entity>            — submit create

Supported <entity> slugs: role, interaction, guard, interaction_component, unit_of_work.

Environment variables:
  MCP_BASE_URL  (default: http://localhost:5001)
  DEFAULT_ACTOR (default: flask_ui_user)
"""
from __future__ import annotations

import os
from typing import Any

from flask import Blueprint, make_response, request

from flask_web.src.clients.mcp_client import MCPClient, MCPClientError

dependent_bp = Blueprint("dependent", __name__, url_prefix="/entities")

# Map slug → (display label, required fields for create form, optional fields)
_ENTITY_META: dict[str, dict[str, Any]] = {
    "role": {
        "label": "Role",
        "required": ["RoleName", "WorkflowName"],
        "optional": ["RoleDescription", "RoleContextDescription",
                     "RoleConfiguration", "RoleConfigurationDescription",
                     "RoleConfigurationContextDescription"],
    },
    "interaction": {
        "label": "Interaction",
        "required": ["InteractionName", "WorkflowName"],
        "optional": ["InteractionDescription", "InteractionContextDescription", "InteractionType"],
    },
    "guard": {
        "label": "Guard",
        "required": ["GuardName", "WorkflowName"],
        "optional": ["GuardDescription", "GuardContextDescription", "GuardType", "GuardConfiguration"],
    },
    "interaction_component": {
        "label": "Interaction Component",
        "required": ["InteractionComponentName", "WorkflowName"],
        "optional": ["InteractionComponentRelationShip", "InteractionComponentDescription",
                     "InteractionComponentContextDescription", "SourceName", "TargetName"],
    },
    "unit_of_work": {
        "label": "Unit of Work",
        "required": ["UnitOfWorkID"],
        "optional": ["UnitOfWorkType", "UnitOfWorkPayLoad"],
    },
}


def _client() -> MCPClient:
    """Construct an MCP client for dependent-entity operations."""

    return MCPClient(base_url=os.environ.get("MCP_BASE_URL", "http://localhost:5001"))


def _actor() -> str:
    """Return the default actor identity for dependent writes."""

    return os.environ.get("DEFAULT_ACTOR", "flask_ui_user")


def _page(title: str, body: str) -> str:
    """Render shared HTML shell for dependent-entity pages."""

    nav_links = " | ".join(
        f'<a href="/entities/{slug}">{meta["label"]}</a>'
        for slug, meta in _ENTITY_META.items()
    )
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{title}</title>
<style>
  body{{font-family:sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem}}
  table{{border-collapse:collapse;width:100%}}
  th,td{{border:1px solid #ccc;padding:.4rem .6rem;text-align:left;font-size:.85rem}}
  th{{background:#f0f0f0}}
  .error{{color:#c00}} .success{{color:#060}}
  form label{{display:block;margin:.4rem 0 .15rem}}
  form input,form textarea{{width:100%;box-sizing:border-box;padding:.3rem}}
  form button{{margin-top:.7rem;padding:.35rem .9rem}}
  nav{{margin-bottom:1rem;font-size:.85rem}}
</style></head><body>
<nav>{nav_links}</nav>
<h1>{title}</h1>
{body}
</body></html>"""


def _404_entity(slug: str):
    """Return an entity-not-found response for unknown route slugs."""

    return make_response(_page("Not Found", f"<p class='error'>Unknown entity type: {slug}</p>"), 404)


# ---------------------------------------------------------------------------
# GET /entities/<entity>  — list
# ---------------------------------------------------------------------------

@dependent_bp.get("/<entity>")
def list_entities_view(entity: str):
    """List active records for a dependent entity type."""

    meta = _ENTITY_META.get(entity)
    if not meta:
        return _404_entity(entity)

    workflow_filter = request.args.get("WorkflowName", "")
    params: dict[str, Any] = {}
    if workflow_filter:
        params["WorkflowName"] = workflow_filter

    try:
        result = _client().call(f"{entity}.list", params)
        rows: list[dict[str, Any]] = result.get(f"{entity}s", [])
    except MCPClientError as exc:
        return make_response(_page(meta["label"], f"<p class='error'>{exc}</p>"), 502)

    if not rows:
        body = "<p>No active records found.</p>"
    else:
        keys = [k for k in rows[0] if not k.startswith("Eff") and k not in ("DeleteInd",)]
        header = "".join(f"<th>{k}</th>" for k in keys)
        row_html = "".join(
            "<tr>" + "".join(f"<td>{r.get(k,'')}</td>" for k in keys) + "</tr>"
            for r in rows
        )
        body = (
            f'<p><a href="/entities/{entity}/new">+ New {meta["label"]}</a></p>'
            f"<table><tr>{header}</tr>{row_html}</table>"
        )

    return make_response(_page(f"{meta['label']} List", body), 200)


# ---------------------------------------------------------------------------
# GET /entities/<entity>/new  — form
# ---------------------------------------------------------------------------

@dependent_bp.get("/<entity>/new")
def create_entity_form(entity: str):
    """Render create form for the selected dependent entity type."""

    meta = _ENTITY_META.get(entity)
    if not meta:
        return _404_entity(entity)

    fields = meta["required"] + meta["optional"]
    inputs = "".join(
        f"<label>{f} {'<span style=\"color:red\">*</span>' if f in meta['required'] else ''}"
        f"<input name='{f}' {'required' if f in meta['required'] else ''}/></label>"
        for f in fields
    )
    body = f"""<form method="POST" action="/entities/{entity}">
{inputs}
<button type="submit">Create</button>
</form>"""
    return make_response(_page(f"New {meta['label']}", body), 200)


# ---------------------------------------------------------------------------
# POST /entities/<entity>  — submit
# ---------------------------------------------------------------------------

@dependent_bp.post("/<entity>")
def create_entity_submit(entity: str):
    """Submit create request for selected dependent entity type."""

    meta = _ENTITY_META.get(entity)
    if not meta:
        return _404_entity(entity)

    form = request.form
    params: dict[str, Any] = {"actor": _actor()}
    for f in meta["required"] + meta["optional"]:
        v = form.get(f, "").strip()
        if v:
            params[f] = v

    for req in meta["required"]:
        if not params.get(req):
            body = f"<p class='error'>{req} is required.</p>"
            return make_response(_page("Validation Error", body), 400)

    try:
        result = _client().call(f"{entity}.create", params)
        first_key = meta["required"][0]
        body = (
            f"<p class='success'><strong>{result.get(first_key)}</strong> created.</p>"
            f"<p><a href='/entities/{entity}'>Back to list</a></p>"
        )
        return make_response(_page(f"{meta['label']} Created", body), 201)
    except MCPClientError as exc:
        body = f"<p class='error'>{exc}</p>"
        return make_response(_page("Error", body), 409)
