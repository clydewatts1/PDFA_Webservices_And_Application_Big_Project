"""Workflow CRUD service — temporal business logic — T015.

All public functions accept an open SQLAlchemy Session and raise
ServiceError subclasses that handlers map to JSON-RPC error codes.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from mcp_server.src.models.base import HIGH_DATE
from mcp_server.src.models.workflow import Workflow, WorkflowHist


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _active_filter(query, workflow_name: str):
    """Filter to the single active row for *workflow_name*."""
    return query.filter_by(WorkflowName=workflow_name, DeleteInd=0).filter(
        Workflow.EffToDateTime == HIGH_DATE
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


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------

def create_workflow(session: Session, params: dict[str, Any], actor: str) -> dict[str, Any]:
    """Insert a new active Workflow row. Raises DuplicateKeyError if one already exists."""
    workflow_name = params.get("WorkflowName")
    if not workflow_name:
        raise MissingFieldError("WorkflowName")

    existing = _active_filter(session.query(Workflow), workflow_name).first()
    if existing is not None:
        raise DuplicateKeyError()

    now = datetime.utcnow()
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
    """Close the active row, copy it to history, and insert a new current row.

    Raises WorkflowNotFoundError if no active row exists.
    """
    workflow_name = params.get("WorkflowName")
    if not workflow_name:
        raise MissingFieldError("WorkflowName")

    active = _active_filter(session.query(Workflow), workflow_name).first()
    if active is None:
        raise WorkflowNotFoundError(workflow_name)

    now = datetime.utcnow()

    # Copy the prior active row to history before closing it
    hist = WorkflowHist(
        WorkflowName=active.WorkflowName,
        WorkflowDescription=active.WorkflowDescription,
        WorkflowContextDescription=active.WorkflowContextDescription,
        WorkflowStateInd=active.WorkflowStateInd,
        EffFromDateTime=active.EffFromDateTime,
        EffToDateTime=now,
        DeleteInd=active.DeleteInd,
        InsertUserName=active.InsertUserName,
        UpdateUserName=actor,
    )
    session.add(hist)

    # Close the current active row
    active.EffToDateTime = now
    active.UpdateUserName = actor

    # Insert the new current row
    new_row = Workflow(
        WorkflowName=workflow_name,
        WorkflowDescription=params.get("WorkflowDescription", active.WorkflowDescription),
        WorkflowContextDescription=params.get("WorkflowContextDescription", active.WorkflowContextDescription),
        WorkflowStateInd=params.get("WorkflowStateInd", active.WorkflowStateInd),
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


def get_workflow(session: Session, workflow_name: str) -> dict[str, Any]:
    """Return the active row for *workflow_name*. Raises WorkflowNotFoundError if absent."""
    row = _active_filter(session.query(Workflow), workflow_name).first()
    if row is None:
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
    query = session.query(Workflow).filter_by(DeleteInd=0).filter(Workflow.EffToDateTime == HIGH_DATE)
    if offset:
        query = query.offset(offset)
    if limit:
        query = query.limit(limit)
    rows = query.all()
    return [_row_to_dict(r) for r in rows]


def delete_workflow(session: Session, workflow_name: str, actor: str) -> dict[str, Any]:
    """Soft-delete the active Workflow: set DeleteInd=1, close EffToDateTime, copy to history."""
    active = _active_filter(session.query(Workflow), workflow_name).first()
    if active is None:
        raise WorkflowNotFoundError(workflow_name)

    now = datetime.utcnow()

    # Copy to history
    hist = WorkflowHist(
        WorkflowName=active.WorkflowName,
        WorkflowDescription=active.WorkflowDescription,
        WorkflowContextDescription=active.WorkflowContextDescription,
        WorkflowStateInd=active.WorkflowStateInd,
        EffFromDateTime=active.EffFromDateTime,
        EffToDateTime=now,
        DeleteInd=active.DeleteInd,
        InsertUserName=active.InsertUserName,
        UpdateUserName=actor,
    )
    session.add(hist)

    # Mark the current row as deleted and close it
    active.DeleteInd = 1
    active.EffToDateTime = now
    active.UpdateUserName = actor

    session.commit()
    return {"deleted": workflow_name}
