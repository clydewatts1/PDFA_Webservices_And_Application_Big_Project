"""Workflow entity routes for the canonical Flask web tier."""
from __future__ import annotations

from flask import session

from flask_web.src.forms.workflow import WorkflowForm
from flask_web.src.routes.entity_helpers import build_crud_blueprint, require_login


def _create_payload(form: WorkflowForm, _entity_id: str | None) -> dict[str, str]:
    return {
        "WorkflowName": str(form.WorkflowName.data or "").strip(),
        "WorkflowDescription": str(form.WorkflowDescription.data or "").strip(),
        "WorkflowContextDescription": str(form.WorkflowContextDescription.data or "").strip(),
        "WorkflowStateInd": str(form.WorkflowStateInd.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _update_payload(form: WorkflowForm, entity_id: str | None) -> dict[str, str]:
    return {
        "WorkflowName": str(form.WorkflowName.data or entity_id or "").strip(),
        "WorkflowDescription": str(form.WorkflowDescription.data or "").strip(),
        "WorkflowContextDescription": str(form.WorkflowContextDescription.data or "").strip(),
        "WorkflowStateInd": str(form.WorkflowStateInd.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _get_params(entity_id: str) -> dict[str, str]:
    return {"WorkflowName": entity_id} if entity_id else {}


def _delete_params(entity_id: str) -> dict[str, str]:
    return {"WorkflowName": entity_id, "actor": str(session.get("user_id"))}


workflow_bp = build_crud_blueprint(
    blueprint_name="workflow",
    entity_label="Workflows",
    entity_path="workflows",
    id_field="WorkflowName",
    columns=["WorkflowName", "WorkflowDescription"],
    form_cls=WorkflowForm,
    require_context=require_login,
    list_params=lambda: {},
    list_method="workflow.list",
    get_method="workflow.get",
    create_method="workflow.create",
    update_method="workflow.update",
    delete_method="workflow.delete",
    build_create_payload=_create_payload,
    build_update_payload=_update_payload,
    build_get_params=_get_params,
    build_delete_params=_delete_params,
)
