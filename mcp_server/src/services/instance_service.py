"""Instance lifecycle service and replication orchestration.

This module manages instance creation, state transitions, and transactional
replication of design-time dependent records into instance-scoped rows.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from mcp_server.src.models.base import HIGH_DATE
from mcp_server.src.models.dependent import (
    Guard,
    Interaction,
    InteractionComponent,
    Role,
)
from mcp_server.src.models.instance import Instance, InstanceHist
from mcp_server.src.models.workflow import Workflow
from mcp_server.src.services.workflow_service import (
    DuplicateKeyError,
    MissingFieldError,
    ServiceError,
    WorkflowNotFoundError,
)
from mcp_server.src.services.validation import validate_instance_state


class InstanceNotFoundError(ServiceError):
    """Raised when an active instance cannot be located by name."""

    def __init__(self, instance_name: str) -> None:
        super().__init__(f"Instance '{instance_name}' not found or not active.", code="instance_not_found")


def _active_workflow(session: Session, workflow_name: str) -> Workflow | None:
    """Return the active workflow row for the supplied workflow name."""

    return (
        session.query(Workflow)
        .filter_by(WorkflowName=workflow_name, DeleteInd=0)
        .filter(Workflow.EffToDateTime == HIGH_DATE)
        .first()
    )


def _active_instance(session: Session, instance_name: str) -> Instance | None:
    """Return the active instance row for the supplied instance name."""

    return (
        session.query(Instance)
        .filter_by(InstanceName=instance_name, DeleteInd=0)
        .filter(Instance.EffToDateTime == HIGH_DATE)
        .first()
    )


def _instance_to_dict(row: Instance) -> dict[str, Any]:
    """Serialize an instance ORM row to an API-safe dictionary."""

    return {
        "InstanceName": row.InstanceName,
        "WorkflowName": row.WorkflowName,
        "InstanceDescription": row.InstanceDescription,
        "InstanceContextDescription": row.InstanceContextDescription,
        "InstanceState": row.InstanceState,
        "InstanceStateDate": row.InstanceStateDate.isoformat() if row.InstanceStateDate else None,
        "InstanceStartDate": row.InstanceStartDate.isoformat() if row.InstanceStartDate else None,
        "InstanceEndDate": row.InstanceEndDate.isoformat() if row.InstanceEndDate else None,
        "EffFromDateTime": row.EffFromDateTime.isoformat() if row.EffFromDateTime else None,
        "EffToDateTime": row.EffToDateTime.isoformat() if row.EffToDateTime else None,
        "DeleteInd": row.DeleteInd,
        "InsertUserName": row.InsertUserName,
        "UpdateUserName": row.UpdateUserName,
    }


def _copy_instance_to_hist(row: Instance, close_time: datetime, actor: str) -> InstanceHist:
    """Create a history snapshot from the active instance row."""

    return InstanceHist(
        InstanceName=row.InstanceName,
        WorkflowName=row.WorkflowName,
        InstanceDescription=row.InstanceDescription,
        InstanceContextDescription=row.InstanceContextDescription,
        InstanceState=row.InstanceState,
        InstanceStateDate=row.InstanceStateDate,
        InstanceStartDate=row.InstanceStartDate,
        InstanceEndDate=row.InstanceEndDate,
        EffFromDateTime=row.EffFromDateTime,
        EffToDateTime=close_time,
        DeleteInd=row.DeleteInd,
        InsertUserName=row.InsertUserName,
        UpdateUserName=actor,
    )


def _replicate_rows(session: Session, model_class: type, fields: list[str], workflow_name: str, instance_name: str, actor: str, now: datetime) -> int:
    """Replicate active design-time rows into instance-scoped current rows."""

    source_rows = (
        session.query(model_class)
        .filter_by(WorkflowName=workflow_name, DeleteInd=0, InstanceName=None)
        .filter(model_class.EffToDateTime == HIGH_DATE)
        .all()
    )
    for src in source_rows:
        payload = {f: getattr(src, f, None) for f in fields}
        payload["InstanceName"] = instance_name
        row = model_class(
            **payload,
            EffFromDateTime=now,
            EffToDateTime=HIGH_DATE,
            DeleteInd=0,
            InsertUserName=actor,
            UpdateUserName=actor,
        )
        session.add(row)
    return len(source_rows)


def create_instance(session: Session, params: dict[str, Any], actor: str) -> dict[str, Any]:
    """Create a new instance and replicate dependent design-time records.

    The operation runs inside a transactional boundary; replication failures
    roll back instance creation.
    """

    instance_name = params.get("InstanceName")
    workflow_name = params.get("WorkflowName")
    if not instance_name:
        raise MissingFieldError("InstanceName")
    if not workflow_name:
        raise MissingFieldError("WorkflowName")

    state = params.get("InstanceState", "A")
    validate_instance_state(state)

    if _active_instance(session, instance_name) is not None:
        raise DuplicateKeyError("An active instance with that name already exists.")

    if _active_workflow(session, workflow_name) is None:
        raise WorkflowNotFoundError(workflow_name)

    now = datetime.utcnow()

    try:
        with session.begin_nested():
            instance = Instance(
                InstanceName=instance_name,
                WorkflowName=workflow_name,
                InstanceDescription=params.get("InstanceDescription"),
                InstanceContextDescription=params.get("InstanceContextDescription"),
                InstanceState=state,
                InstanceStateDate=now,
                InstanceStartDate=now,
                InstanceEndDate=None,
                EffFromDateTime=now,
                EffToDateTime=HIGH_DATE,
                DeleteInd=0,
                InsertUserName=actor,
                UpdateUserName=actor,
            )
            session.add(instance)

            role_count = _replicate_rows(
                session,
                Role,
                [
                    "RoleName", "WorkflowName", "RoleDescription", "RoleContextDescription",
                    "RoleConfiguration", "RoleConfigurationDescription", "RoleConfigurationContextDescription",
                ],
                workflow_name,
                instance_name,
                actor,
                now,
            )
            interaction_count = _replicate_rows(
                session,
                Interaction,
                [
                    "InteractionName", "WorkflowName", "InteractionDescription",
                    "InteractionContextDescription", "InteractionType",
                ],
                workflow_name,
                instance_name,
                actor,
                now,
            )
            guard_count = _replicate_rows(
                session,
                Guard,
                [
                    "GuardName", "WorkflowName", "GuardDescription", "GuardContextDescription",
                    "GuardType", "GuardConfiguration",
                ],
                workflow_name,
                instance_name,
                actor,
                now,
            )
            ic_count = _replicate_rows(
                session,
                InteractionComponent,
                [
                    "InteractionComponentName", "WorkflowName", "InteractionComponentRelationShip",
                    "InteractionComponentDescription", "InteractionComponentContextDescription",
                    "SourceName", "TargetName",
                ],
                workflow_name,
                instance_name,
                actor,
                now,
            )

        session.commit()
        session.refresh(instance)
        out = _instance_to_dict(instance)
        out["replication"] = {
            "roles": role_count,
            "interactions": interaction_count,
            "guards": guard_count,
            "interaction_components": ic_count,
        }
        return out
    except Exception:
        session.rollback()
        raise


def update_instance_state(session: Session, params: dict[str, Any], actor: str) -> dict[str, Any]:
    """Transition instance state by closing current row and inserting replacement."""

    instance_name = params.get("InstanceName")
    new_state = params.get("InstanceState")
    if not instance_name:
        raise MissingFieldError("InstanceName")
    if not new_state:
        raise MissingFieldError("InstanceState")
    validate_instance_state(new_state)

    active = _active_instance(session, instance_name)
    if active is None:
        raise InstanceNotFoundError(instance_name)

    now = datetime.utcnow()
    session.add(_copy_instance_to_hist(active, now, actor))

    active.EffToDateTime = now
    active.UpdateUserName = actor

    end_date = params.get("InstanceEndDate")
    if new_state in ("I", "P") and end_date is None:
        end_date = now

    replacement = Instance(
        InstanceName=active.InstanceName,
        WorkflowName=active.WorkflowName,
        InstanceDescription=params.get("InstanceDescription", active.InstanceDescription),
        InstanceContextDescription=params.get("InstanceContextDescription", active.InstanceContextDescription),
        InstanceState=new_state,
        InstanceStateDate=now,
        InstanceStartDate=active.InstanceStartDate,
        InstanceEndDate=end_date,
        EffFromDateTime=now,
        EffToDateTime=HIGH_DATE,
        DeleteInd=0,
        InsertUserName=actor,
        UpdateUserName=actor,
    )
    session.add(replacement)
    session.commit()
    session.refresh(replacement)
    return _instance_to_dict(replacement)


def get_instance(session: Session, instance_name: str) -> dict[str, Any]:
    """Return the active instance payload for the specified instance name."""

    active = _active_instance(session, instance_name)
    if active is None:
        raise InstanceNotFoundError(instance_name)
    return _instance_to_dict(active)


def list_instances(session: Session, workflow_name: str | None = None) -> list[dict[str, Any]]:
    """List active instances, optionally filtered by workflow name."""

    query = session.query(Instance).filter_by(DeleteInd=0).filter(Instance.EffToDateTime == HIGH_DATE)
    if workflow_name:
        query = query.filter_by(WorkflowName=workflow_name)
    return [_instance_to_dict(r) for r in query.all()]
