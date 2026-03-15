"""SQLAlchemy ORM models for Role, Interaction, Guard, InteractionComponent, UnitOfWork — T021."""
from __future__ import annotations

from sqlalchemy import Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from mcp_server.src.models.base import Base, ControlColumnsMixin


# ---------------------------------------------------------------------------
# Role / Role_Hist
# ---------------------------------------------------------------------------

class Role(Base, ControlColumnsMixin):
    """Current-state table for Role entities. One current row per business key."""

    __tablename__ = "Role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    RoleName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    RoleDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    RoleContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    RoleConfiguration: Mapped[str | None] = mapped_column(Text, nullable=True)
    RoleConfigurationDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    RoleConfigurationContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_role_active", "RoleName", "WorkflowName", "InstanceName", "DeleteInd", "EffToDateTime"),
    )


class RoleHist(Base, ControlColumnsMixin):
    """History-snapshot table for Role entities."""

    __tablename__ = "Role_Hist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    RoleName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    RoleDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    RoleContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    RoleConfiguration: Mapped[str | None] = mapped_column(Text, nullable=True)
    RoleConfigurationDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    RoleConfigurationContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_role_hist_name", "RoleName", "WorkflowName"),
    )


# ---------------------------------------------------------------------------
# Interaction / Interaction_Hist
# ---------------------------------------------------------------------------

class Interaction(Base, ControlColumnsMixin):
    """Current-state table for Interaction entities. One current row per business key."""

    __tablename__ = "Interaction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    InteractionName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    InteractionDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InteractionContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InteractionType: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_interaction_active", "InteractionName", "WorkflowName", "InstanceName", "DeleteInd", "EffToDateTime"),
    )


class InteractionHist(Base, ControlColumnsMixin):
    """History-snapshot table for Interaction entities."""

    __tablename__ = "Interaction_Hist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    InteractionName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    InteractionDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InteractionContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InteractionType: Mapped[str | None] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_interaction_hist_name", "InteractionName", "WorkflowName"),
    )


# ---------------------------------------------------------------------------
# Guard / Guard_Hist
# ---------------------------------------------------------------------------

class Guard(Base, ControlColumnsMixin):
    """Current-state table for Guard entities. One current row per business key."""

    __tablename__ = "Guard"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    GuardName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    GuardDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    GuardContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    GuardType: Mapped[str | None] = mapped_column(String(64), nullable=True)
    GuardConfiguration: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_guard_active", "GuardName", "WorkflowName", "InstanceName", "DeleteInd", "EffToDateTime"),
    )


class GuardHist(Base, ControlColumnsMixin):
    """History-snapshot table for Guard entities."""

    __tablename__ = "Guard_Hist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    GuardName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    GuardDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    GuardContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    GuardType: Mapped[str | None] = mapped_column(String(64), nullable=True)
    GuardConfiguration: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_guard_hist_name", "GuardName", "WorkflowName"),
    )


# ---------------------------------------------------------------------------
# InteractionComponent / InteractionComponent_Hist
# ---------------------------------------------------------------------------

class InteractionComponent(Base, ControlColumnsMixin):
    """Current-state table for InteractionComponent. One current row per business key."""

    __tablename__ = "InteractionComponent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    InteractionComponentName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    InteractionComponentRelationShip: Mapped[str | None] = mapped_column(String(128), nullable=True)
    InteractionComponentDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InteractionComponentContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    SourceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    TargetName: Mapped[str | None] = mapped_column(String(128), nullable=True)

    __table_args__ = (
        Index("ix_ic_active", "InteractionComponentName", "WorkflowName", "InstanceName", "DeleteInd", "EffToDateTime"),
    )


class InteractionComponentHist(Base, ControlColumnsMixin):
    """History-snapshot table for InteractionComponent."""

    __tablename__ = "InteractionComponent_Hist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    InteractionComponentName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    InteractionComponentRelationShip: Mapped[str | None] = mapped_column(String(128), nullable=True)
    InteractionComponentDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InteractionComponentContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    SourceName: Mapped[str | None] = mapped_column(String(128), nullable=True)
    TargetName: Mapped[str | None] = mapped_column(String(128), nullable=True)

    __table_args__ = (
        Index("ix_ic_hist_name", "InteractionComponentName", "WorkflowName"),
    )


# ---------------------------------------------------------------------------
# UnitOfWork / UnitOfWork_Hist  (no WorkflowName FK — intentionally excluded)
# ---------------------------------------------------------------------------

class UnitOfWork(Base, ControlColumnsMixin):
    """Current-state table for UnitOfWork. One current row per UnitOfWorkID."""

    __tablename__ = "UnitOfWork"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UnitOfWorkID: Mapped[str] = mapped_column(String(128), nullable=False)
    UnitOfWorkType: Mapped[str | None] = mapped_column(String(64), nullable=True)
    UnitOfWorkPayLoad: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("UnitOfWorkID", name="uq_unit_of_work_id"),
        Index("ix_uow_active", "DeleteInd", "EffToDateTime"),
    )


class UnitOfWorkHist(Base, ControlColumnsMixin):
    """History-snapshot table for UnitOfWork."""

    __tablename__ = "UnitOfWork_Hist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UnitOfWorkID: Mapped[str] = mapped_column(String(128), nullable=False)
    UnitOfWorkType: Mapped[str | None] = mapped_column(String(64), nullable=True)
    UnitOfWorkPayLoad: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_uow_hist_id", "UnitOfWorkID"),
    )
