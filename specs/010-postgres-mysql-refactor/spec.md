# Feature Specification: Continue PostgreSQL to MySQL Refactor

**Feature Branch**: `010-postgres-mysql-refactor`  
**Created**: 2026-04-03  
**Status**: Draft  
**Input**: User description: "refactor from postgress to mysql - this is a contitutionation of 009"

## Clarifications

### Session 2026-04-03

- Q: Should migration scripts be proactively updated for MySQL compatibility in this feature scope? -> A: Yes, proactively update Alembic migrations for MySQL compatibility as part of this feature.
- Q: What is the required database target for contract and integration suites during migration validation? -> A: Run contract and integration suites on MySQL only.
- Q: What is the data migration strategy for existing PostgreSQL records during cutover? -> A: No data backfill; start MySQL with empty baseline and accept only new post-cutover data.
- Q: What rollback posture should be used after MySQL cutover? -> A: Use a time-boxed rollback window to PostgreSQL if cutover validation checks fail.
- Q: What is the rollback window duration? -> A: 24-hour rollback window.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Complete Runtime Migration (Priority: P1)

As a maintainer, I need all active runtime paths to use MySQL configuration consistently so that production and local runs no longer depend on PostgreSQL-specific settings.

**Why this priority**: This directly determines whether the migration is operationally complete.

**Independent Test**: Set a MySQL `DB_URL`, start MCP and web tier, and verify primary workflows and health checks complete without PostgreSQL dependency errors.

**Acceptance Scenarios**:

1. **Given** the project is configured with a valid MySQL connection URL, **When** MCP runtime starts and handles health checks, **Then** it reports successful database connectivity.
2. **Given** application startup and runtime configuration files, **When** they are reviewed, **Then** no active runtime path requires PostgreSQL-only settings.

---

### User Story 2 - Preserve Functional Behavior and Data Semantics (Priority: P2)

As a maintainer, I need existing workflow behavior and temporal history semantics to remain unchanged after the migration so that business behavior is stable.

**Why this priority**: Migration success is invalid if workflow logic or history behavior regresses.

**Independent Test**: Run contract and integration suites and execute representative create/update/delete workflow operations, verifying current-plus-history behavior remains intact.

**Acceptance Scenarios**:

1. **Given** existing workflow operations are executed, **When** records are created and updated, **Then** current records and historical records reflect the same business outcomes as before migration.
2. **Given** the automated tests that validate workflow behavior, **When** they run after migration updates, **Then** they pass with no new failures caused by database dialect transition.

---

### User Story 3 - Align Documentation and Handover Guidance (Priority: P3)

As a reviewer or new developer, I need project documentation to reflect MySQL as the active database path so setup and verification can be completed without ambiguity.

**Why this priority**: Clear documentation prevents onboarding errors and supports constitutional auditability.

**Independent Test**: Follow documented setup instructions from a clean environment and successfully reach a healthy running state without referring to PostgreSQL instructions.

**Acceptance Scenarios**:

1. **Given** README and feature documents, **When** a reviewer follows the setup steps, **Then** they can configure and run using MySQL instructions only.
2. **Given** active documentation, **When** it is searched for PostgreSQL migration artifacts, **Then** only explicitly historical references remain.

---

### Edge Cases

- MySQL is reachable, but credentials are invalid; startup and health feedback must clearly distinguish authentication failure from network failure.
- Legacy PostgreSQL environment variables persist in local shells; runtime behavior must fail fast with actionable guidance rather than silently misconfiguring.
- Collation or character-set defaults differ between environments; workflow metadata and actor fields must remain readable and uncorrupted.
- Legacy PostgreSQL historical records are not migrated in this feature and remain outside MySQL runtime scope.
- Documentation consumers may start from older feature branches; current branch instructions must clearly identify authoritative MySQL setup guidance.
- Cutover may pass initial startup checks but fail deeper operational checks; rollback eligibility and decision point must be explicit within the rollback window.

## Layer Partition *(mandatory)*

### MCP (Logic)

**Responsibilities**:
- Own all database connection, session, and persistence concerns for the migration continuation.
- Preserve existing MCP tool contract behavior while transitioning all active persistence configuration assumptions to MySQL.
- Maintain temporal current/history orchestration and data integrity guarantees.
- Update and validate Alembic migration scripts for MySQL compatibility as part of migration completion.

**Boundary constraints**:
- SQLAlchemy usage remains confined to MCP server.
- No database-access logic is introduced into Quart route or page layers.

**Impacted contracts**:
- No intentional change to MCP method names, response envelopes, JSON-RPC method contracts, or SSE event semantics.

---

### Web-Tier (Routes)

**Responsibilities**:
- Continue invoking MCP over HTTP contracts only.
- Surface MCP health and domain outcomes without adding database-specific branching.

**Boundary constraints**:
- Routes must not import or manage direct database connection state.
- Route-level behavior remains storage-implementation agnostic.

**Impacted contracts**:
- No route contract changes required for this continuation feature.

---

### Page (UI)

**Responsibilities**:
- Keep user-facing flows stable while backend persistence implementation is finalized.
- Display operational outcomes and errors in a user-comprehensible manner.

**Boundary constraints**:
- No UI component should depend on database dialect details.
- UI behavior remains tied to web-tier API outcomes only.

**Impacted contracts**:
- No page-level payload contract changes are required.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST treat MySQL as the authoritative database runtime target for active application execution paths.
- **FR-002**: The system MUST reject or clearly flag legacy PostgreSQL-only runtime configuration when it would prevent successful operation.
- **FR-003**: MCP health reporting MUST continue to provide explicit success or failure outcomes for database connectivity and operation.
- **FR-004**: Existing workflow operations MUST produce equivalent business outcomes before and after this continuation feature.
- **FR-005**: Temporal tracking behavior for current and historical workflow records MUST remain intact and auditable.
- **FR-006**: Contract and integration verification paths MUST execute against MySQL as part of migration confirmation.
- **FR-007**: Active setup documentation MUST identify MySQL-first configuration and execution steps as the canonical path.
- **FR-008**: Historical PostgreSQL references MAY remain only when clearly labeled as prior-state or archival context.
- **FR-009**: The feature MUST preserve the Database -> MCP Server -> Quart Web Server architecture and avoid cross-layer leakage of persistence concerns.
- **FR-010**: Alembic migration scripts in active use MUST be reviewed and proactively updated where needed to execute correctly against MySQL.
- **FR-011**: Migration execution from baseline to head in a MySQL validation environment MUST complete without dialect-related failures.
- **FR-012**: Existing PostgreSQL data, including historical records, MUST NOT be backfilled into MySQL as part of this feature.
- **FR-013**: Post-cutover MySQL data state MUST begin from the initialized schema baseline, with only new records created after cutover.
- **FR-014**: A 24-hour rollback window to PostgreSQL MUST be defined and documented for use when MySQL cutover validation fails.
- **FR-015**: At rollback-window expiry, operational posture MUST switch to fix-forward on MySQL unless an approved rollback was initiated within the window.

### Key Entities *(include if feature involves data)*

- **Runtime Database Configuration**: Environment-provided connection settings used by MCP to establish persistence sessions.
- **Workflow Current Records**: Active records representing latest state for Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, and Instance entities.
- **Workflow History Records**: `_Hist` records preserving prior states and temporal audit fields for point-in-time traceability.
- **Legacy PostgreSQL Dataset**: Pre-cutover operational records retained in PostgreSQL and excluded from MySQL backfill scope for this feature.
- **Operational Health Result**: Structured status output consumed by routes/pages to represent service and database readiness.

### Assumptions

- This feature continues and finalizes scope initiated in feature 009 rather than introducing a new independent migration strategy.
- Existing MCP and web-tier contracts remain valid and should not require caller-facing shape changes.
- Contract and integration validation environments are provisioned to run against MySQL.
- Stakeholders accept that historical PostgreSQL records remain in the legacy system and are not available in MySQL immediately after cutover.
- Production-like validation environments provide an accessible MySQL instance for runtime confirmation.

### Constitutional Constraints *(mandatory when applicable)*

- **Layer Integrity**: This feature continues migration work without violating the Database -> MCP Server -> Quart Web Server separation.
- **Spec Kit Initiation**: The feature was initiated via Spec Kit workflow and this spec includes MCP (Logic), Web-Tier (Routes), and Page (UI) sections.
- **MCP Contract Stability**: No new JSON-RPC or SSE protocol shape is required; this continuation focuses on persistence migration completion and consistency.
- **Persistence Ownership**: SQLAlchemy remains confined to MCP server ownership and is not introduced in web-tier or page code.
- **Workflow Schema Integrity**: Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, and Instance data integrity is preserved throughout migration continuation.
- **Temporal Symmetry**: Current and `_Hist` tables remain structurally symmetric, preserving `EffFromDateTime`, `EffToDateTime`, `DeleteInd`, `InsertUserName`, and `UpdateUserName` semantics with MCP-owned current/history orchestration.
- **Configuration Expectations**: Runtime environment guidance must clearly indicate MySQL-first configuration and de-emphasize legacy PostgreSQL runtime paths.
- **Migration Continuation Scope**: This continuation explicitly includes migration-script compatibility work for MySQL and is not limited to runtime connection-string updates.
- **Data Cutover Scope**: This continuation excludes historical PostgreSQL data backfill; operational continuity is defined from MySQL cutover forward.
- **Rollback Governance**: Rollback is permitted only within a defined post-cutover validation window and must be driven by explicit validation failure criteria.
- **Attribution and Documentation**: External sources, AI assistance, and specification workflow usage must remain documented in project documentation and feature artifacts.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of designated runtime startup checks for MCP and web-tier succeed with MySQL configuration in the feature validation environment.
- **SC-002**: 100% of selected high-value workflow operations complete with unchanged observable business outcomes compared with pre-continuation baselines.
- **SC-003**: 100% of contract and integration suites designated for this feature execute successfully on MySQL without new database-transition regressions.
- **SC-004**: 100% of active setup documentation reviewed for this feature presents MySQL as the canonical runtime path.
- **SC-005**: 0 unresolved ambiguity items remain in this specification before planning begins.
- **SC-006**: Baseline-to-head Alembic migration run completes successfully on MySQL in the designated validation environment.
- **SC-007**: Cutover validation confirms MySQL starts from initialized schema baseline with no imported pre-cutover PostgreSQL records.
- **SC-008**: Rollback runbook defines a validated decision gate and bounded execution window, and is verified during cutover rehearsal.
- **SC-009**: Operational cutover artifacts explicitly document a 24-hour rollback window and its start/end control points.
