"""Interaction entity routes for the canonical Flask web tier."""

from __future__ import annotations

from flask import session

from flask_web.src.forms.interaction import InteractionForm
from flask_web.src.routes.entity_helpers import build_crud_blueprint, require_workflow_context


def _create_payload(form: InteractionForm, _entity_id: str | None) -> dict[str, str]:
    return {
        "InteractionName": str(form.InteractionName.data or "").strip(),
        "WorkflowName": str(session.get("active_workflow_name")),
        "InteractionDescription": str(form.InteractionDescription.data or "").strip(),
        "InteractionContextDescription": str(form.InteractionContextDescription.data or "").strip(),
        "InteractionType": str(form.InteractionType.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _update_payload(form: InteractionForm, entity_id: str | None) -> dict[str, str]:
    return {
        "InteractionName": str(form.InteractionName.data or entity_id or "").strip(),
        "WorkflowName": str(session.get("active_workflow_name")),
        "InteractionDescription": str(form.InteractionDescription.data or "").strip(),
        "InteractionContextDescription": str(form.InteractionContextDescription.data or "").strip(),
        "InteractionType": str(form.InteractionType.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _list_params() -> dict[str, str]:
    return {"WorkflowName": str(session.get("active_workflow_name"))}


def _get_params(entity_id: str) -> dict[str, str]:
    return {"InteractionName": entity_id, "WorkflowName": str(session.get("active_workflow_name"))}


def _delete_params(entity_id: str) -> dict[str, str]:
    return {
        "InteractionName": entity_id,
        "WorkflowName": str(session.get("active_workflow_name")),
        "actor": str(session.get("user_id")),
    }


interaction_bp = build_crud_blueprint(
    blueprint_name="interaction",
    entity_label="Interactions",
    entity_path="interactions",
    id_field="InteractionName",
    columns=["InteractionName", "WorkflowName"],
    form_cls=InteractionForm,
    require_context=require_workflow_context,
    list_params=_list_params,
    list_method="interaction.list",
    get_method="interaction.get",
    create_method="interaction.create",
    update_method="interaction.update",
    delete_method="interaction.delete",
    build_create_payload=_create_payload,
    build_update_payload=_update_payload,
    build_get_params=_get_params,
    build_delete_params=_delete_params,
)