# Feature Specification: MCP Server FastMCP Refactor

**Feature Branch**: `[005-fastmcp-refactor]`  
**Created**: 2026-03-16  
**Status**: Draft  
**Input**: User description: "Refactor the MCP server to replace custom Flask and manual JSON-RPC routing with official FastMCP, preserve existing tool logic and temporal database orchestration, support `stdio`, `sse`, and `streamable-http` transports, and update boundary-aware testing."

## Clarifications

### Session 2026-03-16

- Q: Which existing MCP tools are in scope for the FastMCP refactor? → A: Limit required migration scope to the feature 004 workflow-domain milestone set: `get_system_health`, `user_logon`, `user_logoff`, `workflow.*`, `role.*`, `interaction.*`, `guard.*`, and `interaction_component.*`; defer `unit_of_work.*` and `instance.*`.
- Q: What HTTP transport outcome is required for this feature relative to Flask integration? → A: This feature is MCP-tier only. `stdio`, `sse`, and `streamable-http` are all required at the MCP tier, and no Flask-side integration changes are required in this increment.
- Q: Should the refactor preserve the current custom HTTP/SSE contract shapes or adopt FastMCP-native HTTP transports? → A: Adopt FastMCP-native `sse` and `streamable-http` contracts and remove the current custom HTTP routing/envelope behavior from required scope.
- Q: Should `WB-Workflow-Configuration.yaml` remain the required source of MCP tool metadata in this refactor? → A: No. Deprecate YAML as the source of MCP tool metadata for this feature and define all in-scope FastMCP tool metadata directly in Python code.
- Q: How much automated transport-specific coverage is required? → A: Require full tool-behavior coverage on `stdio`, plus transport startup/discovery/basic-call smoke coverage for `sse` and `streamable-http`.
- Q: How should constitution-alignment item C1 be treated during MCP runtime stabilization? → A: Defer Flask-tier mock/stub boundary test implementation in this MCP-only increment; record as a temporary governance deferral to be revisited when the web-tier framework direction is finalized.
- Q: How should documentation-attribution item I1 be handled for this increment? → A: Defer supplementary directory README and broader attribution expansion in this increment; keep as a recommended follow-up after MCP stabilization.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Replace Custom MCP Runtime (Priority: P1)

As a maintainer, I need the MCP server tier to run on the constitution-mandated FastMCP framework so that the runtime stops re-implementing protocol behavior in Flask and supports the required transports through one official server abstraction.

**Why this priority**: The current custom runtime violates the constitution and is the highest architectural risk. Until it is removed, every transport and protocol change remains harder to reason about and test.

**Independent Test**: Can be fully tested by starting the MCP server through documented transport options (`stdio`, `sse`, and `streamable-http`) and confirming the server starts without any custom Flask JSON-RPC router or queue-based SSE runtime in the MCP tier.

**Acceptance Scenarios**:

1. **Given** the MCP server codebase still contains custom Flask JSON-RPC request handling, **When** this feature is implemented, **Then** MCP transport startup is owned by FastMCP rather than custom `/rpc` parsing, `_response`, `_error`, queue, or `stream_with_context` logic.
2. **Given** a reviewer needs any supported transport, **When** the MCP server is started with the selected transport mode, **Then** the same FastMCP-based runtime serves the request path without changing tool logic and without preserving legacy custom HTTP envelope handlers.

---

### User Story 2 - Preserve Tool Contracts Across Transports (Priority: P2)

As a reviewer, I need the in-scope workflow-domain MCP tools to remain discoverable and behaviorally consistent across all required MCP transports so that the server framework can change without breaking tool names, result semantics, or transport parity.

**Why this priority**: The refactor only has value if it preserves the existing business contract. Breaking tool names or tool outcomes would turn an architectural cleanup into a feature regression.

**Independent Test**: Can be fully tested by listing and calling the refactored tools through FastMCP-backed transports and confirming the same in-scope tool set, result fields, and temporal side effects are preserved.

**Acceptance Scenarios**:

1. **Given** the in-scope health, auth, and workflow-domain CRUD tools, **When** they are registered on the FastMCP runtime, **Then** their canonical dotted names remain unchanged and discoverable.
2. **Given** equivalent tool inputs over `stdio`, `sse`, and `streamable-http`, **When** the refactored server executes them, **Then** the returned business outcome remains equivalent aside from transport metadata.

---

### User Story 3 - Modernize MCP Test Coverage (Priority: P3)

As a maintainer, I need the MCP server tests to validate the FastMCP-based runtime with boundary-aware harnesses so the new transport framework is verified without weakening the temporal `_Hist` guarantees or tier boundaries.

**Why this priority**: The constitution requires both FastMCP usage and temporal-history validation. Without aligned tests, the refactor would not be safely reviewable.

**Independent Test**: Can be fully tested by running full tool-behavior coverage on `stdio` plus startup/discovery/basic-call smoke coverage on `sse` and `streamable-http`, while confirming that update/delete flows still assert `_Hist` writes and single-current-row behavior.

**Acceptance Scenarios**:

1. **Given** MCP server automated tests, **When** they are updated for the FastMCP runtime, **Then** they validate tool execution without depending on Flask request handlers.
2. **Given** an update to a temporal entity, **When** the MCP server tests run, **Then** they assert the prior state is written to the matching `_Hist` table and the primary table preserves one current row per business key.
3. **Given** the non-stdio transports, **When** automated validation runs, **Then** `sse` and `streamable-http` are covered by startup/discovery/basic-call smoke checks rather than full duplicated end-to-end behavioral suites.

### Edge Cases

- The requested transport mode is unsupported, misspelled, or missing required host/port arguments.
- One of `stdio`, `sse`, or `streamable-http` starts successfully while another is missing or not wired to the same FastMCP tool catalog.
- A tool is omitted during decorator-based registration, causing discovery drift between pre-refactor and post-refactor runtimes.
- A transport starts successfully, but one tool returns a different status/result envelope than before the refactor.
- FastMCP startup fails because required configuration or database environment variables are missing.
- Temporal update tests pass at the tool-call level but fail to verify `_Hist` writes or single-current-row invariants.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The MCP server tier MUST remove custom Flask, Quart, queue-based event streaming, `stream_with_context`, and bespoke JSON-RPC envelope handling from its runtime implementation.
- **FR-002**: The MCP server tier MUST be instantiated through the official Python `mcp` library using `FastMCP` as required by the constitution.
- **FR-003**: The MCP server MUST expose a single FastMCP-based runtime entrypoint with parameterized startup that supports `stdio`, `sse`, and `streamable-http`; the refactor is incomplete if any transport is absent or routed through a separate non-FastMCP implementation.
- **FR-003B**: This feature scope is limited to MCP-tier protocol support; no Flask-side client or integration changes are required for completion of this increment.
- **FR-003C**: The `sse` and `streamable-http` transport behaviors for this feature MUST follow FastMCP-native transport contracts; preserving the current custom `/rpc` route or custom SSE event envelope behavior is not required for completion.
- **FR-004**: The refactor MUST preserve the canonical tool names for the in-scope tool set: `get_system_health`, `user_logon`, `user_logoff`, `workflow.*`, `role.*`, `interaction.*`, `guard.*`, and `interaction_component.*`, so that clients do not need renamed tool calls after migration.
- **FR-004A**: `unit_of_work.*` and `instance.*` are explicitly out of scope for required migration in this feature and MAY be handled in a later refactor increment.
- **FR-005**: Existing adapter-driven tool logic MUST be converted into FastMCP tool registration using the `@mcp.tool()` pattern or an equivalent FastMCP-native registration mechanism that yields the same externally visible tool catalog.
- **FR-006**: The refactor MUST preserve the MCP server’s role as the business-logic and transaction orchestration layer and MUST NOT move persistence logic into the Flask tier.
- **FR-007**: Tool execution results MUST return a standardized MCP call-tool response object containing exactly these top-level fields: `status`, `status_message`, and `data`. `status` MUST be either `success` or `error`; `status_message` MUST be a non-empty string; and `data` MUST be JSON-serializable (object, array, scalar, or `null`) so responses can be validated consistently across transports.
- **FR-008**: For equivalent in-scope tool name and input payload, `stdio`, `sse`, and `streamable-http` MUST execute through the same MCP service-layer handler path and return equivalent business semantics in `status`, `status_message`, and `data`; any differences MUST be limited to transport/protocol metadata.
- **FR-009**: The refactor MUST preserve required runtime environment sourcing and non-tool operational configuration, and MUST define in-scope FastMCP tool names, descriptions, parameter metadata, and registration behavior in Python code rather than sourcing MCP tool metadata from `WB-Workflow-Configuration.yaml`.
- **FR-009A**: `WB-Workflow-Configuration.yaml` MAY be reduced, deprecated, or removed from the MCP runtime path for this feature.
- **FR-010**: The MCP server MUST retain temporal update orchestration in the existing service layer, including `_Hist` writes, timestamp closure, and single-current-row behavior within one transaction.
- **FR-011**: `mcp_server/src/api/app.py` and `mcp_server/src/server.py` MUST no longer implement custom protocol routing or framework-owned request/stream handling after the refactor is complete.
- **FR-012**: Reviewer-facing startup documentation MUST be updated to describe the FastMCP transport startup workflow for `stdio`, `sse`, and `streamable-http`.
- **FR-013**: MCP server automated tests MUST be updated to use FastMCP test clients or standard asyncio-based harnesses instead of Flask request handling for MCP runtime validation.
- **FR-014**: MCP server automated tests MUST explicitly assert temporal `_Hist` behavior for affected update and delete flows, consistent with constitution Principle VI.
- **FR-014A**: Automated test coverage MUST provide full in-scope tool-behavior validation on `stdio`.
- **FR-014B**: Automated test coverage MUST provide startup, discovery, and basic-call smoke validation on `sse` and `streamable-http`.
- **FR-015**: The refactor MUST preserve boundary-aware testing so Flask-tier tests continue to mock MCP interactions rather than connecting directly to the database.
- **FR-015A**: For this MCP-only increment, explicit Flask-tier test-task implementation is deferred pending MCP server stabilization and final web-tier framework decision; this deferral MUST be revisited before any web-tier integration increment.
- **FR-016**: This increment does not require Flask-side integration work or Flask transport-selection changes, provided the existing architectural boundary keeping Flask outside MCP internals remains intact.

### Key Entities *(include if feature involves data)*

- **MCP Runtime Profile**: Defines the supported transport mode (`stdio`, `sse`, or `streamable-http`), startup parameters, and non-tool configuration inputs used to launch the FastMCP server.
- **Tool Registration Catalog**: Represents the in-scope set of health, auth, and workflow-domain tool definitions that must remain discoverable with stable names and descriptions after migration and are now authored directly in Python code.
- **Tool Execution Result**: Represents the MCP call-tool output returned to clients, including status, status message, and structured payload data.
- **Temporal Persistence Operation**: Represents a tool-triggered database mutation that must preserve current-row plus `_Hist` semantics within a single MCP-owned transaction.
- **Boundary-Aware Test Session**: Represents automated validation of the FastMCP runtime, tool behavior, and temporal side effects without violating tier isolation.
- **Transport Smoke Validation**: Represents targeted startup, discovery, and basic-call verification for `sse` and `streamable-http` without requiring full duplicated behavioral suites.

### Constitutional Constraints *(mandatory when applicable)*

- **Affected layers**: Primary impact is the MCP Server tier. The database tier is unchanged in ownership but remains subject to MCP-owned temporal orchestration. The Flask tier remains architecturally adjacent but is out of scope for required implementation changes in this increment.
- **Architecture boundary**: Database -> MCP Server -> Flask Web Server remains intact. The refactor replaces the MCP server framework, not the tier boundaries. No direct imports or database access are introduced across tiers.
- **MCP contract scope**: The runtime must support `stdio`, `sse`, and `streamable-http`. The refactor changes the hosting mechanism for these contracts but must preserve the existing tool-level business semantics.
- **Transport completeness**: `stdio`, `sse`, and `streamable-http` are all in scope for this feature and must be represented consistently in implementation, tests, and reviewer documentation.
- **Legacy contract handling**: Existing custom Flask-based HTTP routing and custom JSON-RPC/SSE envelopes in the MCP tier are deprecated by this feature and do not need to be preserved as compatibility shims.
- **Flask interaction scope**: No Flask-side protocol adaptation is required in this feature; reviewer validation is satisfied by MCP-tier transport behavior and MCP-tier test coverage.
- **Persistence containment**: SQLAlchemy remains confined to the MCP server tier. Existing `mcp_server/src/services/*` transaction logic remains the persistence orchestration point wrapped by the FastMCP runtime.
- **Workflow-schema integrity**: Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, and Instance integrity rules remain owned by MCP services and are not redefined by the transport refactor.
- **Temporal integrity**: Current and `_Hist` tables remain structurally symmetric, preserve `EffFromDateTime`, `EffToDateTime`, `DeleteInd`, `InsertUserName`, and `UpdateUserName`, keep one current primary-row per business key, and continue using MCP-owned current-state plus history orchestration.
- **Configuration changes**: Startup inputs must cover transport selection plus required environment-driven runtime settings such as host, port, database URL, and default actor values. This feature does not require YAML to remain the authoritative source of MCP tool metadata.
- **Documentation and attribution**: README and MCP runtime documentation must be updated to reflect FastMCP startup and testing workflows. External sources referenced for this spec include the official MCP Python SDK repository, the project constitution, the current MCP runtime files, and the FastMCP refactor prompt in `.github/prompts/speckit.specify.prompt.md`.
- **Deferred governance note (this increment)**: Supplementary directory README expansion and broader external-source attribution enhancements beyond MCP runtime documentation are temporarily deferred for this increment and must be revisited in the next web-tier-facing feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reviewer can start the MCP server in each supported transport mode (`stdio`, `sse`, and `streamable-http`) from the documented workflow without source-code edits.
- **SC-002**: 100% of previously supported in-scope MCP tools remain discoverable with unchanged canonical names after the refactor.
- **SC-003**: 100% of MCP server automated tests pass using FastMCP-aware or asyncio-based runtime harnesses rather than Flask request routing.
- **SC-003A**: Automated coverage demonstrates full in-scope tool-behavior validation on `stdio` and smoke validation on both `sse` and `streamable-http`.
- **SC-004**: 100% of tested temporal update/delete flows continue to verify `_Hist` insertion and one-current-row behavior for affected entities.
- **SC-005**: The MCP server runtime path contains no Flask, Quart, queue-driven SSE, or custom JSON-RPC envelope orchestration code after completion.
- **SC-006**: Reviewer validation confirms the MCP tier exposes FastMCP-native `sse` and `streamable-http` transports rather than the prior custom Flask-managed HTTP contract path.
- **SC-007**: 100% of validated in-scope tool responses include exactly `status`, `status_message`, and `data`, where `status` is `success|error`, `status_message` is non-empty, and `data` is JSON-serializable.
- **SC-008**: 100% of sampled in-scope transport-parity validations show equivalent `status`, `status_message`, and business `data` semantics for the same tool input across `stdio`, `sse`, and `streamable-http`, with differences only in transport/protocol metadata.
