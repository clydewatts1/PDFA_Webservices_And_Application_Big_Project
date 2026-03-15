"""Workflow CRUD service — current-state plus history — T015.

All public functions accept an open SQLAlchemy Session and raise
ServiceError subclasses that handlers map to JSON-RPC error codes.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from mcp_server.src.models.base import HIGH_DATE, utcnow_naive
from mcp_server.src.models.workflow import Workflow, WorkflowHist


class ServiceError(ValueError):
    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


class DuplicateKeyError(ServiceError):
    def __init__(self, message: str = "An active workflow with that name already exists.") -> None:
        super().__init__(message, code="duplicate_active_key")


class WorkflowNotFoundError(ServiceError):
    def __init__(self, workflow_name: str) -> None:
        super().__init__(f"Workflow '{workflow_name}' not found or not active.", code="workflow_not_found")


class MissingFieldError(ServiceError):
    def __init__(self, field: str) -> None:
        super().__init__(f"Required field missing: {field}", code="missing_required_field")


def _current_row(session: Session, workflow_name: str) -> Workflow | None:
    return session.query(Workflow).filter_by(WorkflowName=workflow_name).first()


def _active_filter(query):
    return query.filter_by(DeleteInd=0).filter(Workflow.EffToDateTime == HIGH_DATE)


def _snapshot_to_hist(row: Workflow, close_time, actor: str) -> WorkflowHist:
    return WorkflowHist(
        WorkflowName=row.WorkflowName,
        WorkflowDescription=row.WorkflowDescription,
        WorkflowContextDescription=row.WorkflowContextDescription,
        WorkflowStateInd=row.WorkflowStateInd,
        EffFromDateTime=row.EffFromDateTime,
        EffToDateTime=close_time,
        DeleteInd=row.DeleteInd,
        InsertUserName=row.InsertUserName,
        UpdateUserName=actor,
    )


def _row_to_dict(row: Workflow) -> dict[str, Any]:
    return {
        "WorkflowName": row.WorkflowName,
        "WorkflowDescription": row.WorkflowDescription,
        "WorkflowContextDescription": row.WorkflowContextDescription,
        "WorkflowStateInd": row.WorkflowStateInd,
        "EffFromDateTime": row.EffFromDateTime.isoformat() if row.EffFromDateTime else None,
        "EffToDateTime": row.EffToDateTime.isoformat() if row.EffToDateTime else None,
        "DeleteInd": row.DeleteInd,
        "InsertUserName": row.InsertUserName,
        "UpdateUserName": row.UpdateUserName,
    }


def _validate_pagination(limit: int | None, offset: int | None) -> tuple[int | None, int | None]:
    """Validate optional pagination fields and normalize integer values."""

    if limit is not None and (not isinstance(limit, int) or limit <= 0):
        raise ServiceError("limit must be a positive integer", code="invalid_pagination")
    if offset is not None and (not isinstance(offset, int) or offset < 0):
        raise ServiceError("offset must be a non-negative integer", code="invalid_pagination")
    return limit, offset


def create_workflow(session: Session, params: dict[str, Any], actor: str) -> dict[str, Any]:
    """Insert a new current Workflow row. Raises DuplicateKeyError if one already exists."""
    workflow_name = params.get("WorkflowName")
    if not workflow_name:
        raise MissingFieldError("WorkflowName")

    existing = _current_row(session, workflow_name)
    if existing is not None:
        raise DuplicateKeyError()

    now = utcnow_naive()
    row = Workflow(
        WorkflowName=workflow_name,
        WorkflowDescription=params.get("WorkflowDescription"),
        WorkflowContextDescription=params.get("WorkflowContextDescription"),
        WorkflowStateInd=params.get("WorkflowStateInd", "A"),
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


def update_workflow(session: Session, params: dict[str, Any], actor: str) -> dict[str, Any]:
    """Copy the current row to history and update the primary current row in place.

    Raises WorkflowNotFoundError if no current row exists.
    """
    workflow_name = params.get("WorkflowName")
    if not workflow_name:
        raise MissingFieldError("WorkflowName")

    row = _current_row(session, workflow_name)
    if row is None:
        raise WorkflowNotFoundError(workflow_name)

    now = utcnow_naive()
    session.add(_snapshot_to_hist(row, now, actor))

    row.WorkflowDescription = params.get("WorkflowDescription", row.WorkflowDescription)
    row.WorkflowContextDescription = params.get("WorkflowContextDescription", row.WorkflowContextDescription)
    row.WorkflowStateInd = params.get("WorkflowStateInd", row.WorkflowStateInd)
    row.EffFromDateTime = now
    row.EffToDateTime = HIGH_DATE
    row.DeleteInd = 0
    row.UpdateUserName = actor

    session.commit()
    session.refresh(row)
    return _row_to_dict(row)


def get_workflow(session: Session, workflow_name: str) -> dict[str, Any]:
    """Return the active row for *workflow_name*. Raises WorkflowNotFoundError if absent."""
    row = _current_row(session, workflow_name)
    if row is None or row.DeleteInd != 0:
        raise WorkflowNotFoundError(workflow_name)
    return _row_to_dict(row)


def list_workflows(
    session: Session,
    *,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict[str, Any]]:
    """Return all active Workflow rows."""
    limit, offset = _validate_pagination(limit, offset)
    query = _active_filter(session.query(Workflow))
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    return [_row_to_dict(r) for r in query.all()]


def delete_workflow(session: Session, workflow_name: str, actor: str) -> dict[str, Any]:
    """Soft-delete the current Workflow after writing its prior state to history."""
    row = _current_row(session, workflow_name)
    if row is None or row.DeleteInd != 0:
        raise WorkflowNotFoundError(workflow_name)

    now = utcnow_naive()
    session.add(_snapshot_to_hist(row, now, actor))

    row.DeleteInd = 1
    row.EffToDateTime = now
    row.UpdateUserName = actor

    session.commit()
    return {"deleted": workflow_name}
