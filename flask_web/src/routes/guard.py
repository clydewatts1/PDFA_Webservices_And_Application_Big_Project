"""Guard entity routes for the canonical Flask web tier."""

from __future__ import annotations

from flask import session

from flask_web.src.forms.guard import GuardForm
from flask_web.src.routes.entity_helpers import build_crud_blueprint, require_workflow_context


def _create_payload(form: GuardForm, _entity_id: str | None) -> dict[str, str]:
    return {
        "GuardName": str(form.GuardName.data or "").strip(),
        "WorkflowName": str(session.get("active_workflow_name")),
        "GuardDescription": str(form.GuardDescription.data or "").strip(),
        "GuardContextDescription": str(form.GuardContextDescription.data or "").strip(),
        "GuardType": str(form.GuardType.data or "").strip(),
        "GuardConfiguration": str(form.GuardConfiguration.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _update_payload(form: GuardForm, entity_id: str | None) -> dict[str, str]:
    return {
        "GuardName": str(form.GuardName.data or entity_id or "").strip(),
        "WorkflowName": str(session.get("active_workflow_name")),
        "GuardDescription": str(form.GuardDescription.data or "").strip(),
        "GuardContextDescription": str(form.GuardContextDescription.data or "").strip(),
        "GuardType": str(form.GuardType.data or "").strip(),
        "GuardConfiguration": str(form.GuardConfiguration.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _list_params() -> dict[str, str]:
    return {"WorkflowName": str(session.get("active_workflow_name"))}


def _get_params(entity_id: str) -> dict[str, str]:
    return {"GuardName": entity_id, "WorkflowName": str(session.get("active_workflow_name"))}


def _delete_params(entity_id: str) -> dict[str, str]:
    return {
        "GuardName": entity_id,
        "WorkflowName": str(session.get("active_workflow_name")),
        "actor": str(session.get("user_id")),
    }


guard_bp = build_crud_blueprint(
    blueprint_name="guard",
    entity_label="Guards",
    entity_path="guards",
    id_field="GuardName",
    columns=["GuardName", "WorkflowName"],
    form_cls=GuardForm,
    require_context=require_workflow_context,
    list_params=_list_params,
    list_method="guard.list",
    get_method="guard.get",
    create_method="guard.create",
    update_method="guard.update",
    delete_method="guard.delete",
    build_create_payload=_create_payload,
    build_update_payload=_update_payload,
    build_get_params=_get_params,
    build_delete_params=_delete_params,
)