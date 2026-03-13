"""Generic temporal CRUD service for dependent entities — T022.

Supports Role, Interaction, Guard, InteractionComponent, UnitOfWork via
EntityConfig dataclasses. All public functions accept an open SQLAlchemy
Session and raise ServiceError subclasses for handler mapping.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from mcp_server.src.models.base import HIGH_DATE
from mcp_server.src.models.dependent import (
    Guard,
    GuardHist,
    Interaction,
    InteractionComponent,
    InteractionComponentHist,
    InteractionHist,
    Role,
    RoleHist,
    UnitOfWork,
    UnitOfWorkHist,
)
from mcp_server.src.models.workflow import Workflow
from mcp_server.src.services.workflow_service import (
    DuplicateKeyError,
    MissingFieldError,
    ServiceError,
)


# ---------------------------------------------------------------------------
# Additional exceptions
# ---------------------------------------------------------------------------

class InvalidWorkflowReferenceError(ServiceError):
    def __init__(self, workflow_name: str) -> None:
        super().__init__(
            f"Workflow '{workflow_name}' is not active or does not exist.",
            code="invalid_workflow_reference",
        )


class EntityNotFoundError(ServiceError):
    def __init__(self, entity_name: str, key_desc: str) -> None:
        super().__init__(
            f"{entity_name} '{key_desc}' not found or not active.",
            code="entity_not_found",
        )


# ---------------------------------------------------------------------------
# Entity configuration
# ---------------------------------------------------------------------------

@dataclass
class EntityConfig:
    entity_name: str
    model_class: type
    hist_class: type
    business_keys: list[str]
    all_fields: list[str]
    requires_workflow_fk: bool = True


ROLE_CONFIG = EntityConfig(
    entity_name="role",
    model_class=Role,
    hist_class=RoleHist,
    business_keys=["RoleName", "WorkflowName"],
    all_fields=[
        "RoleName", "WorkflowName", "InstanceName",
        "RoleDescription", "RoleContextDescription",
        "RoleConfiguration", "RoleConfigurationDescription",
        "RoleConfigurationContextDescription",
    ],
    requires_workflow_fk=True,
)

INTERACTION_CONFIG = EntityConfig(
    entity_name="interaction",
    model_class=Interaction,
    hist_class=InteractionHist,
    business_keys=["InteractionName", "WorkflowName"],
    all_fields=[
        "InteractionName", "WorkflowName", "InstanceName",
        "InteractionDescription", "InteractionContextDescription",
        "InteractionType",
    ],
    requires_workflow_fk=True,
)

GUARD_CONFIG = EntityConfig(
    entity_name="guard",
    model_class=Guard,
    hist_class=GuardHist,
    business_keys=["GuardName", "WorkflowName"],
    all_fields=[
        "GuardName", "WorkflowName", "InstanceName",
        "GuardDescription", "GuardContextDescription",
        "GuardType", "GuardConfiguration",
    ],
    requires_workflow_fk=True,
)

INTERACTION_COMPONENT_CONFIG = EntityConfig(
    entity_name="interaction_component",
    model_class=InteractionComponent,
    hist_class=InteractionComponentHist,
    business_keys=["InteractionComponentName", "WorkflowName"],
    all_fields=[
        "InteractionComponentName", "WorkflowName", "InstanceName",
        "InteractionComponentRelationShip",
        "InteractionComponentDescription",
        "InteractionComponentContextDescription",
        "SourceName", "TargetName",
    ],
    requires_workflow_fk=True,
)

UNIT_OF_WORK_CONFIG = EntityConfig(
    entity_name="unit_of_work",
    model_class=UnitOfWork,
    hist_class=UnitOfWorkHist,
    business_keys=["UnitOfWorkID"],
    all_fields=["UnitOfWorkID", "UnitOfWorkType", "UnitOfWorkPayLoad"],
    requires_workflow_fk=False,
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _row_to_dict(row: Any) -> dict[str, Any]:
    return {
        k: (v.isoformat() if isinstance(v, datetime) else v)
        for k, v in row.__dict__.items()
        if not k.startswith("_")
    }


def _get_active(session: Session, config: EntityConfig, bk_values: dict[str, Any]) -> Any | None:
    return (
        session.query(config.model_class)
        .filter_by(**bk_values, DeleteInd=0)
        .filter(config.model_class.EffToDateTime == HIGH_DATE)
        .first()
    )


def _validate_workflow_active(session: Session, workflow_name: str) -> None:
    active = (
        session.query(Workflow)
        .filter_by(WorkflowName=workflow_name, DeleteInd=0)
        .filter(Workflow.EffToDateTime == HIGH_DATE)
        .first()
    )
    if active is None:
        raise InvalidWorkflowReferenceError(workflow_name)


def _copy_to_hist(config: EntityConfig, active: Any, close_time: datetime, actor: str) -> Any:
    hist_fields = {f: getattr(active, f) for f in config.all_fields}
    return config.hist_class(
        **hist_fields,
        EffFromDateTime=active.EffFromDateTime,
        EffToDateTime=close_time,
        DeleteInd=active.DeleteInd,
        InsertUserName=active.InsertUserName,
        UpdateUserName=actor,
    )


# ---------------------------------------------------------------------------
# Public CRUD operations
# ---------------------------------------------------------------------------

def create_entity(session: Session, config: EntityConfig, params: dict[str, Any], actor: str) -> dict[str, Any]:
    """Insert a new active row. Validates workflow FK and duplicate active key."""
    for key in config.business_keys:
        if not params.get(key):
            raise MissingFieldError(key)

    if config.requires_workflow_fk:
        _validate_workflow_active(session, params["WorkflowName"])

    bk = {k: params[k] for k in config.business_keys}
    if _get_active(session, config, bk) is not None:
        raise DuplicateKeyError(f"An active {config.entity_name} with that key already exists.")

    now = datetime.utcnow()
    row = config.model_class(
        **{f: params.get(f) for f in config.all_fields},
        EffFromDateTime=now,
        EffToDateTime=HIGH_DATE,
        DeleteInd=0,
        InsertUserName=actor,
        UpdateUserName=actor,
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return _row_to_dict(row)


def update_entity(session: Session, config: EntityConfig, params: dict[str, Any], actor: str) -> dict[str, Any]:
    """Close active row → copy to history → insert new current row."""
    for key in config.business_keys:
        if not params.get(key):
            raise MissingFieldError(key)

    bk = {k: params[k] for k in config.business_keys}
    active = _get_active(session, config, bk)
    if active is None:
        raise EntityNotFoundError(config.entity_name, str(bk))

    now = datetime.utcnow()
    session.add(_copy_to_hist(config, active, now, actor))

    # Close the current active row
    active.EffToDateTime = now
    active.UpdateUserName = actor

    # Insert new current row — patch only supplied fields; carry forward the rest
    merged = {f: params.get(f, getattr(active, f)) for f in config.all_fields}
    new_row = config.model_class(
        **merged,
        EffFromDateTime=now,
        EffToDateTime=HIGH_DATE,
        DeleteInd=0,
        InsertUserName=actor,
        UpdateUserName=actor,
    )
    session.add(new_row)
    session.commit()
    session.refresh(new_row)
    return _row_to_dict(new_row)


def get_entity(session: Session, config: EntityConfig, bk_values: dict[str, Any]) -> dict[str, Any]:
    active = _get_active(session, config, bk_values)
    if active is None:
        raise EntityNotFoundError(config.entity_name, str(bk_values))
    return _row_to_dict(active)


def list_entities(
    session: Session,
    config: EntityConfig,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    query = (
        session.query(config.model_class)
        .filter_by(DeleteInd=0)
        .filter(config.model_class.EffToDateTime == HIGH_DATE)
    )
    if filters:
        query = query.filter_by(**filters)
    return [_row_to_dict(r) for r in query.all()]


def delete_entity(
    session: Session,
    config: EntityConfig,
    bk_values: dict[str, Any],
    actor: str,
) -> dict[str, Any]:
    active = _get_active(session, config, bk_values)
    if active is None:
        raise EntityNotFoundError(config.entity_name, str(bk_values))

    now = datetime.utcnow()
    session.add(_copy_to_hist(config, active, now, actor))

    active.DeleteInd = 1
    active.EffToDateTime = now
    active.UpdateUserName = actor

    session.commit()
    return {"deleted": str(bk_values)}
