from __future__ import annotations

from datetime import datetime

from sqlalchemy import Index, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from mcp_server.src.models.base import Base, ControlColumnsMixin


class Instance(Base, ControlColumnsMixin):
    __tablename__ = "Instance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    InstanceName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InstanceContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InstanceState: Mapped[str | None] = mapped_column(String(8), nullable=True)
    InstanceStateDate: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    InstanceStartDate: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    InstanceEndDate: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)

    __table_args__ = (
        Index("ix_instance_active", "InstanceName", "DeleteInd", "EffToDateTime"),
    )


class InstanceHist(Base, ControlColumnsMixin):
    __tablename__ = "Instance_Hist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    InstanceName: Mapped[str] = mapped_column(String(128), nullable=False)
    WorkflowName: Mapped[str] = mapped_column(String(128), nullable=False)
    InstanceDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InstanceContextDescription: Mapped[str | None] = mapped_column(Text, nullable=True)
    InstanceState: Mapped[str | None] = mapped_column(String(8), nullable=True)
    InstanceStateDate: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    InstanceStartDate: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    InstanceEndDate: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)

    __table_args__ = (
        Index("ix_instance_hist_name", "InstanceName"),
    )
