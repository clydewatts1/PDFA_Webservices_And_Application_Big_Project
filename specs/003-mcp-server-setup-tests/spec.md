# Feature Specification: MCP Server Configuration and Test Guide

**Feature Branch**: `003-mcp-server-setup-tests`  
**Created**: 2026-03-14  
**Status**: Draft  
**Input**: User description: "Implement MCP milestone with YAML-based MCP configuration, health/logon/logoff and table CRUD tools, plus a test document for MCP server/database configuration and testing including npx instructions and manual DB/table verification steps"

## Clarifications

### Session 2026-03-14

- Q: Which tables are in scope for mandatory CRUD tooling? → A: Workflow, Role, Interaction, Guard, InteractionComponent.
- Q: What exact MCP YAML filename convention is required? → A: Base name `WB-Workflow-Configuration` with canonical `.yaml` extension.
- Q: How should mock `user_logon` credential validation work? → A: Validate against a small in-memory user map defined in YAML config.
- Q: Which `npx` path is mandatory in the test document? → A: Use `npx @modelcontextprotocol/inspector` for interactive MCP tool verification.
- Q: Which manual DB query path is required for reviewer verification? → A: Primary SQLite CLI (`sqlite3`) path, with optional PostgreSQL `psql` equivalents.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure MCP Runtime from Standardized Inputs (Priority: P1)

As a developer, I need one clear MCP configuration definition and environment-based database connectivity so I can start the server consistently across local environments.

**Why this priority**: Without configuration standardization, no tool behavior can be executed or tested reliably.

**Independent Test**: Can be fully tested by creating the MCP configuration YAML and `.env` values, starting the server, and confirming the startup path resolves configuration without manual code edits.

**Acceptance Scenarios**:

1. **Given** a repository with no active runtime session, **When** a developer provides the defined MCP configuration YAML and `.env` database variables, **Then** the MCP server starts using those sources as the authoritative runtime configuration.
2. **Given** the MCP configuration file name requirement, **When** a reviewer inspects the implementation and docs, **Then** the MCP configuration source and naming convention are explicit and discoverable.

---

### User Story 2 - Execute Core MCP Tools for Health and Access Flow (Priority: P2)

As an operator or reviewer, I need core MCP tools for system health, mock user logon, and user logoff so I can validate operational readiness and basic access flow behavior.

**Why this priority**: These tools provide the minimum operational visibility and interaction expected for milestone verification.

**Independent Test**: Can be fully tested by invoking `get_system_health`, `user_logon`, and `user_logoff` and verifying status fields and error fields match the defined result patterns.

**Acceptance Scenarios**:

1. **Given** an MCP server instance, **When** `get_system_health` is invoked, **Then** the response includes `health_status`, `health_status_description`, and error fields when status is failure-oriented.
2. **Given** valid or invalid mock credentials, **When** `user_logon` is invoked, **Then** the response status is one of `SUCCESS`, `DENIED`, or `ERROR` and includes an error message when required.
3. **Given** a logged-on mock user context, **When** `user_logoff` is invoked, **Then** the response status is `SUCCESS` or `ERROR` with appropriate status detail.

---

### User Story 3 - Perform Table CRUD and Follow End-to-End Test Instructions (Priority: P3)

As a reviewer, I need generic table CRUD tool behavior plus a test document with step-by-step execution instructions (including `npx` usage and direct database/table query checks) so I can validate the milestone without guessing command flows.

**Why this priority**: The user request explicitly requires table CRUD expectations and a testing guide that includes both `npx` instructions and manual direct database verification.

**Independent Test**: Can be fully tested by following the test document to run MCP/database setup, execute create/get/list/update/delete calls for current tables via documented commands, and manually query database tables to verify results, including at least one `npx`-based invocation path.

**Acceptance Scenarios**:

1. **Given** a current table domain, **When** `create_[table]` is invoked with required data, **Then** the tool returns status and status message with the created record outcome.
2. **Given** an existing record key, **When** `get_[table]`, `list_[table]s`, `update_[table]`, and `delete_[table]` are invoked, **Then** each tool returns status and status message with operation-appropriate payloads or errors.
3. **Given** a fresh local environment, **When** a reviewer follows the test document, **Then** the reviewer can configure MCP and database settings and run documented tests (including `npx` commands) end-to-end.
4. **Given** completed tool operations, **When** a reviewer executes documented direct database queries, **Then** the reviewer can manually verify expected table-level data outcomes.

### Edge Cases

- Database connection is unavailable at startup or during health checks.
- MCP configuration YAML is missing, malformed, or missing tool definitions.
- Mock logon requests omit username or password values.
- CRUD tool calls target unknown table names or missing primary key values.
- `list_[table]s` requests provide invalid pagination values.
- `npx` tooling is not installed or available on the reviewer machine.
- Reviewer has MCP tool success responses but cannot reconcile data due to missing manual query guidance.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST define MCP server configuration in `WB-Workflow-Configuration.yaml` (canonical filename; base name `WB-Workflow-Configuration`) containing required MCP resources and tool definitions.
- **FR-002**: The system MUST source database connectivity values from `.env` configuration aligned with `env.example` documentation.
- **FR-003**: The system MUST expose a `get_system_health` tool that checks database connectivity state and returns `health_status`, `health_status_description`, and health error detail fields when applicable.
- **FR-004**: `get_system_health` MUST support status values `CONNECTED`, `DISCONNECTED`, `FAILED`, `INITIALIZING`, and `DEAD`.
- **FR-005**: The system MUST expose a mock `user_logon` tool accepting username and password, validating against a small in-memory user map defined in MCP YAML configuration, and returning status values `SUCCESS`, `DENIED`, or `ERROR` plus an error message field when relevant.
- **FR-006**: The system MUST expose a `user_logoff` tool accepting username and returning status values `SUCCESS` or `ERROR`.
- **FR-007**: For each in-scope table (`Workflow`, `Role`, `Interaction`, `Guard`, `InteractionComponent`), the system MUST provide `create_[table]`, `get_[table]`, `list_[table]s`, `update_[table]`, and `delete_[table]` tools.
- **FR-008**: All CRUD tools MUST return, at minimum, a normalized operation status (`SUCCESS` or `ERROR`) and a status message/error code field.
- **FR-009**: `get_[table]`, `update_[table]`, and `delete_[table]` MUST require the table primary key identifier input.
- **FR-010**: `list_[table]s` MUST accept optional pagination inputs (`limit`, `offset`).
- **FR-011**: The project MUST provide a dedicated test document that describes MCP server setup, database configuration, and end-to-end tool testing steps.
- **FR-012**: The test document MUST include `npx @modelcontextprotocol/inspector` as the required interactive MCP verification path in review workflows.
- **FR-013**: Documentation MUST describe expected failure handling for configuration errors, database connection failures, and invalid tool inputs.
- **FR-014**: The test document MUST include manual instructions for directly querying the database and in-scope tables so reviewers can independently verify tool-operation outcomes at the data level.
- **FR-015**: Manual query verification in the test document MUST provide a primary SQLite CLI (`sqlite3`) procedure and MAY include PostgreSQL `psql` equivalent commands as optional alternatives.

### Key Entities *(include if feature involves data)*

- **MCP Configuration Definition**: YAML-driven definition of MCP server name, resource declarations, and tool contracts.
- **Health Check Result**: Structured response entity with connection status, description, and optional error metadata.
- **Mock Authentication Session Event**: Result of `user_logon` or `user_logoff` interaction with standardized status and message fields.
- **Table Tool Operation Result**: Standardized response wrapper for CRUD operations containing status, status message, and operation payload.
- **Test Runbook**: Reviewer-facing document describing setup prerequisites, environment configuration, command execution (including `npx`), and expected outcomes.

### Constitutional Constraints *(mandatory when applicable)*

- Affected layers include MCP server runtime and documentation; Database -> MCP Server -> Flask Web Server boundaries MUST remain intact.
- MCP tool contract additions are confined to MCP interaction surfaces and do not introduce direct Flask-to-database coupling.
- If persistence interactions are extended for table tools, SQLAlchemy access MUST remain MCP-confined and preserve workflow schema integrity across Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, and Instance.
- Required configuration updates are limited to YAML MCP definition and `.env` database settings documented for reviewers.
- External sources, AI prompts, and Spec Kit usage that influence this feature MUST be recorded in project traceability documents.
- README and directory-level README expectations remain in force for any new setup/testing document introduced by this feature.

## Assumptions

- MCP configuration uses canonical filename `WB-Workflow-Configuration.yaml`.
- Mock authentication flow is non-production and uses a small in-memory YAML-defined user map without secure credential storage in this milestone.
- Current table scope for mandatory CRUD tooling is `Workflow`, `Role`, `Interaction`, `Guard`, and `InteractionComponent`.
- Reviewers have a Node.js runtime capable of executing documented `npx` commands.
- Reviewers have a Node.js runtime capable of running `npx @modelcontextprotocol/inspector`.
- Reviewers can access a local SQLite CLI (`sqlite3`) for primary manual table verification steps.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of required MCP tools (`get_system_health`, `user_logon`, `user_logoff`, and table CRUD set) are documented and invocable through the MCP interface for in-scope tables.
- **SC-002**: 100% of tool responses include standardized status and status-message/error semantics defined by this milestone.
- **SC-003**: A reviewer can complete MCP configuration and database setup from documentation in under 15 minutes without source-code modification.
- **SC-004**: A reviewer can execute the documented test flow (including at least one `npx` command path) and validate expected outcomes for health, auth mock tools, and one full CRUD lifecycle.
- **SC-005**: Configuration or input error scenarios are reproducibly surfaced with explicit failure status and error detail in 100% of tested negative cases.
- **SC-006**: A reviewer can complete manual direct-database verification for at least one end-to-end CRUD flow using the documented table-query instructions without additional undocumented steps.
