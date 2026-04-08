# Feature Specification: Full Stack WSGI Migration

**Feature Branch**: `011-flask-wsgi-migration`  
**Created**: 2026-04-07  
**Status**: Draft  
**Input**: User description: "/speckit specify Feature Name: Full Stack WSGI Migration (Flask Web Tier + Flask MCP Wrapper for PythonAnywhere)"

## Clarifications

### Session 2026-04-07

- Q: Should this feature fully replace the current ASGI/SSE MCP runtime path, or keep it as a legacy fallback? -> A: Fully replace the current ASGI/SSE MCP runtime path; the Flask `wsgi_app.py` wrapper becomes the only supported MCP server entrypoint.
- Q: Which current Quart user flows must be preserved in the Flask migration scope? -> A: Migrate all user-facing production flows: health, authentication, dashboard/workspace navigation, and supported workflow-entity CRUD pages; exclude debug-only or experimental surfaces.
- Q: How should the new Flask MCP wrapper dispatch JSON-RPC requests into existing MCP logic? -> A: Build `wsgi_app.py` as a thin in-process adapter over the existing MCP handler/tool adapter and service layer.
- Q: How should the Flask web tier and Flask MCP wrapper be deployed for PythonAnywhere? -> A: Deploy them as two separate WSGI applications communicating over HTTP.
- Q: How should the Flask MCP wrapper map JSON-RPC errors to HTTP status codes? -> A: Return HTTP 200 for valid JSON-RPC requests, including MCP method, validation, and business errors; reserve HTTP 400/500 for malformed HTTP/JSON or server-failure conditions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the Stack on WSGI (Priority: P1)

As an operator deploying on PythonAnywhere, I need both the web tier and the MCP-facing runtime to run through WSGI-compatible Flask applications so the system can be hosted without unsupported ASGI features.

**Why this priority**: If the stack cannot run inside PythonAnywhere's WSGI model, the application cannot be deployed at all.

**Independent Test**: Start the MCP Flask wrapper and the Flask web tier as separate WSGI-compatible applications, send a health request through the web tier, and confirm a successful end-to-end response over HTTP without SSE, WebSockets, uvicorn, or Starlette runtime dependencies.

**Acceptance Scenarios**:

1. **Given** a PythonAnywhere-compatible WSGI environment, **When** the MCP wrapper is started, **Then** it accepts synchronous `POST /rpc` JSON-RPC requests and returns valid responses.
2. **Given** the Flask web tier is configured to use the MCP wrapper endpoint, **When** a user opens the application health or sign-in flow, **Then** the request completes over HTTP between the two WSGI apps without any async-only transport requirement.

---

### User Story 2 - Preserve Existing User Flows in Flask (Priority: P2)

As an end user, I need the existing production workflow UI, forms, and navigation to behave the same after the migration so I can continue managing workflow entities without learning a new interface.

**Why this priority**: Deployment compatibility is not sufficient if the migration breaks the business workflows already implemented in the web tier.

**Independent Test**: Use the migrated Flask UI to access health, log in, navigate dashboard and workspace flows, and complete representative create, update, and delete flows for supported entities while confirming the same user-facing outcomes as the current tier.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** they navigate through dashboard, workspace, and entity pages in the migrated Flask tier, **Then** the same production workflow-management paths remain available.
2. **Given** existing forms and templates are migrated into the Flask tier, **When** a user submits valid and invalid data, **Then** they receive the same success feedback and validation behavior expected from the current system.

---

### User Story 3 - Retire Async-Only Web Dependencies Safely (Priority: P3)

As a maintainer, I need the Quart/SSE-specific runtime path to be deprecated and the active documentation, tests, and configuration updated so future changes do not drift back toward unsupported hosting assumptions.

**Why this priority**: The migration will regress quickly if the repository continues to treat the async tier as the active path.

**Independent Test**: Review active runbooks, dependencies, and automated test entry points to confirm the Flask WSGI path is authoritative and Quart-specific paths are clearly marked as legacy or removed from active guidance.

**Acceptance Scenarios**:

1. **Given** the repository's active setup and run documentation, **When** a maintainer follows it, **Then** they are directed to the Flask web tier and Flask MCP wrapper rather than the Quart/SSE path.
2. **Given** the active dependency and test surface, **When** it is reviewed, **Then** async-only web-tier assumptions are removed from the canonical implementation path.

### Edge Cases

- The Flask web tier can reach the MCP wrapper endpoint, but the wrapper receives an invalid JSON-RPC payload; the response must stay synchronous and return a clear error contract.
- A migrated route still depends on async-only behavior from the Quart implementation; the affected flow must fail visibly during validation rather than silently hanging under WSGI.
- A template migrates successfully, but route names or form field expectations change; navigation and submission behavior must remain consistent with the current user journey.
- The MCP wrapper starts in a WSGI environment, but one or more tool handlers still assume an ASGI runtime; startup and validation must identify the unsupported assumption before deployment.
- Legacy Quart artifacts remain in the repository for reference; active documentation must distinguish legacy content from the canonical WSGI path.
- A client sends malformed HTTP or invalid JSON to `POST /rpc`; the wrapper must reject it with transport-level HTTP 400/500 handling rather than pretending it is a valid JSON-RPC application response.

## Layer Partition *(mandatory)*

### MCP (Logic)

**Responsibilities**:
- Provide a new WSGI-compatible Flask wrapper in `mcp_server/src/wsgi_app.py` that exposes a synchronous `POST /rpc` endpoint.
- Expose a lightweight `GET /health` operational endpoint for wrapper readiness checks and deployment troubleshooting.
- Receive JSON-RPC request bodies, translate them into calls against the existing MCP handler/tool adapter layer synchronously, and return normalized JSON-RPC success or error envelopes.
- Preserve MCP-owned business logic, validation, transaction handling, and temporal current/history orchestration without moving any persistence concerns into the web tier.
- Make the WSGI wrapper the only supported MCP runtime surface after this migration completes.
- Operate as a separately deployable WSGI service consumed by the Flask web tier over HTTP.
- Distinguish valid JSON-RPC application responses from malformed transport requests by using HTTP 200 for the former and HTTP 400/500 only for the latter.

**Boundary constraints**:
- SQLAlchemy, session creation, and all database operations remain inside the MCP server tier.
- The wrapper must not introduce SSE, WebSockets, Starlette, uvicorn, or other async-only hosting requirements into the supported deployment path.
- The wrapper must not duplicate MCP business logic or create a second independently maintained dispatch path.
- The wrapper must remain a separate HTTP-addressable tier rather than being embedded inside the web-tier Flask process.

**Impacted contracts**:
- The supported MCP runtime contract becomes synchronous HTTP `POST /rpc` JSON-RPC plus a non-business `GET /health` readiness endpoint.
- The prior ASGI and SSE runtime path is removed from supported operation for this feature.
- Dispatch internals reuse `mcp_server/src/api/app.py` as the shared Flask JSON-RPC transport implementation and `mcp_server/src/lib/tool_adapter.py` as the single method-dispatch source rather than creating a second wrapper stack.
- Valid JSON-RPC requests keep JSON-RPC error information in the response payload while malformed transport requests use HTTP error status handling.

---

### Web-Tier (Routes)

**Responsibilities**:
- Port the active production routes and forms from `quart_web` into `flask_web`, covering health, authentication, dashboard/workspace navigation, and supported workflow-entity CRUD pages.
- Replace async route handling with synchronous Flask request handling and transition form handling to `flask-wtf`.
- Rebuild `flask_web/src/clients/mcp_client.py` around synchronous HTTP requests to the MCP wrapper's `POST /rpc` endpoint.
- Preserve existing route responsibilities, navigation, validation messaging, and MCP error handling semantics expected by users.
- Treat the in-scope production route surface as: `/`, `/login`, `/logout`, `/dashboard`, `/entities`, `/workflows`, `/workflows/new`, `/workflows/<workflow_name>/edit`, `/workflows/<workflow_name>/delete`, `/roles`, `/roles/new`, `/roles/<role_name>/edit`, `/roles/<role_name>/delete`, `/guards`, `/guards/new`, `/guards/<guard_name>/edit`, `/guards/<guard_name>/delete`, `/interactions`, `/interactions/new`, `/interactions/<interaction_name>/edit`, `/interactions/<interaction_name>/delete`, `/interaction-components`, `/interaction-components/new`, `/interaction-components/<component_name>/edit`, and `/interaction-components/<component_name>/delete`.
- Treat the in-scope form surface as Flask-WTF replacements for login, workspace selection, workflow, role, interaction, guard, and interaction-component forms; experimental or debug-only forms outside these routes are out of scope.

**Boundary constraints**:
- The Flask web tier must not import SQLAlchemy, open database sessions, or embed business logic that belongs in MCP tools.
- The Flask web tier must not use SSE, WebSockets, or any persistent connection model.

**Impacted contracts**:
- Web-tier MCP client calls become synchronous HTTP POST JSON-RPC exchanges.
- Route behavior remains driven by MCP tool contracts rather than local persistence logic.

---

### Page (UI)

**Responsibilities**:
- Migrate the current production Jinja2 templates and user flows into `flask_web/src/templates/`, covering health, authentication, dashboard/workspace, and supported entity-management pages.
- Preserve user-visible entity management flows, page structure, and validation feedback while swapping the underlying web framework.
- Ensure forms, redirects, and navigation patterns remain understandable and stable for reviewers and end users.

**Boundary constraints**:
- Pages remain presentation-only and depend on route/view models rather than direct MCP or database implementation details.
- The migration must not remove required user flows that exist in the current tier.

**Impacted contracts**:
- Template context and page actions may be adapted for Flask, but user-observable workflow outcomes must remain equivalent.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a WSGI-compatible Flask application for the web tier as the canonical presentation layer.
- **FR-002**: The system MUST provide a WSGI-compatible Flask wrapper for MCP runtime access that accepts synchronous HTTP `POST /rpc` JSON-RPC requests as the only supported MCP server entrypoint.
- **FR-002a**: The MCP wrapper MUST expose `GET /health` as its only supported operational endpoint in addition to `POST /rpc`, and it MUST NOT expose supported SSE, WebSocket, or alternate HTTP business endpoints.
- **FR-003**: The MCP wrapper MUST invoke the MCP logic layer synchronously and return normalized JSON-RPC responses for both success and failure cases.
- **FR-003a**: The MCP wrapper MUST dispatch requests through the existing MCP handler/tool adapter and service layer rather than through a separate proxy hop or reimplemented MCP business logic.
- **FR-003b**: The Flask web tier and the Flask MCP wrapper MUST be deployed as separate WSGI applications communicating over HTTP rather than as a single combined process.
- **FR-003c**: The MCP wrapper MUST return HTTP 200 for valid JSON-RPC requests, including method, validation, and business-level MCP errors, and MUST reserve HTTP 400/500 semantics for malformed HTTP/JSON or server-failure conditions.
- **FR-004**: The active production routes and forms currently implemented in the Quart tier MUST be migrated into the Flask tier without loss of supported user journeys for health, authentication, dashboard/workspace navigation, and supported workflow-entity CRUD pages.
- **FR-004a**: The supported workflow-entity CRUD scope is limited to workflow, role, interaction, guard, and interaction-component management; instance flows, debug pages, and experimental Quart-only assets are outside this feature's parity commitment.
- **FR-005**: The Flask web tier MUST use a synchronous MCP client that sends standard HTTP POST requests to the MCP wrapper endpoint.
- **FR-006**: The canonical web-tier implementation MUST NOT require SSE, WebSockets, uvicorn, Starlette, or any ASGI runtime to function.
- **FR-007**: The Flask web tier MUST NOT import SQLAlchemy, create database sessions, or perform direct database operations.
- **FR-008**: All business logic, validation, transaction handling, and persistence orchestration MUST remain inside the MCP server tier.
- **FR-009**: The migrated page layer MUST preserve the current Jinja2-based user flows for health, authentication, dashboard/workspace navigation, and supported workflow-entity management pages.
- **FR-010**: The active dependency set and test surface MUST reflect the synchronous Flask-based architecture as the canonical path.
- **FR-010a**: Quart code and tests MAY remain in the repository during migration, but they MUST be marked legacy and MUST NOT remain the default or recommended execution path.
- **FR-011**: Active runbooks and developer-facing documentation MUST identify the Flask web tier and Flask MCP wrapper as the supported PythonAnywhere deployment path.
- **FR-011a**: The required environment configuration for the canonical path MUST explicitly include `DB_URL`, `MCP_CONFIG_PATH`, `MCP_WRAPPER_HOST`, `MCP_WRAPPER_PORT`, `FLASK_HOST`, `FLASK_PORT`, `SESSION_SECRET`, `MCP_RPC_URL`, and `MCP_TIMEOUT_SECONDS`.
- **FR-012**: The prior ASGI/SSE MCP runtime path MUST be removed from supported setup, runtime, and test instructions for this feature.
- **FR-013**: The wrapper and Flask web tier MUST emit structured logs for transport failures, JSON-RPC errors, authentication attempts, and workflow-selection actions sufficient to diagnose cross-app configuration failures.
- **FR-014**: The Flask web tier MUST enforce session-secret-backed cookies and CSRF protection for authenticated form submissions outside explicit automated-test configuration.

### Key Entities *(include if feature involves data)*

- **WSGI MCP Wrapper**: The Flask-hosted MCP entry surface that accepts JSON-RPC requests and delegates to MCP-owned logic synchronously.
- **In-Process MCP Dispatcher**: The adapter path that maps JSON-RPC methods from the Flask wrapper into the existing MCP handler/tool adapter and service layer.
- **Synchronous MCP Client**: The Flask web-tier component responsible for issuing HTTP POST JSON-RPC calls and normalizing MCP responses.
- **Inter-App HTTP Boundary**: The networked boundary between the Flask web tier and the separately deployed Flask MCP wrapper.
- **Migrated Route Surface**: The set of production Flask routes that replace active Quart handlers for health, authentication, dashboard/workspace navigation, and supported workflow-entity CRUD behavior.
- **Migrated Page Templates**: The production Jinja2 templates and form pages ported into the Flask template tree.
- **Retired ASGI Runtime Path**: The previous MCP network runtime based on async transport support that is removed from supported operation by this feature.

### Assumptions

- PythonAnywhere deployment is the controlling hosting constraint for this feature.
- Existing MCP business logic can be reused through a synchronous wrapper without changing core domain behavior.
- The existing MCP handler/tool adapter surface is sufficiently reusable to serve as the single dispatch core for both transport and WSGI wrapper behavior.
- Existing Quart user flows are the baseline to preserve during migration rather than an opportunity to redesign the UI.
- The project will continue to use JSON-RPC as the cross-tier contract between the web tier and the MCP tier.
- Any remaining async-only web assets can remain as temporary legacy references during implementation, but final acceptance requires they be clearly labeled unsupported in active docs and default execution guidance.
- PythonAnywhere deployment can host the web tier and MCP wrapper as two distinct WSGI applications with HTTP reachability between them.

### Constitutional Constraints *(mandatory when applicable)*

- **Layer Integrity**: This feature must preserve the Database -> MCP Server -> Flask Web Server boundary defined by Constitution v3.0.0.
- **Spec Kit Initiation**: The feature was initiated via Spec Kit and this specification includes MCP (Logic), Web-Tier (Routes), and Page (UI) partitions.
- **Transport Constraint**: The supported cross-tier interaction must be synchronous HTTP POST JSON-RPC only; SSE and WebSockets are excluded from the active deployment path.
- **Tier Deployment Constraint**: The Flask web tier and MCP wrapper must remain separate tiers in deployment as well as code structure.
- **Persistence Ownership**: SQLAlchemy and all persistence behavior remain confined to the MCP server tier.
- **Single Logic Path**: The WSGI wrapper must reuse the existing MCP dispatch and service layer rather than creating a second business-logic implementation.
- **Temporal Integrity**: Any MCP wrapper changes must preserve MCP-owned current/history orchestration and must not alter current and `_Hist` responsibilities.
- **Documentation Alignment**: Active setup, dependency, and test guidance must be updated to reflect the Flask WSGI path as authoritative.
- **Traceability**: External sources, AI prompts, and Spec Kit usage referenced during planning and implementation must be recorded in the project traceability documentation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of canonical deployment steps for the migrated stack can be executed in a WSGI-compatible environment without requiring ASGI-specific runtime components.
- **SC-002**: 100% of designated primary user journeys for health, authentication, dashboard/workspace access, and supported entity management complete successfully through the Flask web tier.
- **SC-003**: 100% of canonical web-tier-to-MCP calls during validation use synchronous HTTP POST JSON-RPC and 0 use SSE or WebSockets.
- **SC-003a**: 100% of sampled valid JSON-RPC error cases during validation preserve JSON-RPC error payloads under HTTP 200, while malformed transport cases are handled with HTTP 400/500 behavior.
- **SC-004**: 100% of reviewed active runbooks and setup documents identify Flask, not Quart, as the canonical web-tier deployment path.
- **SC-004a**: The authoritative reviewed document set for this feature is `README.md`, `docs/README.md`, `mcp_server/README.md`, `flask_web/README.md`, `.env.example`, and `specs/011-flask-wsgi-migration/quickstart.md`.
- **SC-005**: 0 verified cases of direct database access from the Flask web tier remain in the migrated implementation path.
- **SC-006**: 100% of designated migration validation tests for the Flask web tier and MCP wrapper pass on the canonical synchronous stack.
- **SC-006a**: The designated validation suite for this feature includes `mcp_server/tests/contract/test_wsgi_app_rpc.py`, `mcp_server/tests/integration/test_wsgi_wrapper_startup.py`, `flask_web/tests/unit/test_health.py`, `flask_web/tests/unit/test_auth.py`, and the migrated `flask_web/tests/integration/test_role_crud_e2e.py`.
- **SC-007**: 0 unresolved constitutional compliance gaps remain in this specification before planning begins.
