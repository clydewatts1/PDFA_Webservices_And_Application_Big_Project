# Data Model: Continue PostgreSQL to MySQL Refactor

Feature: 010-postgres-mysql-refactor  
Date: 2026-04-03

## Schema Impact Summary

No functional domain schema redesign is introduced. The workflow model remains:
- Workflow and Workflow_Hist
- Role and Role_Hist
- Interaction and Interaction_Hist
- Guard and Guard_Hist
- InteractionComponent and InteractionComponent_Hist
- UnitOfWork and UnitOfWork_Hist
- Instance and Instance_Hist

SCD requirements remain unchanged:
- Symmetric current and `_Hist` structures.
- Temporal/audit columns preserved: EffFromDateTime, EffToDateTime, DeleteInd, InsertUserName, UpdateUserName.
- MCP server remains owner of current/history transaction orchestration.

## Operational Entities (Planning-Level)

These entities model migration operations and validation state for this feature. They are planning constructs and may be represented via runbook artifacts, CI metadata, or lightweight tracking tables/files as implemented in tasks.

### 1) MigrationValidationRun

Fields:
- run_id (string, required)
- executed_at_utc (datetime, required)
- environment_name (string, required)
- migration_start_revision (string, required)
- migration_end_revision (string, required)
- status (enum: passed, failed, required)
- failure_summary (string, optional)

Validation rules:
- migration_start_revision must be reachable from migration_end_revision.
- status=failed requires failure_summary.

### 2) CutoverWindow

Fields:
- cutover_id (string, required)
- started_at_utc (datetime, required)
- rollback_deadline_utc (datetime, required)
- status (enum: active, committed, rolled_back)
- decision_owner (string, required)

Validation rules:
- rollback_deadline_utc must equal started_at_utc + 24 hours.
- status transitions allowed only as:
  active -> committed
  active -> rolled_back

### 3) RollbackDecision

Fields:
- decision_id (string, required)
- cutover_id (string, required)
- decided_at_utc (datetime, required)
- trigger_reason (enum: migration_failure, health_check_failure, contract_failure, integration_failure, manual_abort)
- approved_by (string, required)
- outcome (enum: rollback_executed, fix_forward)

Validation rules:
- decided_at_utc must be <= related rollback_deadline_utc for rollback_executed.
- outcome=rollback_executed requires CutoverWindow.status to become rolled_back.

## State Transitions

### Cutover lifecycle
1. prepared -> active
2. active -> rolled_back (if failure criteria met within 24 hours)
3. active -> committed (when validation passes and rollback window closes or early commit approved)

### Validation lifecycle
1. required -> passed
2. required -> failed
3. failed -> required (after remediation and rerun)

## Relationships

- One CutoverWindow has many MigrationValidationRun entries.
- One CutoverWindow has zero or more RollbackDecision entries.
- Domain workflow entities are unchanged and independent of operational tracking entities.
