"""SQLAlchemy ORM models for Workflow and Workflow_Hist tables — T014."""
from __future__ import annotations

from sqlalchemy import Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mcp_server.src.models.base import Base, ControlColumnsMixin


class Workflow(Base, ControlColumnsMixin):
    """Current-state table for Workflow entities.

    Business key: WorkflowName.
    Exactly one row exists per WorkflowName in this table.
    Historical versions are written to Workflow_Hist.
    """

    __tablename__ = "Workflow"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    WorkflowContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    WorkflowStateInd: Mapped[str | None] = mapped_column(String(8), nullable=True, default="A")

    __table_args__ = (
        UniqueConstraint("WorkflowName", name="uq_workflow_name"),
        Index("ix_workflow_active", "DeleteInd", "EffToDateTime"),
    )


class WorkflowHist(Base, ControlColumnsMixin):
    """History-snapshot table for Workflow entities.

    A row is written here whenever an active Workflow row is closed (update or delete).
    Mirrors the column set of Workflow; surrogate PK keeps inserts idempotent.
    """

    __tablename__ = "Workflow_Hist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    WorkflowContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    WorkflowStateInd: Mapped[str | None] = mapped_column(String(8), nullable=True)

    __table_args__ = (
        Index("ix_workflow_hist_name", "WorkflowName"),
    )
