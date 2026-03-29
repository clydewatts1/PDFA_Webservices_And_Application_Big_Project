# Tasks: Simplified Web Tier Integration (Phases 1-4)

**Input**: Design documents from `/specs/006-web-tier-integration/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Included (explicitly requested by FR-004 and SC-006 in spec.md)  
**Organization**: Tasks grouped by user story so each story is independently implementable and testable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize Quart web tier skeleton, dependencies, and baseline configuration.

- [X] T001 Create Quart web tier package structure in quart_web/__init__.py and quart_web/src/{__init__.py,app.py}
- [X] T002 Create route package skeleton in quart_web/src/routes/{__init__.py,health.py,auth.py,workspace.py,workflow.py,role.py,interaction.py,guard.py,interaction_component.py}
- [X] T003 [P] Create form package skeleton in quart_web/src/forms/{__init__.py,auth.py,workflow.py,role.py,interaction.py,guard.py,interaction_component.py}
- [X] T004 [P] Create template skeleton in quart_web/src/templates/{base.html,error.html} and quart_web/src/templates/{auth/login.html,workspace/dashboard.html,workspace/entities.html,entities/list.html,entities/form.html,entities/delete_confirm.html,landing.html}
- [X] T005 Add Quart web dependencies to requirements.txt and requirements-dev.txt
- [X] T006 [P] Add Quart pytest configuration (`asyncio_mode=auto`) in pyproject.toml
- [X] T007 [P] Add Quart tier startup and env documentation section to README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core app factory, MCP client wrapper, session/CSRF/error infrastructure that blocks all stories.

**⚠️ CRITICAL**: No user story implementation starts before this phase is complete.

- [X] T008 Implement Quart app factory and blueprint registration in quart_web/src/app.py
- [X] T009 Implement MCP SDK SSE singleton wrapper (`MCPClientWrapper`) with 10s timeout in quart_web/src/clients/mcp_client.py
- [X] T010 [P] Implement web-tier MCP exception classes in quart_web/src/clients/errors.py
- [X] T011 Implement environment configuration (`MCP_SERVER_URL`, `SESSION_SECRET`, cookie flags) in quart_web/src/config.py
- [X] T012 Integrate CSRFProtect and session settings in quart_web/src/app.py
- [X] T013 [P] Implement shared auth/session guards decorator utilities in quart_web/src/routes/guards.py
- [X] T014 [P] Implement shared template partials for flash/errors/navigation in quart_web/src/templates/{_flash.html,_form_errors.html,_navigation.html}
- [X] T015 Implement global error handlers (400/403/500/503/504) in quart_web/src/routes/errors.py

**Checkpoint**: Foundation ready; user stories can now proceed.

---

## Phase 3: User Story 1 - System Health Check & Authentication Landing Page (Priority: P1) 🎯 MVP

**Goal**: Render landing page, perform MCP health check, and show enabled/disabled login UI by health state.

**Independent Test**: `GET /` calls `get_system_health`; healthy response enables login UI, failure disables form and shows backend-unavailable message.

### Tests for User Story 1

- [X] T016 [P] [US1] Add route unit tests for landing health success/failure in quart_web/tests/unit/test_health.py
- [X] T017 [P] [US1] Add template rendering assertions for healthy/unhealthy states in quart_web/tests/unit/test_health.py

### Implementation for User Story 1

- [X] T018 [US1] Implement landing route `GET /` with `get_system_health` MCP call in quart_web/src/routes/health.py
- [X] T019 [US1] Implement landing page template with disabled login form fallback in quart_web/src/templates/landing.html
- [X] T020 [US1] Wire health blueprint in quart_web/src/app.py
- [X] T021 [US1] Add structured route logging for health check timing/errors in quart_web/src/routes/health.py
- [X] T022 [US1] Update quickstart verification step for landing health in specs/006-web-tier-integration/quickstart.md

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Login & Session Establishment (Priority: P1)

**Goal**: Authenticate through MCP `user_logon`, establish secure session cookie, and support logout.

**Independent Test**: Valid login sets session and redirects to `/dashboard`; invalid login re-renders form with error; logout clears session after `user_logoff`.

### Tests for User Story 2

- [X] T023 [P] [US2] Add auth route tests for GET/POST login and POST logout in quart_web/tests/unit/test_auth.py
- [X] T024 [P] [US2] Add CSRF enforcement tests for login/logout POST routes in quart_web/tests/unit/test_auth.py

### Implementation for User Story 2

- [X] T025 [US2] Implement login/logout forms and validators in quart_web/src/forms/auth.py
- [X] T026 [US2] Implement auth routes (`GET /login`, `POST /login`, `POST /logout`) in quart_web/src/routes/auth.py
- [X] T027 [US2] Implement login template with `{{ form.csrf_token }}` and submit-disable onclick in quart_web/src/templates/auth/login.html
- [X] T028 [US2] Wire auth blueprint and session lifecycle hooks in quart_web/src/app.py
- [X] T029 [US2] Add auth flow logging and MCP error mapping in quart_web/src/routes/auth.py

**Checkpoint**: User Stories 1 and 2 are independently functional and testable.

---

## Phase 5: User Story 3 - Workflow/Workspace Selection (Priority: P2)

**Goal**: Fetch workflow list via MCP and persist selected workflow context in session.

**Independent Test**: Authenticated user can load `/dashboard`, select workflow via POST, and land on `/entities` with `active_workflow_name` in session.

### Tests for User Story 3

- [X] T030 [P] [US3] Add workspace route tests for workflow list and selection in quart_web/tests/unit/test_workspace.py
- [X] T031 [P] [US3] Add session-guard tests for unauthenticated access to `/dashboard` in quart_web/tests/unit/test_workspace.py

### Implementation for User Story 3

- [X] T032 [US3] Implement workflow selection form (`WorkspaceSelectForm`) in quart_web/src/forms/auth.py
- [X] T033 [US3] Implement workspace routes (`GET /dashboard`, `POST /dashboard`) in quart_web/src/routes/workspace.py
- [X] T034 [US3] Implement workspace selection template in quart_web/src/templates/workspace/dashboard.html
- [X] T035 [US3] Add empty-workflow UX state and create-workflow CTA in quart_web/src/templates/workspace/dashboard.html

**Checkpoint**: User Story 3 works independently after authentication.

---

## Phase 6: User Story 4 - Main Dashboard with Contextual Navigation (Priority: P2)

**Goal**: Provide entity navigation hub scoped by selected workflow.

**Independent Test**: `/entities` renders tabs/links for workflows, roles, guards, interactions, and interaction components; missing workflow context redirects to `/dashboard`.

### Tests for User Story 4

- [X] T036 [P] [US4] Add dashboard route tests for context-required navigation in quart_web/tests/unit/test_dashboard.py
- [X] T037 [P] [US4] Add navbar link rendering tests in quart_web/tests/unit/test_dashboard.py

### Implementation for User Story 4

- [X] T038 [US4] Implement entities dashboard route `GET /entities` in quart_web/src/routes/workspace.py
- [X] T039 [US4] Implement shared navigation partial with active workflow context in quart_web/src/templates/_navigation.html
- [X] T040 [US4] Implement entities dashboard template in quart_web/src/templates/workspace/entities.html
- [X] T041 [US4] Add redirect guard for missing `active_workflow_name` in quart_web/src/routes/workspace.py

**Checkpoint**: User Story 4 is independently functional with established session/workflow context.

---

## Phase 7: User Story 5 - List View for Entity Types (Priority: P2)

**Goal**: Render workflow-scoped list tables for all entity types.

**Independent Test**: Each entity list route calls `<entity>.list` with session workflow filter and shows rows, actions, or empty-state message.

### Tests for User Story 5

- [X] T042 [P] [US5] Add workflow list-route tests in quart_web/tests/unit/test_workflow_routes.py
- [X] T043 [P] [US5] Add role list-route tests in quart_web/tests/unit/test_role_routes.py
- [X] T044 [P] [US5] Add interaction/guard/component list-route tests in quart_web/tests/unit/test_dependent_routes.py

### Implementation for User Story 5

- [X] T045 [US5] Implement workflow list route (`GET /workflows`) in quart_web/src/routes/workflow.py
- [X] T046 [US5] Implement role list route (`GET /roles`) in quart_web/src/routes/role.py
- [X] T047 [US5] Implement interaction/guard/component list routes in quart_web/src/routes/{interaction.py,guard.py,interaction_component.py}
- [X] T048 [US5] Implement shared entity list template with Edit/Delete actions and no-records state in quart_web/src/templates/entities/list.html

**Checkpoint**: User Story 5 is independently functional for list/read discovery.

---

## Phase 8: User Story 6 - Edit & Create Pages with Form Submission (Priority: P3)

**Goal**: Implement create/edit forms (business fields only) for workflow and dependent entities.

**Independent Test**: GET edit/new routes prefill data via `<entity>.get`; POST create/update maps form data to MCP tools; validation errors re-render same page with preserved input.

### Tests for User Story 6

- [X] T049 [P] [US6] Add workflow create/edit route tests with success/error cases in quart_web/tests/unit/test_workflow_routes.py
- [X] T050 [P] [US6] Add role create/edit route tests with same-page validation re-render in quart_web/tests/unit/test_role_routes.py
- [X] T051 [P] [US6] Add interaction/guard/component create/edit tests in quart_web/tests/unit/test_dependent_routes.py

### Implementation for User Story 6

- [X] T052 [US6] Implement workflow form class (business fields only) in quart_web/src/forms/workflow.py
- [X] T053 [US6] Implement role/interaction/guard/component form classes (exclude temporal/audit columns) in quart_web/src/forms/{role.py,interaction.py,guard.py,interaction_component.py}
- [X] T054 [US6] Implement workflow create/edit routes in quart_web/src/routes/workflow.py
- [X] T055 [US6] Implement role create/edit routes in quart_web/src/routes/role.py
- [X] T056 [US6] Implement interaction/guard/component create/edit routes in quart_web/src/routes/{interaction.py,guard.py,interaction_component.py}
- [X] T057 [US6] Implement shared create/edit template with CSRF token and submit-disable onclick in quart_web/src/templates/entities/form.html
- [X] T058 [US6] Implement MCP validation-error mapping and form re-render logic in quart_web/src/routes/{workflow.py,role.py,interaction.py,guard.py,interaction_component.py}

**Checkpoint**: User Story 6 is independently functional for create/update flows.

---

## Phase 9: User Story 7 - Delete Record with Confirmation (Priority: P3)

**Goal**: Confirm destructive action and execute MCP delete per entity.

**Independent Test**: Delete action shows confirmation page; POST confirm calls `<entity>.delete` with business keys + actor; success redirects to list; failure shows error.

### Tests for User Story 7

- [X] T059 [P] [US7] Add workflow delete confirmation/submit tests in quart_web/tests/unit/test_workflow_routes.py
- [X] T060 [P] [US7] Add role and dependent entity delete tests in quart_web/tests/unit/test_role_routes.py and quart_web/tests/unit/test_dependent_routes.py

### Implementation for User Story 7

- [X] T061 [US7] Implement delete confirmation routes/pages in quart_web/src/routes/{workflow.py,role.py,interaction.py,guard.py,interaction_component.py}
- [X] T062 [US7] Implement delete confirmation template in quart_web/src/templates/entities/delete_confirm.html
- [X] T063 [US7] Implement delete POST handlers with actor/session checks and error messaging in quart_web/src/routes/{workflow.py,role.py,interaction.py,guard.py,interaction_component.py}

**Checkpoint**: User Story 7 is independently functional for delete workflows.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Harden, document, and validate full feature behavior.

- [X] T064 [P] Add end-to-end happy-path integration tests (health→login→select workflow→CRUD role) in quart_web/tests/integration/test_role_crud_e2e.py
- [X] T065 Add route-level structured logging fields (tool_name, duration_ms, workflow_name, username) in quart_web/src/routes/{health.py,auth.py,workspace.py,workflow.py,role.py,interaction.py,guard.py,interaction_component.py}
- [X] T066 [P] Add project-level docs for quart_web architecture and runbook in docs/README.md and quart_web/README.md
- [X] T067 Validate quickstart command flow and expected outputs in specs/006-web-tier-integration/quickstart.md
- [X] T068 [P] Add source attribution entries for Quart/quart-wtf/MCP SDK references in docs/source_attribution.md
- [X] T069 Run final test matrix and capture evidence in docs/test_evidence.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): starts immediately
- Foundational (Phase 2): depends on Setup completion; blocks all user stories
- User Stories (Phases 3-9): depend on Foundational completion
- Polish (Phase 10): depends on completion of desired stories

### User Story Dependency Graph

- US1 (P1) → base MVP entry point
- US2 (P1) depends on US1 route/template baseline
- US3 (P2) depends on US2 authenticated session
- US4 (P2) depends on US3 active workflow session context
- US5 (P2) depends on US4 navigation context
- US6 (P3) depends on US5 list/read context and form scaffolding
- US7 (P3) depends on US5 list/read context

Graph: `US1 → US2 → US3 → US4 → US5 → {US6, US7}`

### Within Each User Story

- Tests first (expected to fail)
- Route/form implementation
- Template integration
- Error handling/logging
- Story-level verification

---

## Parallel Execution Examples

### US1

- T016 and T017 can run in parallel (same test module, independent assertions)

### US2

- T023 and T024 can run in parallel

### US3

- T030 and T031 can run in parallel

### US4

- T036 and T037 can run in parallel

### US5

- T042, T043, and T044 can run in parallel (separate test modules)

### US6

- T049, T050, and T051 can run in parallel
- T052 and T053 can run in parallel (separate form modules)

### US7

- T059 and T060 can run in parallel

---

## Implementation Strategy

### MVP First (US1)

1. Complete Phase 1 (Setup)
2. Complete Phase 2 (Foundational)
3. Complete Phase 3 (US1)
4. Validate `GET /` health + landing behavior before adding auth/session flows

### Incremental Delivery

1. Deliver US1 + US2 as authentication milestone
2. Deliver US3 + US4 as session-context navigation milestone
3. Deliver US5 as list/read milestone
4. Deliver US6 + US7 as full CRUD milestone
5. Finish with Phase 10 hardening and evidence capture

### Team Parallelization

- After Phase 2, one engineer can own auth/session (US2/US3), another navigation/list (US4/US5), another CRUD forms/delete (US6/US7)

---

## Format Validation Checklist

- All tasks use checkbox format: `- [ ]`
- All tasks have sequential IDs `T001` through `T069`
- `[P]` marker appears only on parallelizable tasks
- Story label `[US#]` appears only in user story phases
- Every task description includes at least one explicit file path
