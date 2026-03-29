# Feature Specification: Simplified Web Tier Integration (Phases 1-4)

**Feature Branch**: `006-web-tier-integration`  
**Created**: 2026-03-16  
**Status**: Draft  
**Input**: User description: "Build isolated web tier using Quart for async Flask compatibility, Jinja2 templates, and official MCP Python SDK client. Deliver four-phase implementation: Phase 1 (Foundation & Authentication), Phase 2 (Workspace/Workflow Selection), Phase 3 (Main Dashboard & Navigation), Phase 4 (Traditional CRUD Pages). Enforce strict tier isolation (Quart only calls await mcp_session.call_tool), no JavaScript state management, and boundary-aware testing with mocked MCP sessions."

## Clarifications

### Session 2026-03-16

- Q: Which MCP transport should the web tier connect to? → A: SSE transport at `http://127.0.0.1:5001/sse`. Chosen for long-lived server-to-server communication and alignment with existing 005-fastmcp-refactor infrastructure.
- Q: Should entity list and single-entity reads use separate MCP tools or a polymorphic tool? → A: Two separate tools per entity type using canonical MCP names (e.g., `role.list` for list and `role.get` for single record). Cleaner separation of concerns and simpler test mocking.
- Q: What should happen when a form submission returns validation errors? → A: Re-render the form on the same page with user input preserved in session. Standard web behavior; preserves user context.
- Q: Which entity attributes should be visible in create/edit forms? → A: Hide temporal/audit columns (`eff_from_datetime`, `eff_to_datetime`, `delete_ind`, `insert_user_name`, `update_user_name`); show business attributes only. MCP backend manages all temporal/audit logic per Constitution Principle III.a.
- Q: How should the MCP session be initialized when Quart starts? → A: Create session in app factory (`create_app()`); validate connectivity on first `GET /` health check, not at startup. Supports independent tier startup and cloud-native loose coupling.
- Q: How should POST routes be protected against Cross-Site Request Forgery (CSRF)? → A: Use `quart-wtf` CSRFProtect extension; add `{{ form.csrf_token }}` hidden input to every POST form; validate token automatically on submit via `CSRFProtect(app)`.
- Q: Which directory is the canonical root for the Quart web tier source code and templates? → A: `quart_web/` — the new async web tier lives under `quart_web/src/`, including `quart_web/src/templates/`. The existing `flask_web/` directory is the legacy synchronous tier and is not modified by this feature.
- Q: What is the canonical environment variable name and value format for the MCP backend endpoint? → A: Single variable `MCP_SERVER_URL=http://127.0.0.1:5001/sse` (full SSE URL). Default dev value is `http://127.0.0.1:5001/sse`. Eliminates the split `MCP_HOST`/`MCP_PORT` pattern; simpler to configure and avoids path-assembly bugs.
- Q: What timeout policy applies to MCP tool calls in CRUD routes? → A: All MCP tool calls MUST time out after 10 seconds via `asyncio.wait_for()`. On timeout, the route MUST render a user-visible error page with a retry link. The 10-second limit applies uniformly to all tools (list, fetch, create, update, delete).
- Q: How should forms prevent double-submission during the MCP round-trip? → A: All POST form submit buttons MUST include `onclick="this.disabled=true; this.form.submit()"`. No additional JavaScript libraries or loading spinners are required; this is the only permitted JS expression in templates.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - System Health Check & Authentication Landing Page (Priority: P1)

As a user, I need to load the application landing page, verify the MCP backend is healthy, and see an enabled login form so that I can proceed to authenticate.

**Why this priority**: This is the entry point to the application and the minimum viable feature to demonstrate the Quart-MCP integration and basic health monitoring.

**Independent Test**: Can be fully tested by:
1. Launching the Quart web server
2. Loading `GET /` 
3. Inspecting the response to confirm MCP `get_system_health` was called on page load
4. Verifying the login form is rendered and enabled
5. Validating the response indicates healthy MCP backend status

**Acceptance Scenarios**:

1. **Given** the Quart server is running and MCP backend is healthy, **When** a user loads `GET /`, **Then** the landing page renders with login form enabled and health status visible
2. **Given** MCP backend is unreachable, **When** the landing page loads, **Then** the form is disabled and error message indicates backend unavailable
3. **Given** a user submits login credentials via `POST /login`, **When** the MCP `user_logon` tool returns success, **Then** a secure Quart session cookie is set and user redirects to `/dashboard`

---

### User Story 2 - Login & Session Establishment (Priority: P1)

As an authenticated user, I need to submit my credentials through a standard HTML form and receive a secure session cookie so that subsequent requests recognize my identity without re-authenticating.

**Why this priority**: Authentication is a prerequisite for all state-dependent operations; blocking this prevents accessing protected resources.

**Independent Test**: Can be fully tested by:
1. Submitting `POST /login` with valid credentials
2. Confirming MCP `user_logon` tool is awaited
3. Verifying session cookie is set on success with correct user identifier
4. Validating failed login returns form with error message
5. Checking that missing credentials show validation errors

**Acceptance Scenarios**:

1. **Given** valid credentials submitted, **When** `user_logon` returns success status, **Then** Quart session is created and user is redirected to `/dashboard`
2. **Given** invalid credentials, **When** `user_logon` returns DENIED status, **Then** login form redisplays with error message
3. **Given** MCP request fails, **When** `user_logon` raises exception, **Then** generic error message is shown and form is re-rendered

---

### User Story 3 - Workflow/Workspace Selection (Priority: P2)

As an authenticated user, I need to see a list of available workflows and select one to activate so that the application context is established for subsequent CRUD operations.

**Why this priority**: Required before main dashboard access; enables multi-workflow support across the application lifecycle.

**Independent Test**: Can be fully tested by:
1. After successful login, accessing `/dashboard`
2. Verifying MCP tool (e.g., `get_workflows_for_actor`) is awaited to populate the workflow list
3. Submitting `POST /dashboard` to select a workflow
4. Confirming active_workflow_name is stored in Quart session
5. Validating redirect to main navigation dashboard occurs

**Acceptance Scenarios**:

1. **Given** logged-in user, **When** accessing `/dashboard`, **Then** list of workflows is rendered from MCP call and selection form is displayed
2. **Given** workflow selection submitted, **When** `POST /dashboard` is processed, **Then** active_workflow_name is persisted in session and user redirects to `/entities`
3. **Given** no workflows exist, **When** returning from MCP, **Then** user sees message to create new workflow and create form is available

---

### User Story 4 - Main Dashboard with Contextual Navigation (Priority: P2)

As an authenticated user with active workflow context, I need to see a navigation bar with links to entity categories so that I can navigate to different CRUD sections.

**Why this priority**: Enables browsing and managing entities; is the primary navigation hub after authentication.

**Independent Test**: Can be fully tested by:
1. Accessing `/entities` with active workflow in session
2. Verifying navbar renders with links to Workflows, Roles, Guards, Interactions, Interaction Components
3. Confirming each link preserves the active workflow context
4. Validating that links are routable and accessible

**Acceptance Scenarios**:

1. **Given** user with active workflow, **When** accessing `/entities`, **Then** sticky Bootstrap navbar displays with all entity category links
2. **Given** user clicks "Roles" link, **When** `GET /roles` is processed, **Then** active_workflow_name is read from session and role list is fetched via MCP
3. **Given** session loses active_workflow_name, **When** navigating to entity list, **Then** user is redirected back to workflow selection

---

### User Story 5 - List View for Entity Types (Priority: P2)

As a user, I need to see a table of records for an entity type (e.g., Roles) filtered by active workflow so that I can identify records to edit or delete.

**Why this priority**: Enables discovery of records; provides foundation for subsequent CRUD operations.

**Independent Test**: Can be fully tested by:
1. Accessing `/roles` with active workflow in session
2. Verifying MCP tool (e.g., `role.list`) is called with `WorkflowName` from session
3. Confirming returned records are rendered in HTML table with columns for key fields
4. Validating Edit and Delete action links are present for each row
5. Testing with empty result set to ensure graceful handling

**Acceptance Scenarios**:

1. **Given** active workflow, **When** accessing `/roles`, **Then** MCP `role.list` is awaited and results render in table
2. **Given** each table row, **When** displayed, **Then** Edit link routes to `/roles/edit/<id>` and Delete triggers confirmation
3. **Given** no records for workflow, **When** MCP returns empty list, **Then** table shows "No records" message and Create New button is available

---

### User Story 6 - Edit & Create Pages with Form Submission (Priority: P3)

As a user, I need to edit existing records or create new records through dedicated pages with standard HTML forms so that I can modify entity data and persist changes through the MCP backend.

**Why this priority**: Completes the CRUD cycle; blocks cannot be closed without update capability.

**Independent Test**: Can be fully tested by:
1. Accessing `/roles/edit/<id>` to open edit form
2. Modifying form fields and submitting `POST /roles/edit/<id>`
3. Verifying MCP `update_role` tool is awaited with form-mapped parameters
4. Confirming success redirects back to list view (`/roles`)
5. Testing validation errors and re-rendering form with error messages
6. Testing create flow via `GET /roles/new` and `POST /roles/new`

**Acceptance Scenarios**:

1. **Given** user clicks Edit on a role, **When** `GET /roles/edit/<id>` is accessed, **Then** form renders with current values from MCP
2. **Given** form submission with valid data, **When** `POST /roles/edit/<id>` is processed, **Then** MCP `update_role` is called and user redirects to list
3. **Given** MCP validation error, **When** tool returns error, **Then** form redisplays with error message and user can correct input
4. **Given** user accesses `/roles/new`, **When** form is submitted, **Then** MCP `create_role` is called and success redirects to list

---

### User Story 7 - Delete Record with Confirmation (Priority: P3)

As a user, I need to delete a record with confirmation so that I can remove obsolete entities while preventing accidental deletions.

**Why this priority**: Completes CRUD; soft delete is implemented at MCP tier via SCD Type-2 history logic.

**Independent Test**: Can be fully tested by:
1. Accessing list view and clicking Delete action
2. Server returns confirmation page or modal redirect
3. User confirms deletion via `POST /roles/delete/<id>`
4. MCP `delete_role` tool is awaited
5. Success redirects back to list; failure shows error

**Acceptance Scenarios**:

1. **Given** user initiates delete on a record, **When** confirmation page displays, **Then** user sees record details and confirms action
2. **Given** user confirms deletion, **When** `POST /roles/delete/<id>` is processed, **Then** MCP `delete_role` is called and user redirects to list
3. **Given** MCP returns error, **When** delete fails, **Then** user sees error message and remains on list view

---

## Requirements *(mandatory)*

### Functional Requirements

**FR-001: Quart Web Application Foundation**  
The web tier MUST be implemented using Quart (async Flask) with Jinja2 templating engine serving HTML responses. No SPAs, React, HTMX, or JavaScript state management tools are permitted.

**FR-002: Stateless Server-Side Rendering**  
The Quart application MUST NOT import SQLAlchemy, execute SQL directly, or maintain data state beyond HTTP session scope. All state persistence and business logic MUST be delegated to the MCP backend via `await mcp_session.call_tool()`.

**FR-003: Official MCP Python SDK Client with SSE Transport**  
The web tier MUST use the official Python MCP SDK (`mcp`) with `mcp.client.sse.sse_client` and `mcp.ClientSession` to communicate via SSE transport at `http://127.0.0.1:5001/sse`. Connection management MUST establish a single global async session in the app factory (`create_app()`), available to all routes. MCP session initialization MUST NOT block web tier startup; connectivity validation MUST occur on the first landing-page request (`GET /` health check).

**FR-004: Tier Isolation & Testing Boundary**  
Route-level unit tests MUST use `AsyncMock` to mock the MCP session rather than making real network calls. Test suite MUST verify Quart routes in isolation from the actual MCP server (Constitution Principle VI).

**FR-005: Clean Traditional UI with Bootstrap 5**  
All HTML templates MUST use Bootstrap 5 CSS framework for consistent, clean aesthetic (ample whitespace, readable fonts, simple tables). Navigation MUST use standard full-page GET/POST requests; no AJAX or dynamic partial updates. All POST form submit buttons MUST include the attribute `onclick="this.disabled=true; this.form.submit()"` to prevent double-submission during MCP round-trips. This is the only JavaScript expression permitted in templates; no JS state management, event listeners, or framework code is allowed.

**FR-006: Health Check on Landing Page**  
Landing page (`GET /`) MUST call MCP `get_system_health` on each load and display status. Login form MUST be functionally disabled if health check fails.

**FR-007: Secure Session Establishment**  
Login route (`POST /login`) MUST await MCP `user_logon` tool, set secure Quart session cookie on success with user identifier, and redirect authenticated users to workflow selection page.

**FR-008: Workflow/Workspace Selection**  
Dashboard route (`/dashboard`) MUST retrieve user's available workflows via MCP tool, render selection form, accept `POST` submission, persist selected `active_workflow_name` in Quart session, and redirect to main entity navigation.

**FR-009: Contextual Entity Navigation**  
Main navigation bar MUST render links to entity categories (Workflows, Roles, Guards, Interactions, Interaction Components). All routes MUST read `active_workflow_name` from session and pass it to MCP tools to filter results by workflow.

**FR-010: List Views with Table Rendering (Two-Tool Pattern)**  
Entity list routes (e.g., `/roles`) MUST call a dedicated MCP list tool for the entity type (e.g., `role.list` with optional `WorkflowName` filter). Single-entity fetch routes MUST call a separate tool (e.g., `role.get` with business key parameters `RoleName` and `WorkflowName`). Both tools MUST be awaited separately in their respective routes. List tool results MUST render in an HTML table with action columns (Edit, Delete) and handle empty result sets gracefully.

**FR-011: Edit & Create Pages with Form Submission (Business Fields Only)**  
Edit and create routes MUST render HTML forms containing ONLY business attribute fields (e.g., `role_name`, `role_description`); temporal columns (`eff_from_datetime`, `eff_to_datetime`) and audit columns (`insert_user_name`, `update_user_name`) MUST be hidden from the user and managed exclusively by the MCP backend. Form submission (`POST`) MUST map request form data to MCP tool parameters (e.g., `update_role`), await tool result, redirect to list view on success, and re-render the same form page with validation errors and user input preserved in session on failure.

**FR-012: Delete Operations with Confirmation**  
Delete action MUST show confirmation page before processing. Confirmation submission MUST await MCP delete tool, redirect on success, and show error message on failure.

**FR-013: Session Timeout & Re-authentication**  
Routes MUST check for valid session; missing or expired session MUST redirect to login page. Logout route (`POST /logout`) MUST call MCP `user_logoff` tool and clear session cookie.

**FR-014: CSRF Protection on All POST Routes**  
All HTML forms that submit via HTTP POST (login, workflow selection, create/edit/delete entity) MUST include a CSRF token hidden input rendered via `{{ form.csrf_token }}`. The application MUST use `quart-wtf` `CSRFProtect(app)` initialised in the app factory. Any POST request missing or carrying an invalid CSRF token MUST return HTTP 400 and re-render the originating form with an error message. CSRF protection MUST NOT be disabled in the test suite; tests MUST supply a valid token via the test client or disable with `WTF_CSRF_ENABLED = False` in test config only.

---

### Non-Functional Requirements

**NFR-001: Async/Await Support**  
All Quart routes MUST use `async def` syntax and `await` MCP calls to support concurrent request handling without blocking.

**NFR-002: Template Organization**  
Jinja2 templates MUST be organized in `quart_web/src/templates/` with subdirectories for entity types (e.g., `roles/`, `workflows/`) and shared components (e.g., `_navigation.html`, `_form_errors.html`). The legacy `flask_web/` directory is not modified by this feature.

**NFR-003: Error Handling & User Feedback**  
MCP tool errors MUST be caught, translated to user-friendly messages, and rendered in templates. Generic error page MUST be available for unhandled exceptions. All MCP tool calls MUST be wrapped in `asyncio.wait_for()` with a 10-second timeout; on `asyncio.TimeoutError` the route MUST render an error page informing the user the backend did not respond, with a retry link back to the originating page.

**NFR-004: Logging & Diagnostics**  
Quart routes MUST log MCP calls, response times, and errors using structured logging (JSON format preferred for consistency with MCP tier).

**NFR-005: Environment Configuration**  
The MCP SSE endpoint URL MUST be configurable via the `MCP_SERVER_URL` environment variable. Default development value: `MCP_SERVER_URL=http://127.0.0.1:5001/sse`. The application MUST NOT hardcode the URL; all references MUST read from this single variable.

---

## Success Criteria *(mandatory)*

**SC-001: Landing Page Loads with Health Status**  
User can load `GET /` and see health status within 2 seconds; login form is responsive and accepts input.

**SC-002: Login Flow Completes in Under 5 Seconds**  
User can authenticate, receive session cookie, and be redirected to workflow selection within 5 seconds from form submission.

**SC-003: Workflow Selection Enables Navigation**  
User can select a workflow, and subsequent entity list requests filter by that workflow without explicit URL parameters.

**SC-004: Entity CRUD Operations Succeed End-to-End**  
User can create, read, update, and delete a record (e.g., role) through UI form submission. MCP backend SCD Type-2 history is preserved transparently.

**SC-005: No JavaScript State Management**  
All state transitions occur via HTTP POST/GET; inspector tools show no XHR requests, no form data in JavaScript variables, no client-side validation libraries.

**SC-006: Routes Testable in Isolation**  
Unit tests can mock MCP session and verify route behavior without network calls; test execution completes within 5 seconds for full suite.

**SC-007: Traditional Full-Page Navigation**  
All user interactions result in full page reloads; browser history (back/forward) works as expected for standard HTTP GET/POST flow.

**SC-008: Bootstrap-Styled, Accessible HTML**  
All templates render valid HTML5 with Bootstrap 5 classes; form inputs have labels, error messages are visible, table columns are sortable headers (CSS only).

---

## Key Entities *(mandatory)*

### HTTP Session Object
**Storage**: In-memory (development) or Redis (production)  
**Contents**:
- `user_id`: User identifier from successful `user_logon`
- `active_workflow_name`: Selected workflow name from workflow selection
- `created_at`: Session creation timestamp

### MCP Session (Global)
**Type**: `mcp.ClientSession` created from `mcp.client.sse.sse_client` transport  
**Endpoint**: `http://127.0.0.1:5001/sse` (configurable via `MCP_SERVER_URL` environment variable)  
**Initialization**: Created in app factory function (`create_app()`); NOT in startup hook  
**Lifetime**: Application-level singleton  
**Validation**: Connectivity validated on first `GET /` request (health check); web tier can start if MCP is temporarily unavailable  
**Usage**: All routes call `await mcp_session.call_tool(tool_name, tool_input_dict)`

### Entity Record (Generic)
**Fields** (example for Role):
- `workflow_id`: Foreign key to workflow
- `role_name`: Natural key within workflow
- `role_description`: Human-readable description
- `eff_from_datetime`: SCD Type-2 validity start (set by MCP)
- `eff_to_datetime`: SCD Type-2 validity end (9999-01-01 for current)
- `delete_ind`: Soft delete flag (0=active, 1=deleted)
- `insert_user_name`: Audit user
- `insert_datetime`: Audit timestamp

---

## Assumptions

- **Single User in MVP**: Session management is single-user per browser; multi-user concurrent sessions are out of scope.
- **MCP Backend Always Available**: All MCP tool calls use a 10-second timeout via `asyncio.wait_for()`; on timeout or connection error, a user-visible error page with retry link is shown. Full reconnection and retry logic is deferred to Phase 2.
- **Workflow Scope for All Entities**: All dependent entities (Role, Guard, Interaction, etc.) are scoped to the selected workflow; cross-workflow access is not supported.
- **Form Validation is MCP-Driven**: Client-side form validation (HTML5 constraints) is secondary; MCP tool returns validation errors which are displayed to user.
- **CSS Framework Sufficiency**: Bootstrap 5 is sufficient for all UI requirements; custom CSS is minimal.
- **Jinja2 Power is Sufficient**: Template rendering does not require custom frontend build process; Jinja2 macros and inheritance meet composition needs.
- **HTTP Session Cookies are Secure**: Quart default secure session handling (HTTPS in production, HttpOnly, SameSite) is acceptable.

---

## Boundary & Scope

**In Scope**:
- Quart application foundation with routing and session management
- Jinja2 template rendering for all UI
- Integration with official MCP Python SDK
- Four-phase implementation: Auth, Workspace, Dashboard, CRUD
- Boundary-aware unit testing with mocked MCP client

**Out of Scope**:
- Integration with Flask web tier (unchanged from Phase 5; Quart web tier is separate)
- JavaScript libraries, SPAs, or dynamic UI frameworks
- Custom CSS; Bootstrap 5 only
- WebSocket real-time updates
- Multi-workspace session handling
- Admin dashboards or super-user features
- Pagination (simple list rendering)
- Advanced form validation (delegated to MCP)
- Internationalization (i18n)
- API authentication (OAuth, JWT); HTTP session cookies only

---

## Phase Breakdown

### Phase 1: Foundation & Authentication (P1)
- Quart app initialized with MCP HTTP client session
- Landing page with health check
- Login form and session establishment
- Redirect flow to workflow selection

### Phase 2: Workspace Selection (P1)
- Dashboard page to list available workflows
- Workflow selection form
- Session persistence of active_workflow_name
- Redirect to main navigation

### Phase 3: Main Dashboard & Navigation (P2)
- Sticky navbar with entity category links
- Preserved active workflow context across navigation
- Template inheritance and layout structure

### Phase 4: Traditional CRUD Pages (P3)
- List views for each entity type with tables
- Edit and create pages with forms
- Delete confirmation and soft-delete flow
- Validation error handling and re-rendering

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| MCP backend unavailable at startup | Health check on landing page provides early feedback; user is instructed to check backend status |
| Session loss during workflow interaction | Session timeout redirects to login; user re-enters workflow selection workflow |
| Form submission exceeds MCP timeout | Quart request timeout configured to match MCP backend; user sees timeout error and can retry |
| Template rendering errors leak internals | Error templates show generic message; logs contain detailed traceback for debugging |
| Concurrent active workflows in single session | Scope explicitly restricted to one active workflow per session; multi-workspace planned for Phase 5+ if needed |

---

## Testing Strategy

### Unit Tests
- Mock `mcp_session` using `AsyncMock`
- Test each route in isolation
- Verify correct MCP tool name and parameters are awaited
- Confirm redirect URLs, session mutations, and template context

### Integration Tests (with real MCP backend)
- Minimal coverage; primarily smoke tests
- Verify end-to-end flow from login to single CRUD operation
- Test with pre-populated test data

### Manual Testing
- QA checklist for each phase acceptance scenario
- Browser testing for form submission, validation, and page flow
- Verify Bootstrap styling is consistent across pages

---

## Definition of Done

1. ✓ All FR and NFR requirements implemented
2. ✓ All acceptance scenarios for U1-U7 passing (manual verification)
3. ✓ Unit test coverage ≥ 80% for route logic (excluding Jinja2 rendering)
4. ✓ Quart requirements.txt updated with dependencies
5. ✓ No TypeErrors or AttributeErrors on route access
6. ✓ Bootstrap 5 CSS loads and renders consistently
7. ✓ MCP session is properly initialized at application startup
8. ✓ Logging includes structured JSON output for all MCP calls
9. ✓ Documentation updated: quickstart guides for Phase 1-4 workflows
10. ✓ Code review sign-off from project lead

