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
    op.create_table("Workflow",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowDescription", sa.Text(), nullable=True),
        sa.Column("WorkflowContextDescription", sa.Text(), nullable=True),
        sa.Column("WorkflowStateInd", sa.String(length=8), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Workflow_Hist",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowDescription", sa.Text(), nullable=True),
        sa.Column("WorkflowContextDescription", sa.Text(), nullable=True),
        sa.Column("WorkflowStateInd", sa.String(length=8), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Role",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("RoleName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=True),
        sa.Column("RoleDescription", sa.Text(), nullable=True),
        sa.Column("RoleContextDescription", sa.Text(), nullable=True),
        sa.Column("RoleConfiguration", sa.Text(), nullable=True),
        sa.Column("RoleConfigurationDescription", sa.Text(), nullable=True),
        sa.Column("RoleConfigurationContextDescription", sa.Text(), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Role_Hist",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("RoleName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=True),
        sa.Column("RoleDescription", sa.Text(), nullable=True),
        sa.Column("RoleContextDescription", sa.Text(), nullable=True),
        sa.Column("RoleConfiguration", sa.Text(), nullable=True),
        sa.Column("RoleConfigurationDescription", sa.Text(), nullable=True),
        sa.Column("RoleConfigurationContextDescription", sa.Text(), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Interaction",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("InteractionName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=True),
        sa.Column("InteractionDescription", sa.Text(), nullable=True),
        sa.Column("InteractionContextDescription", sa.Text(), nullable=True),
        sa.Column("InteractionType", sa.String(length=64), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Interaction_Hist",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("InteractionName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=True),
        sa.Column("InteractionDescription", sa.Text(), nullable=True),
        sa.Column("InteractionContextDescription", sa.Text(), nullable=True),
        sa.Column("InteractionType", sa.String(length=64), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Guard",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("GuardName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=True),
        sa.Column("GuardDescription", sa.Text(), nullable=True),
        sa.Column("GuardContextDescription", sa.Text(), nullable=True),
        sa.Column("GuardType", sa.String(length=64), nullable=True),
        sa.Column("GuardConfiguration", sa.Text(), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Guard_Hist",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("GuardName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=True),
        sa.Column("GuardDescription", sa.Text(), nullable=True),
        sa.Column("GuardContextDescription", sa.Text(), nullable=True),
        sa.Column("GuardType", sa.String(length=64), nullable=True),
        sa.Column("GuardConfiguration", sa.Text(), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("InteractionComponent",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("InteractionComponentName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=True),
        sa.Column("InteractionComponentRelationShip", sa.Text(), nullable=True),
        sa.Column("InteractionComponentDescription", sa.Text(), nullable=True),
        sa.Column("InteractionComponentContextDescription", sa.Text(), nullable=True),
        sa.Column("SourceName", sa.String(length=128), nullable=True),
        sa.Column("TargetName", sa.String(length=128), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("InteractionComponent_Hist",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("InteractionComponentName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=True),
        sa.Column("InteractionComponentRelationShip", sa.Text(), nullable=True),
        sa.Column("InteractionComponentDescription", sa.Text(), nullable=True),
        sa.Column("InteractionComponentContextDescription", sa.Text(), nullable=True),
        sa.Column("SourceName", sa.String(length=128), nullable=True),
        sa.Column("TargetName", sa.String(length=128), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("UnitOfWork",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("UnitOfWorkID", sa.String(length=128), nullable=False),
        sa.Column("UnitOfWorkType", sa.String(length=64), nullable=True),
        sa.Column("UnitOfWorkPayLoad", sa.Text(), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("UnitOfWork_Hist",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("UnitOfWorkID", sa.String(length=128), nullable=False),
        sa.Column("UnitOfWorkType", sa.String(length=64), nullable=True),
        sa.Column("UnitOfWorkPayLoad", sa.Text(), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Instance",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceDescription", sa.Text(), nullable=True),
        sa.Column("InstanceContextDescription", sa.Text(), nullable=True),
        sa.Column("InstanceState", sa.String(length=8), nullable=True),
        sa.Column("InstanceStateDate", sa.DateTime(), nullable=True),
        sa.Column("InstanceStartDate", sa.DateTime(), nullable=True),
        sa.Column("InstanceEndDate", sa.DateTime(), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table("Instance_Hist",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("InstanceName", sa.String(length=128), nullable=False),
        sa.Column("WorkflowName", sa.String(length=128), nullable=False),
        sa.Column("InstanceDescription", sa.Text(), nullable=True),
        sa.Column("InstanceContextDescription", sa.Text(), nullable=True),
        sa.Column("InstanceState", sa.String(length=8), nullable=True),
        sa.Column("InstanceStateDate", sa.DateTime(), nullable=True),
        sa.Column("InstanceStartDate", sa.DateTime(), nullable=True),
        sa.Column("InstanceEndDate", sa.DateTime(), nullable=True),
        *_control_columns(),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    for name in [
        "Instance_Hist", "Instance",
        "UnitOfWork_Hist", "UnitOfWork",
        "InteractionComponent_Hist", "InteractionComponent",
        "Guard_Hist", "Guard",
        "Interaction_Hist", "Interaction",
        "Role_Hist", "Role",
        "Workflow_Hist", "Workflow",
    ]:
        op.drop_table(name)