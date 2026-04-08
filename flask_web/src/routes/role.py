"""Role entity routes for the canonical Flask web tier."""

from __future__ import annotations

from flask import session

from flask_web.src.forms.role import RoleForm
from flask_web.src.routes.entity_helpers import build_crud_blueprint, require_workflow_context


def _create_payload(form: RoleForm, _entity_id: str | None) -> dict[str, str]:
    return {
        "RoleName": str(form.RoleName.data or "").strip(),
        "WorkflowName": str(session.get("active_workflow_name")),
        "RoleDescription": str(form.RoleDescription.data or "").strip(),
        "RoleContextDescription": str(form.RoleContextDescription.data or "").strip(),
        "RoleConfiguration": str(form.RoleConfiguration.data or "").strip(),
        "RoleConfigurationDescription": str(form.RoleConfigurationDescription.data or "").strip(),
        "RoleConfigurationContextDescription": str(form.RoleConfigurationContextDescription.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _update_payload(form: RoleForm, entity_id: str | None) -> dict[str, str]:
    return {
        "RoleName": str(form.RoleName.data or entity_id or "").strip(),
        "WorkflowName": str(session.get("active_workflow_name")),
        "RoleDescription": str(form.RoleDescription.data or "").strip(),
        "RoleContextDescription": str(form.RoleContextDescription.data or "").strip(),
        "RoleConfiguration": str(form.RoleConfiguration.data or "").strip(),
        "RoleConfigurationDescription": str(form.RoleConfigurationDescription.data or "").strip(),
        "RoleConfigurationContextDescription": str(form.RoleConfigurationContextDescription.data or "").strip(),
        "actor": str(session.get("user_id")),
    }


def _list_params() -> dict[str, str]:
    return {"WorkflowName": str(session.get("active_workflow_name"))}


def _get_params(entity_id: str) -> dict[str, str]:
    return {"RoleName": entity_id, "WorkflowName": str(session.get("active_workflow_name"))}


def _delete_params(entity_id: str) -> dict[str, str]:
    return {
        "RoleName": entity_id,
        "WorkflowName": str(session.get("active_workflow_name")),
        "actor": str(session.get("user_id")),
    }


role_bp = build_crud_blueprint(
    blueprint_name="role",
    entity_label="Roles",
    entity_path="roles",
    id_field="RoleName",
    columns=["RoleName", "WorkflowName", "RoleDescription"],
    form_cls=RoleForm,
    require_context=require_workflow_context,
    list_params=_list_params,
    list_method="role.list",
    get_method="role.get",
    create_method="role.create",
    update_method="role.update",
    delete_method="role.delete",
    build_create_payload=_create_payload,
    build_update_payload=_update_payload,
    build_get_params=_get_params,
    build_delete_params=_delete_params,
)