"""create current and history tables

Revision ID: 0001_current_history_tables
Revises:
Create Date: 2026-03-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_current_history_tables"
down_revision = None
branch_labels = None
depends_on = None


def _control_columns() -> list[sa.Column]:
    return [
        sa.Column("EffFromDateTime", sa.DateTime(), nullable=False),
        sa.Column("EffToDateTime", sa.DateTime(), nullable=False),
        sa.Column("DeleteInd", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("InsertUserName", sa.String(length=128), nullable=False),
        sa.Column("UpdateUserName", sa.String(length=128), nullable=False),
    ]


def upgrade() -> None:
    for name in [
        "Workflow",
        "Workflow_Hist",
        "Role",
        "Role_Hist",
        "Interaction",
        "Interaction_Hist",
        "Guard",
        "Guard_Hist",
        "InteractionComponent",
        "InteractionComponent_Hist",
        "UnitOfWork",
        "UnitOfWork_Hist",
        "Instance",
        "Instance_Hist",
    ]:
        columns = []

        if name.startswith("Workflow"):
            columns.extend([
                sa.Column("WorkflowName", sa.String(length=128), nullable=False),
                sa.Column("WorkflowDescription", sa.Text(), nullable=True),
                sa.Column("WorkflowContextDescription", sa.Text(), nullable=True),
                sa.Column("WorkflowStateInd", sa.String(length=8), nullable=True),
            ])
        elif name.startswith("Role"):
            columns.extend([
                sa.Column("RoleName", sa.String(length=128), nullable=False),
                sa.Column("WorkflowName", sa.String(length=128), nullable=False),
                sa.Column("InstanceName", sa.String(length=128), nullable=True),
                sa.Column("RoleDescription", sa.Text(), nullable=True),
            ])
        elif name.startswith("Interaction"):
            columns.extend([
                sa.Column("InteractionName", sa.String(length=128), nullable=False),
                sa.Column("WorkflowName", sa.String(length=128), nullable=False),
                sa.Column("InstanceName", sa.String(length=128), nullable=True),
                sa.Column("InteractionDescription", sa.Text(), nullable=True),
            ])
        elif name.startswith("Guard"):
            columns.extend([
                sa.Column("GuardName", sa.String(length=128), nullable=False),
                sa.Column("WorkflowName", sa.String(length=128), nullable=False),
                sa.Column("InstanceName", sa.String(length=128), nullable=True),
                sa.Column("GuardDescription", sa.Text(), nullable=True),
            ])
        elif name.startswith("InteractionComponent"):
            columns.extend([
                sa.Column("InteractionComponentName", sa.String(length=128), nullable=False),
                sa.Column("WorkflowName", sa.String(length=128), nullable=False),
                sa.Column("InstanceName", sa.String(length=128), nullable=True),
                sa.Column("SourceName", sa.String(length=128), nullable=True),
                sa.Column("TargetName", sa.String(length=128), nullable=True),
            ])
        elif name.startswith("UnitOfWork"):
            columns.extend([
                sa.Column("UnitOfWorkID", sa.String(length=128), nullable=False),
                sa.Column("UnitOfWorkType", sa.String(length=64), nullable=True),
                sa.Column("UnitOfWorkPayLoad", sa.Text(), nullable=True),
            ])
        elif name.startswith("Instance"):
            columns.extend([
                sa.Column("InstanceName", sa.String(length=128), nullable=False),
                sa.Column("WorkflowName", sa.String(length=128), nullable=False),
                sa.Column("InstanceState", sa.String(length=8), nullable=True),
                sa.Column("InstanceStateDate", sa.DateTime(), nullable=True),
                sa.Column("InstanceStartDate", sa.DateTime(), nullable=True),
                sa.Column("InstanceEndDate", sa.DateTime(), nullable=True),
            ])

        columns.extend(_control_columns())

        all_columns = [
            sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        ] + columns
        all_columns.append(sa.PrimaryKeyConstraint("id"))

        op.create_table(name, *all_columns)


def downgrade() -> None:
    for name in [
        "Instance_Hist",
        "Instance",
        "UnitOfWork_Hist",
        "UnitOfWork",
        "InteractionComponent_Hist",
        "InteractionComponent",
        "Guard_Hist",
        "Guard",
        "Interaction_Hist",
        "Interaction",
        "Role_Hist",
        "Role",
        "Workflow_Hist",
        "Workflow",
    ]:
        op.drop_table(name)
