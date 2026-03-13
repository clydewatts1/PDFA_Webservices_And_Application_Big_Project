# Feature Specification: Workflow Interaction Schema Foundation

**Feature Branch**: `001-define-workflow-tables`  
**Created**: 2026-03-13  
**Status**: Draft  
**Input**: User description: "Define workflow tables with control columns, current/history snapshots, and instance replication rules for Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, and Instance."

## Clarifications

### Session 2026-03-13

- Q: Should instantiation replicate into fixed tables or create per-instance physical tables? → A: Use fixed current/history tables and store replicated records as instance-scoped rows.
- Q: Should dependent entities use surrogate IDs or workflow-scoped natural/composite keys? → A: Use workflow-scoped natural/composite keys for dependent entities and keep `InstanceName` unique for instances.
- Q: Should this feature require both JSON-RPC and SSE, or JSON-RPC first with SSE deferred? → A: JSON-RPC is required for this feature; SSE is optional and deferred.
- Q: Should updates allow multiple active current rows or enforce one active current row per key? → A: Enforce exactly one active current row per business key and close the prior row on update.
- Q: Is UnitOfWork included in instantiation replication at this stage? → A: No, UnitOfWork is intentionally excluded in this increment.
- Q: What is the active-row criteria? → A: Active row criteria is `DeleteInd=0` and `EffToDateTime=9999-01-01 00:00:00`.
- Q: What should happen on partial failure during instantiation replication? → A: Roll back the entire instance creation transaction.
- Q: How should duplicate temporal rows be handled? → A: Perfect duplicates collapse to one row; partial duplicates keep one current row and set duplicate row with identical from/to timestamps.
- Q: Confirm active/deleted semantics and lifecycle behavior? → A: Active means `DeleteInd=0` with `EffToDateTime=9999-01-01 00:00:00`; delete sets `DeleteInd=1`; reactivation creates a new active row.
- Q: How should historical retrieval work and what environment variables are required in the current phase? → A: There is always one current row; historical retrieval excludes that current row unless explicitly requested, and current-phase environment variables are limited to database/module-create-table needs.
- Q: Is MVP-bounded global uniqueness for `InstanceName` a valid assumption? → A: Yes, this is valid for MVP and may be revisited in later phases.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Maintain Workflow Records with Temporal History (Priority: P1)

As a workflow designer, I need to create and update workflow definitions in a current record set while preserving historical snapshots so that I can safely evolve process definitions over time.

**Why this priority**: Workflow is the root object for all dependent entities and is the minimum demonstrable chunk required to start the project sequence.

**Independent Test**: Can be fully tested by creating a workflow, updating its description/state, and verifying one active current record plus correctly timestamped historical snapshots.

**Acceptance Scenarios**:

1. **Given** no existing workflow with a name, **When** a user creates a workflow with required fields, **Then** the system stores one current record with control columns and no delete marker.
2. **Given** an existing active workflow, **When** the workflow description is updated, **Then** the previous version is captured in the history set and the current set reflects only the latest active version.
3. **Given** an existing workflow, **When** it is logically deleted, **Then** delete status is tracked through `DeleteInd` without losing historical versions.

---

### User Story 2 - Maintain Role/Interaction/Guard/Component Definitions per Workflow (Priority: P2)

As a solution modeler, I need to manage workflow-scoped definitions for roles, interactions, guards, and interaction components so that process behavior is fully described and traceable.

**Why this priority**: These entities are required to express behavior and relationships once workflow maintenance is established.

**Independent Test**: Can be tested by creating one workflow and then creating each dependent entity type linked to that workflow, including updates that produce history snapshots.

**Acceptance Scenarios**:

1. **Given** an active workflow, **When** a role, interaction, guard, and interaction component are created, **Then** each record is linked to the workflow and persists required descriptive/context fields.
2. **Given** an existing guard record, **When** guard configuration is changed, **Then** the updated version becomes current and the prior version is preserved in history.

---

### User Story 3 - Create Runnable Instances with Replicated Operational Definitions (Priority: P3)

As an operator, I need to create a workflow instance that captures runtime state and instance-scoped copies of selected definitions so that execution can proceed without mutating design-time records.

**Why this priority**: Runtime execution depends on completed design-time modeling from User Stories 1 and 2.

**Independent Test**: Can be tested by creating an instance from an existing workflow and verifying instance state fields plus replicated operational records stored as instance-scoped rows in fixed tables.

**Acceptance Scenarios**:

1. **Given** a workflow with roles, interactions, guards, and interaction components, **When** an instance is created, **Then** instance metadata is stored and instance-scoped operational records are generated in fixed tables.
2. **Given** an active instance, **When** instance state changes (active, inactive, paused), **Then** state and state date are updated while preserving start/end date rules.

### Edge Cases

- Duplicate names are submitted for entities with unique keys within the same workflow scope.
- A dependent record (role/interaction/guard/component) is submitted for a workflow that does not exist or is inactive.
- `EffToDateTime` is earlier than `EffFromDateTime`.
- A logical delete is requested for a record already marked deleted.
- A reactivation is requested for a row previously marked deleted.
- Instance creation is requested when required source design-time entities are missing.
- Source and target values in an interaction component reference names that are not valid in the associated workflow scope.
- A perfect duplicate temporal row is received for an existing business key.
- A partial duplicate temporal row is received for an existing business key.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support control columns on all in-scope tables: `EffFromDateTime`, `EffToDateTime`, `DeleteInd`, `InsertUserName`, and `UpdateUserName`.
- **FR-002**: System MUST maintain both current and history datasets for each in-scope table, where history stores previous snapshots and current stores the latest version.
- **FR-003**: System MUST suffix each history dataset with `_Hist`.
- **FR-004**: System MUST store Workflow records with unique `WorkflowName`, plus workflow description, context description, and workflow state indicator.
- **FR-005**: System MUST store Role records linked to `WorkflowName`, including role description, context description, and role configuration fields, using a workflow-scoped composite key (`RoleName`, `WorkflowName`).
- **FR-006**: System MUST store Interaction records linked to `WorkflowName`, including interaction description, context description, and interaction type, using a workflow-scoped composite key (`InteractionName`, `WorkflowName`).
- **FR-007**: System MUST store Guard records linked to `WorkflowName`, including guard description, context description, guard type, and guard configuration, using a workflow-scoped composite key (`GuardName`, `WorkflowName`).
- **FR-008**: System MUST store InteractionComponent records linked to `WorkflowName`, including relationship expression, description, context description, source name, and target name, using a workflow-scoped composite key (`InteractionComponentName`, `WorkflowName`).
- **FR-009**: System MUST store UnitOfWork records with unit identifier, type, and payload.
- **FR-010**: System MUST store Instance records linked to `WorkflowName`, including instance description, context description, state, state date, start date, and end date.
- **FR-011**: System MUST enforce workflow-scoped referential consistency so dependent records cannot exist without a valid parent workflow.
- **FR-012**: System MUST support logical deletion through `DeleteInd` values where `0` means active and `1` means deleted.
- **FR-013**: System MUST replicate Role, Interaction, InteractionComponent, and Guard definitions at instance creation time as instance-scoped rows in fixed current/history tables, while explicitly excluding UnitOfWork in this increment.
- **FR-014**: System MUST allow retrieval of both current and historical versions for each in-scope entity.
- **FR-015**: System MUST NOT create per-instance physical tables at runtime for instantiation.
- **FR-016**: System MUST keep `InstanceName` globally unique for Instance records in MVP scope for this increment.
- **FR-017**: System MUST expose required MCP operations through JSON-RPC contracts for this feature increment.
- **FR-018**: System MAY defer SSE endpoints to a subsequent increment without blocking feature completion.
- **FR-019**: System MUST enforce exactly one active current row per business key and, on update, set `EffToDateTime` on the previously active row before persisting the new current row.
- **FR-020**: System MUST treat a row as active only when `DeleteInd=0` and `EffToDateTime=9999-01-01 00:00:00`.
- **FR-021**: System MUST execute instance creation and dependent-entity replication as a single transaction; any replication failure MUST roll back the entire instance creation.
- **FR-022**: System MUST include `InstanceName` as the required instance-scoping identifier on replicated dependent rows so instance-scoped rows are unambiguous in fixed tables.
- **FR-023**: System MUST handle temporal duplicates as follows: perfect duplicates (all non-tracking columns equal) are collapsed to one row; partial duplicates keep one current row and assign the duplicate row equal `EffFromDateTime` and `EffToDateTime`.
- **FR-024**: System MUST include all control columns (`EffFromDateTime`, `EffToDateTime`, `DeleteInd`, `InsertUserName`, `UpdateUserName`) on each current/history pair: `Workflow`/`Workflow_Hist`, `Role`/`Role_Hist`, `Interaction`/`Interaction_Hist`, `Guard`/`Guard_Hist`, `InteractionComponent`/`InteractionComponent_Hist`, `UnitOfWork`/`UnitOfWork_Hist`, and `Instance`/`Instance_Hist`.
- **FR-025**: System MUST treat a logical delete as a state transition that sets `DeleteInd=1` and closes the row by setting `EffToDateTime` to the deletion timestamp.
- **FR-026**: System MUST treat reactivation as insertion of a new current row for the same business key with `DeleteInd=0`, `EffFromDateTime` equal to reactivation timestamp, and `EffToDateTime=9999-01-01 00:00:00`.
- **FR-027**: System MUST NOT overwrite prior deleted rows during reactivation; prior versions remain preserved in history.
- **FR-028**: System MUST enforce retrieval semantics where each business key has exactly one current row, and history retrieval returns only closed versions (`EffToDateTime` not equal to `9999-01-01 00:00:00`) unless the caller explicitly requests inclusion of current rows.
- **FR-029**: For the current phase (build module to create tables), required environment variables are limited to database configuration needed for migrations/schema creation; MCP/Flask service URL variables are deferred to later phases.

### Key Entities *(include if feature involves data)*

- **Workflow**: Root process definition identified by `WorkflowName`, with human and context descriptions plus lifecycle state.
- **Role**: Workflow-scoped responsibility definition with configuration and descriptive metadata.
- **Interaction**: Workflow-scoped communication definition describing interaction behavior/type.
- **Guard**: Workflow-scoped conditional rule with type and configuration.
- **InteractionComponent**: Workflow-scoped directional relationship descriptor connecting source and target names.
- **UnitOfWork**: Discrete work item representation with type and payload.
- **Instance**: Runtime workflow execution record with lifecycle timestamps and state.
- **HistoricalSnapshot**: Versioned copy of an entity record preserved in a matching `_Hist` dataset.

### Constitutional Constraints *(mandatory when applicable)*

- This feature affects the database and MCP server layers; the Flask layer consumes only MCP contracts and does not define persistence behavior directly.
- All required operations for this feature are exposed via MCP-over-HTTP JSON-RPC interfaces; SSE may be added later for streaming visibility.
- Persistence and relationship enforcement remain within the MCP tier only, preserving constitutional separation from the Flask tier.
- Environment variables must provide database connectivity and MCP endpoint configuration for environments used during specification, planning, and implementation.
- Environment-variable requirements are phase-scoped: this phase requires only database configuration for schema/migration work; MCP/Flask endpoint variables are introduced in later phases.
- External-source references for this feature include project prompts/specification notes and Spec Kit workflows; these must be cited in documentation updates produced during implementation.

## Assumptions

- Name fields marked as primary keys are treated as unique within their defined scope (global for workflow and instance, workflow-scoped composite keys for dependent entities).
- `DeleteInd` supports `0` (active) and `1` (deleted) in this increment.
- Snapshot behavior follows a slowly changing dimension style where the previous current row is copied to history before replacement.
- Instance replication copies design-time records as an initialization baseline into fixed tables and does not overwrite design-time definitions.
- Active current windows for the same business key do not overlap.
- High-date sentinel for active rows is `9999-01-01 00:00:00`.
- UnitOfWork is not replicated during instantiation in this increment.
- Global uniqueness of `InstanceName` is treated as an MVP assumption and can be redesigned in later phases if scale requirements change.
- Historical reads return closed versions by default; current rows are included only when explicitly requested.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of create/update/delete operations for in-scope entities persist required control-column values.
- **SC-002**: 100% of successful updates result in one new historical snapshot and one current active version for the affected entity.
- **SC-006**: 100% of tested updates close the prior active row (`EffToDateTime` populated) before the replacement current row is activated.
- **SC-007**: 100% of tested active-current rows satisfy `DeleteInd=0` and `EffToDateTime=9999-01-01 00:00:00`.
- **SC-003**: In validation testing, 100% of dependent entity writes fail with clear feedback when parent workflow validity rules are violated.
- **SC-004**: A new instance can be created from a valid workflow in under 30 seconds including replication of role, interaction, guard, and interaction component baseline records.
- **SC-005**: At least 95% of test participants can complete workflow definition plus dependent-entity setup without external assistance using documented field definitions.
- **SC-008**: 100% of simulated partial failures during instantiation result in no persisted instance or replicated dependent rows.
