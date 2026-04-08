# Tasks: Full Stack WSGI Migration

**Input**: Design documents from `/specs/011-flask-wsgi-migration/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/  
**Tests**: Include contract, integration, and unit coverage because the spec and constitution require validation of the new WSGI wrapper, Flask route parity, and boundary isolation.  
**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no direct dependency)
- **[Story]**: Which user story this task belongs to (`US1`, `US2`, `US3`)
- Exact file paths are included in each task description

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the canonical Flask/WGSI baseline before transport and route migration.

- [X] T001 Update active dependency and runtime configuration surfaces in `requirements.txt`, `pyproject.toml`, and `.env.example` for the Flask-only canonical stack, `MCP_RPC_URL`, and wrapper host/port variables.
- [X] T002 [P] Create Flask web-tier test package scaffolding in `flask_web/tests/unit/__init__.py`, `flask_web/tests/integration/__init__.py`, and any missing parent package files under `flask_web/tests/`.
- [X] T003 [P] Create Flask migration scaffolding for forms and template directories under `flask_web/src/forms/`, `flask_web/src/templates/auth/`, `flask_web/src/templates/workspace/`, and `flask_web/src/templates/entities/`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Complete the transport, boundary, and test foundations that all user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Review and resolve requirement gaps captured in `specs/011-flask-wsgi-migration/checklists/wsgi.md` that block concrete implementation choices.
- [X] T005 Implement the canonical Flask MCP wrapper in `mcp_server/src/wsgi_app.py` using `mcp_server/src/lib/tool_adapter.py` and existing handler/service-layer dispatch.
- [X] T006 [P] Add MCP wrapper contract coverage in `mcp_server/tests/contract/test_wsgi_app_rpc.py` for success envelopes, JSON-RPC application errors under HTTP 200, and malformed transport failures under HTTP 400/500.
- [X] T007 Refactor `flask_web/src/clients/mcp_client.py` and `flask_web/src/app.py` to use `MCP_RPC_URL`, session configuration, timeout handling, and structured synchronous JSON-RPC error normalization.
- [X] T008 [P] Add reusable Flask test fixtures and mocked MCP client patterns in `flask_web/tests/unit/conftest.py` and `flask_web/tests/integration/conftest.py`.

**Checkpoint**: The repository has a supported Flask `/rpc` wrapper, the Flask web tier can call it synchronously, and the new test harness exists.

---

## Phase 3: User Story 1 - Run the Stack on WSGI (Priority: P1) 🎯 MVP

**Goal**: Deliver two separate WSGI-compatible Flask applications that can complete health and sign-in flows over synchronous HTTP JSON-RPC.

**Independent Test**: Start `mcp_server/src/wsgi_app.py` and `flask_web/src/app.py`, then verify health and login behavior through the Flask web tier without any ASGI or SSE dependency.

### Tests for User Story 1

- [X] T009 [P] [US1] Add health and authentication route tests in `flask_web/tests/unit/test_health.py` and `flask_web/tests/unit/test_auth.py`.
- [X] T010 [P] [US1] Add wrapper startup and smoke coverage in `mcp_server/tests/integration/test_wsgi_wrapper_startup.py`.

### Implementation for User Story 1

- [X] T011 [P] [US1] Implement Flask-WTF authentication and workspace-selection forms in `flask_web/src/forms/auth.py`.
- [X] T012 [P] [US1] Implement synchronous health and authentication routes in `flask_web/src/routes/health.py` and `flask_web/src/routes/auth.py`.
- [X] T013 [P] [US1] Migrate base, landing, authentication, and shared partial templates into `flask_web/src/templates/base.html`, `flask_web/src/templates/landing.html`, `flask_web/src/templates/auth/login.html`, `flask_web/src/templates/_flash.html`, `flask_web/src/templates/_form_errors.html`, and `flask_web/src/templates/_navigation.html`.
- [X] T014 [US1] Register the new health/auth routes and session handling in `flask_web/src/app.py`, preserving centralized MCP client error handling.

**Checkpoint**: The MVP path works as two Flask WSGI apps with health and login flows fully functional and testable in isolation.

---

## Phase 4: User Story 2 - Preserve Existing User Flows in Flask (Priority: P2)

**Goal**: Port the production Quart UI surface to Flask for dashboard/workspace navigation and supported workflow-entity CRUD flows.

**Independent Test**: Use the Flask test client and mocked synchronous MCP responses to validate dashboard/workspace selection plus representative role CRUD parity.

### Tests for User Story 2

- [X] T015 [P] [US2] Add workspace and workflow route tests in `flask_web/tests/unit/test_workspace.py` and `flask_web/tests/unit/test_workflow_routes.py`.
- [X] T016 [P] [US2] Port the role CRUD happy-path integration test into `flask_web/tests/integration/test_role_crud_e2e.py` using synchronous mocked MCP responses.
- [X] T017 [P] [US2] Add dependent-entity route coverage in `flask_web/tests/unit/test_role_routes.py` and `flask_web/tests/unit/test_dependent_routes.py`.

### Implementation for User Story 2

- [X] T018 [P] [US2] Implement dashboard/workspace and workflow routes in `flask_web/src/routes/workspace.py` and `flask_web/src/routes/workflow.py`.
- [X] T019 [P] [US2] Migrate entity and workflow forms into `flask_web/src/forms/workflow.py`, `flask_web/src/forms/role.py`, `flask_web/src/forms/interaction.py`, `flask_web/src/forms/guard.py`, and `flask_web/src/forms/interaction_component.py`.
- [X] T020 [P] [US2] Implement role route parity in `flask_web/src/routes/role.py` and migrate shared entity templates under `flask_web/src/templates/entities/`.
- [X] T021 [P] [US2] Implement interaction, guard, and interaction-component route parity in `flask_web/src/routes/interaction.py`, `flask_web/src/routes/guard.py`, and `flask_web/src/routes/interaction_component.py`.
- [X] T022 [US2] Migrate workspace templates under `flask_web/src/templates/workspace/` and complete blueprint registration/navigation updates in `flask_web/src/app.py`.

**Checkpoint**: The Flask web tier now covers the production user-facing routes, forms, and templates defined in the route parity contract.

---

## Phase 5: User Story 3 - Retire Async-Only Web Dependencies Safely (Priority: P3)

**Goal**: Remove the supported Quart/ASGI/SSE path from active configuration, docs, and test instructions while preserving traceability.

**Independent Test**: Review the active runbooks, dependency set, and default test surfaces to confirm Flask WSGI is the only supported path.

### Tests for User Story 3

- [ ] T023 [P] [US3] Add regression coverage for active configuration expectations in `flask_web/tests/unit/test_canary.py` and any new MCP wrapper config tests under `mcp_server/tests/unit/`.

### Implementation for User Story 3

- [X] T024 [P] [US3] Remove Quart from active dependency and default test configuration in `requirements.txt` and `pyproject.toml`, keeping legacy code unsupported rather than canonical.
- [X] T025 [P] [US3] Update canonical runbooks and environment guidance in `README.md`, `docs/README.md`, `mcp_server/README.md`, `flask_web/README.md`, `quart_web/README.md`, and `.env.example`.
- [X] T026 [P] [US3] Update migration and traceability documentation in `docs/source_attribution.md`, `docs/constitution/coverage-matrix.md`, and `specs/011-flask-wsgi-migration/quickstart.md`.
- [X] T027 [US3] Mark obsolete Flask stubs and Quart runtime surfaces as legacy/non-canonical in `flask_web/src/routes/dependent.py`, `flask_web/src/routes/instance.py`, and the `quart_web/` documentation set.

**Checkpoint**: Active docs, dependencies, and supported test/runtime instructions all point to the Flask WSGI path only.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and documentation evidence across all stories.

- [X] T028 [P] Run focused validation suites with `pytest mcp_server/tests/contract/test_wsgi_app_rpc.py flask_web/tests/unit flask_web/tests/integration -v --tb=short` and address any failures.
- [X] T029 [P] Run broader regression suites with `pytest mcp_server/tests flask_web/tests -v --tb=short` and capture any remaining known issues.
- [X] T030 Update delivery evidence and prompt/process trace artifacts in `docs/test_evidence.md`, `docs/prompts/prompt_log.md`, and `README.md` to reflect the completed migration path.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Stories (Phases 3-5)**: All depend on Foundational completion.
- **Polish (Phase 6)**: Depends on all targeted user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; establishes the canonical WSGI stack.
- **User Story 2 (P2)**: Starts after Phase 2 and depends on the US1 transport/client baseline.
- **User Story 3 (P3)**: Starts after Phase 2 and is safest after US1/US2 migration surfaces exist.

### Within Each User Story

- Tests should be authored before or alongside implementation and must fail meaningfully before the code is considered complete.
- Transport/client scaffolding must precede route parity work.
- Forms and templates should land before route registration is finalized.
- Documentation retirement should follow implementation proof so guidance reflects verified behavior.

### Parallel Opportunities

- `T002` and `T003` can run in parallel after `T001`.
- `T006` and `T008` can run in parallel once `T005` is underway.
- Within US1, `T009`, `T010`, `T011`, `T012`, and `T013` can proceed in parallel with coordination.
- Within US2, `T015`, `T016`, `T017`, `T018`, `T019`, `T020`, and `T021` can be distributed across contributors.
- Within US3, `T024`, `T025`, and `T026` can proceed in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phases 1 and 2.
2. Complete Phase 3 to deliver the new Flask MCP wrapper plus health/login web flow.
3. Validate the two-WGSI-app stack before expanding route parity.

### Incremental Delivery

1. Establish the canonical Flask wrapper and client boundary.
2. Port production user-facing routes and templates in the Flask tier.
3. Remove supported Quart/ASGI/SSE guidance and lock the canonical docs/test path.

### Parallel Team Strategy

1. One contributor owns `mcp_server/src/wsgi_app.py` and MCP wrapper tests.
2. One contributor ports Flask auth/workspace and shared templates.
3. One contributor ports entity CRUD routes/forms/tests.
4. Documentation and deprecation cleanup lands after the route surface is validated.

---

## Notes

- `[P]` tasks indicate different files with low direct coupling.
- The canonical route-parity scope is limited to production flows: health, auth, dashboard/workspace, and supported workflow-entity CRUD pages.
- The prior ASGI/SSE runtime path is not a supported fallback in this feature.
- Keep SQLAlchemy and all persistence logic inside the MCP tier throughout implementation.