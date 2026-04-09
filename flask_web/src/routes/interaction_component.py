"""Interaction-component entity routes for the canonical Flask web tier."""

from __future__ import annotations

from flask import session

from flask_web.src.forms.interaction_component import InteractionComponentForm
from flask_web.src.routes.entity_helpers import build_crud_blueprint, require_workflow_context


def _create_payload(form: InteractionComponentForm, _entity_id: str | None) -> dict[str, str]:
    return {
        "InteractionComponentName": str(form.InteractionComponentName.data or "").strip(),
        "WorkflowName": str(session.get("active_workflow_name")),
        "InteractionComponentRelationShip": str(form.InteractionComponentRelationShip.data or "").strip(),
        "InteractionComponentDescription": str(form.InteractionComponentDescription.data or "").strip(),
        "InteractionComponentContextDescription": str(form.InteractionComponentContextDescription.data or "").strip(),
        "SourceName": str(form.SourceName.data or "").strip(),
        "TargetName": str(form.TargetName.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _update_payload(form: InteractionComponentForm, entity_id: str | None) -> dict[str, str]:
    return {
        "InteractionComponentName": str(form.InteractionComponentName.data or entity_id or "").strip(),
        "WorkflowName": str(session.get("active_workflow_name")),
        "InteractionComponentRelationShip": str(form.InteractionComponentRelationShip.data or "").strip(),
        "InteractionComponentDescription": str(form.InteractionComponentDescription.data or "").strip(),
        "InteractionComponentContextDescription": str(form.InteractionComponentContextDescription.data or "").strip(),
        "SourceName": str(form.SourceName.data or "").strip(),
        "TargetName": str(form.TargetName.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _list_params() -> dict[str, str]:
    return {"WorkflowName": str(session.get("active_workflow_name"))}


def _get_params(entity_id: str) -> dict[str, str]:
    return {
        "InteractionComponentName": entity_id,
        "WorkflowName": str(session.get("active_workflow_name")),
    }


def _delete_params(entity_id: str) -> dict[str, str]:
    return {
        "InteractionComponentName": entity_id,
        "WorkflowName": str(session.get("active_workflow_name")),
        "actor": str(session.get("user_id")),
    }


interaction_component_bp = build_crud_blueprint(
    blueprint_name="interaction_component",
    entity_label="Interaction Components",
    entity_path="interaction-components",
    id_field="InteractionComponentName",
    columns=["InteractionComponentName", "WorkflowName"],
    form_cls=InteractionComponentForm,
    require_context=require_workflow_context,
    list_params=_list_params,
    list_method="interaction_component.list",
    get_method="interaction_component.get",
    create_method="interaction_component.create",
    update_method="interaction_component.update",
    delete_method="interaction_component.delete",
    build_create_payload=_create_payload,
    build_update_payload=_update_payload,
    build_get_params=_get_params,
    build_delete_params=_delete_params,
)