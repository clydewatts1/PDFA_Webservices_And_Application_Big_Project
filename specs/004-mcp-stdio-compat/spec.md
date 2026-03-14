# Feature Specification: MCP Stdio Inspector Compatibility

**Feature Branch**: `004-mcp-stdio-compat`  
**Created**: 2026-03-14  
**Status**: Draft  
**Input**: User description: "Build a production-valid Model Context Protocol (MCP) server milestone that is fully compatible with npx @modelcontextprotocol/inspector and supports health, auth, and CRUD tool workflows for the current workflow domain."

## Clarifications

### Session 2026-03-14

- Q: Which CRUD MCP tool naming style is canonical for this milestone? → A: Preserve dotted names (`workflow.create`, `role.get`, etc.).
- Q: What is the canonical Inspector stdio launch command for this milestone? → A: `python -m mcp_server.src.server` using a dedicated MCP stdio entrypoint.
- Q: Which MCP transport scope is required for this milestone? → A: Both stdio and HTTP/SSE transports are required.
- Q: What mock authentication model is required for this milestone? → A: Keep YAML plain-text mock credentials for non-production testing only with explicit non-production disclaimer.
- Q: How must behavior differ between stdio and HTTP/SSE transports? → A: No behavior difference; both transports must expose the same tool set and status semantics.
- Q: What are the canonical MCP transport endpoints and payload rules? → A: Use stdio launch command python -m mcp_server.src.server; expose HTTP JSON-RPC at POST /rpc (JSON-RPC 2.0 envelope: jsonrpc, id, method, params); expose SSE at GET /sse (text/event-stream) with events ready, tool_result, error, and heartbeat; enforce equivalent business-semantic outcomes across stdio, HTTP JSON-RPC, and SSE for equivalent tool inputs.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Connect Inspector to MCP Server (Priority: P1)

As a reviewer, I need to launch the MCP server using a standard command and connect to it from MCP Inspector via stdio so I can validate the milestone without custom adapters.

**Why this priority**: If Inspector cannot connect and discover tools, none of the milestone verification flow is possible.

**Independent Test**: Can be fully tested by launching the documented stdio server command, opening Inspector, and confirming successful connection plus tool discovery.

**Acceptance Scenarios**:

1. **Given** a configured local environment, **When** the reviewer starts the MCP server using the documented stdio command and opens Inspector, **Then** Inspector connects successfully with no source-code modification.
2. **Given** an active Inspector session, **When** tools are listed, **Then** the required health, auth, and in-scope CRUD tool families are discoverable.

---

### User Story 2 - Verify Health and Auth Contract Behavior (Priority: P2)

As an operator, I need `get_system_health`, `user_logon`, and `user_logoff` tools to return deterministic statuses and error semantics so I can verify readiness and basic access flow behavior.

**Why this priority**: Core operational verification depends on health and auth behavior before deeper CRUD validation.

**Independent Test**: Can be fully tested by invoking health/auth tools through Inspector with valid and invalid inputs and checking expected status outcomes.

**Acceptance Scenarios**:

1. **Given** a running MCP server and reachable database, **When** `get_system_health` is invoked, **Then** the response includes health status fields and appropriate failure details when unhealthy.
2. **Given** valid and invalid credentials from the mock user map, **When** `user_logon` is invoked, **Then** statuses align to `SUCCESS`, `DENIED`, or `ERROR` according to input validity and credential match.
3. **Given** a valid username, **When** `user_logoff` is invoked, **Then** the response returns `SUCCESS` or `ERROR` with clear status details.

---

### User Story 3 - Execute CRUD and Manually Verify Data Outcomes (Priority: P3)

As a reviewer, I need to run CRUD operations for the current workflow-domain tables and verify outcomes directly in the database so I can confirm the milestone behavior end-to-end.

**Why this priority**: CRUD verification plus direct table checks confirms that tool outputs match actual persisted outcomes.

**Independent Test**: Can be fully tested by running one complete CRUD lifecycle through Inspector and validating resulting rows via manual database queries.

**Acceptance Scenarios**:

1. **Given** in-scope tables, **When** create/get/list/update/delete tools are invoked from Inspector, **Then** each operation returns normalized status and status-message semantics.
2. **Given** successful CRUD operations, **When** the reviewer runs documented SQLite direct queries, **Then** expected create/update/delete outcomes are visible in table data.
3. **Given** a PostgreSQL environment, **When** the reviewer uses optional equivalent queries, **Then** verification remains consistent with SQLite outcomes.

### Edge Cases

- Inspector cannot connect because the wrong transport or launch command is used.
- MCP configuration file is missing, malformed, or does not include required tool definitions.
- Database is unavailable during startup or becomes unavailable during tool execution.
- `user_logon` receives missing fields or malformed payloads.
- CRUD tools receive missing primary key values, invalid pagination values, or out-of-scope table requests.
- Reviewer environment is missing `npx` or SQLite CLI.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide standards-compliant MCP transport support for all of the following: stdio, HTTP JSON-RPC, and SSE. Stdio is mandatory for Inspector compatibility.
- **FR-002**: The documented inspector workflow MUST use `npx @modelcontextprotocol/inspector` and include explicit stdio server command configuration.
- **FR-002A**: The canonical stdio launch command for Inspector workflows MUST be python -m mcp_server.src.server.
- **FR-002B**: HTTP JSON-RPC MUST be exposed at POST /rpc and accept JSON-RPC 2.0 requests with fields jsonrpc, id, method, and optional params.
- **FR-002C**: HTTP JSON-RPC success responses MUST return JSON-RPC 2.0 result; errors MUST return JSON-RPC 2.0 error with code, message, and optional data.
- **FR-002D**: SSE MUST be exposed at GET /sse with text/event-stream and MUST emit events ready, tool_result, error, and heartbeat.
- **FR-002E**: SSE tool_result events MUST include, at minimum, request_id, method, status, and status_message.
- **FR-002F**: For equivalent tool inputs, stdio, HTTP JSON-RPC, and SSE MUST return equivalent business-semantic outcomes (status, status_message, and required tool fields), excluding transport metadata such as timestamps or connection identifiers.
- **FR-002G**: Transport-level invalid requests MUST produce deterministic failures: invalid JSON-RPC envelope, unknown method, and missing required parameters MUST each map to documented error outcomes.

- **FR-003**: Inspector tool discovery MUST include `get_system_health`, `user_logon`, `user_logoff`, and dotted-name CRUD tool families (`workflow.create|get|list|update|delete`, `role.*`, `interaction.*`, `guard.*`, `interaction_component.*`) for `Workflow`, `Role`, `Interaction`, `Guard`, and `InteractionComponent`.
- **FR-004**: MCP server configuration MUST use canonical filename `WB-Workflow-Configuration.yaml`.
- **FR-005**: Database connectivity MUST be sourced from `.env` values aligned with `env.example`.
- **FR-006**: `get_system_health` MUST return status values from `CONNECTED`, `DISCONNECTED`, `FAILED`, `INITIALIZING`, and `DEAD`, including failure details when applicable.
- **FR-007**: `user_logon` MUST validate credentials against a YAML-defined in-memory plain-text mock user map and return `SUCCESS`, `DENIED`, or `ERROR` with appropriate status details.
- **FR-008**: Mock authentication behavior MUST be explicitly documented as non-production only and MUST NOT be represented as production-safe authentication.
- **FR-009**: `user_logoff` MUST return `SUCCESS` or `ERROR` with clear status details.
- **FR-010**: CRUD tools for each in-scope table MUST provide create, get, list, update, and delete operations.
- **FR-011**: CRUD responses MUST include normalized operation status (`SUCCESS` or `ERROR`) and status-message semantics.
- **FR-012**: `get`, `update`, and `delete` operations MUST require primary-key identifier input.
- **FR-013**: `list` operations MUST accept optional pagination parameters (`limit`, `offset`) and reject invalid values.
- **FR-014**: The test runbook MUST include reproducible manual SQLite verification queries for in-scope tables and MAY include optional PostgreSQL-equivalent queries.
- **FR-015**: Documentation MUST include negative-path verification for malformed/missing config, database failures, invalid auth payloads, and invalid CRUD inputs.
- **FR-016**: Feature planning artifacts (spec, plan, tasks, and checklist) MUST include explicit MCP protocol/transport compatibility gates, not only endpoint existence checks.
- **FR-017**: Both stdio and HTTP/SSE transports MUST expose the same required tool set and equivalent status/result semantics for all in-scope operations.

### Key Entities *(include if feature involves data)*

- **MCPServerRuntimeProfile**: Describes launch command, transport mode, and runtime prerequisites needed for Inspector connectivity.
- **InspectorVerificationSession**: Captures connection status, tool discovery set, executed tool calls, and verification outcomes.
- **HealthAuthToolResult**: Standardized status/result object for health and auth tools, including failure details and status messages.
- **CrudToolResult**: Standardized status/result object for CRUD operations, with operation metadata and payload/error semantics.
- **ManualDatabaseVerificationStep**: Ordered instruction with query command, expected table outcome, and recorded evidence.

### Constitutional Constraints *(mandatory when applicable)*

- Affected layers are MCP server runtime and documentation; Database -> MCP Server -> Flask Web Server boundaries MUST remain intact.
- MCP contract behavior in this feature includes standards-compliant MCP protocol compatibility for Inspector while preserving existing service boundaries.
- Persistence access MUST remain MCP-confined, and workflow schema integrity MUST remain preserved across Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, and Instance.
- Required environment/configuration scope is limited to `.env` alignment and canonical `WB-Workflow-Configuration.yaml` usage.
- External sources, AI prompts, and Spec Kit outputs used for this feature MUST be captured in project traceability artifacts.
- Any new test/runbook instructions MUST be discoverable from top-level project documentation.

## Assumptions

- Reviewers will use a local environment with Node.js and `npx` available.
- Reviewers can execute a local stdio MCP server process.
- Reviewers can run and reach the HTTP/SSE MCP transport in local validation.
- SQLite is the primary local manual verification path.
- Existing table schemas for in-scope entities remain available and unchanged for this milestone.
- Canonical MCP CRUD tool naming remains dotted style (for example `workflow.create`) for this milestone.
- Canonical Inspector stdio launch path is a dedicated MCP entrypoint module (`python -m mcp_server.src.server`), not the Flask JSON-RPC app module.
- YAML mock credentials are for milestone testing only and are never production authentication controls.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of first-time reviewer runs can connect Inspector to the documented stdio MCP server command within 5 minutes.
- **SC-002**: 100% of required tools are discoverable in Inspector and invocable in at least one end-to-end validation session.
- **SC-003**: 100% of tested health/auth calls return defined status semantics, including explicit failure details for negative cases.
- **SC-004**: Reviewers can complete one full CRUD lifecycle plus direct SQLite verification for at least one in-scope table with no undocumented steps.
- **SC-005**: Documentation-driven full validation flow (setup, connect, invoke, verify) is completed by a first-time reviewer in under 15 minutes.
