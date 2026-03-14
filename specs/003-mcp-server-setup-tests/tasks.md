# Tasks: MCP Server Configuration and Test Guide

**Input**: Design documents from `/specs/003-mcp-server-setup-tests/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/mcp-milestone-tooling.md`, `quickstart.md`

**Tests**: No new automated tests are required by the specification. Validation is contract/runbook driven with optional regression command execution.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize canonical feature artifacts and baseline configuration files.

- [X] T001 Create canonical MCP configuration file skeleton in WB-Workflow-Configuration.yaml
- [X] T002 Add milestone-specific environment variable placeholders in .env.example
- [X] T003 [P] Create feature test runbook shell in docs/mcp_milestone_test_guide.md
- [X] T004 [P] Add feature evidence section placeholder in docs/test_evidence.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build reusable configuration and contract infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation should begin before this phase is complete.

- [X] T005 Implement YAML configuration loader utilities in mcp_server/src/lib/mcp_config.py
- [X] T006 Update MCP app bootstrap to read canonical config and env settings in mcp_server/src/api/app.py
- [X] T007 [P] Add startup-time configuration validation helper in mcp_server/src/services/validation.py
- [X] T008 [P] Define normalized tool result envelope helper in mcp_server/src/lib/tool_result.py
- [X] T009 Update milestone tooling contract details in specs/003-mcp-server-setup-tests/contracts/mcp-milestone-tooling.md
- [X] T010 Align quickstart command paths and evidence expectations in specs/003-mcp-server-setup-tests/quickstart.md

**Checkpoint**: Foundational configuration and contract primitives are complete.

---

## Phase 3: User Story 1 - Configure MCP Runtime from Standardized Inputs (Priority: P1) 🎯 MVP

**Goal**: Ensure MCP runtime configuration is canonical, env-driven, and startup-verifiable.

**Independent Test**: With only this story implemented, reviewer can configure `.env`, load `WB-Workflow-Configuration.yaml`, and start MCP server without code edits.

### Implementation for User Story 1

- [X] T011 [US1] Define MCP server metadata/resources/tool declarations in WB-Workflow-Configuration.yaml
- [X] T012 [US1] Add mock-auth user map section in WB-Workflow-Configuration.yaml
- [X] T013 [US1] Implement config path resolution and loading in mcp_server/src/lib/mcp_config.py
- [X] T014 [US1] Wire loaded configuration into app initialization in mcp_server/src/api/app.py
- [X] T015 [US1] Enforce missing/malformed config error handling in mcp_server/src/api/app.py
- [X] T016 [US1] Document env + config startup requirements in docs/mcp_milestone_test_guide.md
- [X] T017 [US1] Record US1 validation evidence in docs/test_evidence.md

**Checkpoint**: MCP runtime starts from canonical YAML + `.env` configuration with documented setup.

---

## Phase 4: User Story 2 - Execute Core MCP Tools for Health and Access Flow (Priority: P2)

**Goal**: Deliver health/auth tools and normalized CRUD tool behavior for in-scope tables.

**Independent Test**: Reviewer can invoke `get_system_health`, `user_logon`, `user_logoff`, and CRUD operations for in-scope tables with expected status/error semantics.

### Implementation for User Story 2

- [X] T018 [P] [US2] Implement health-check service logic in mcp_server/src/services/system_service.py
- [X] T019 [P] [US2] Implement mock-auth service logic using YAML user map in mcp_server/src/services/auth_service.py
- [X] T020 [US2] Implement health/auth JSON-RPC handlers in mcp_server/src/api/handlers/system_handlers.py
- [X] T021 [US2] Register health/auth handlers in mcp_server/src/api/app.py
- [X] T022 [P] [US2] Add normalized success/error result builders in mcp_server/src/lib/tool_result.py
- [X] T023 [US2] Update workflow CRUD response envelopes in mcp_server/src/api/handlers/workflow_handlers.py
- [X] T024 [US2] Update dependent-entity CRUD response envelopes in mcp_server/src/api/handlers/dependent_handlers.py
- [X] T025 [US2] Restrict milestone CRUD scope documentation to Workflow/Role/Interaction/Guard/InteractionComponent in specs/003-mcp-server-setup-tests/spec.md
- [X] T026 [US2] Update contract response examples for health/auth/CRUD in specs/003-mcp-server-setup-tests/contracts/mcp-milestone-tooling.md
- [X] T027 [US2] Add negative-case verification steps (invalid config/input/pagination) in docs/mcp_milestone_test_guide.md
- [X] T028 [US2] Record US2 tool verification evidence in docs/test_evidence.md

**Checkpoint**: Core health/auth/CRUD tool contract behavior is available and documented.

---

## Phase 5: User Story 3 - Perform Table CRUD and Follow End-to-End Test Instructions (Priority: P3)

**Goal**: Provide reviewer-ready end-to-end runbook with required `npx` and manual SQL verification.

**Independent Test**: Reviewer follows runbook to execute inspector-based tool checks and direct table queries (`sqlite3` primary, optional `psql`) for one end-to-end CRUD lifecycle.

### Implementation for User Story 3

- [X] T029 [US3] Add required `npx @modelcontextprotocol/inspector` execution procedure in docs/mcp_milestone_test_guide.md
- [X] T030 [US3] Add end-to-end tool validation sequence (health, auth, CRUD) in docs/mcp_milestone_test_guide.md
- [X] T031 [US3] Add primary SQLite manual table-query verification instructions in docs/mcp_milestone_test_guide.md
- [X] T032 [US3] Add optional PostgreSQL `psql` equivalent verification instructions in docs/mcp_milestone_test_guide.md
- [X] T033 [US3] Add expected evidence capture format for manual verification in docs/test_evidence.md
- [X] T034 [US3] Link runbook from top-level navigation docs in README.md
- [X] T035 [US3] Update attribution and AI prompt traceability for runbook additions in docs/source_attribution.md

**Checkpoint**: Reviewer can execute complete documented verification without undocumented steps.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency pass across contracts, docs, and runtime wiring.

- [X] T036 [P] Validate quickstart flow against implemented commands in specs/003-mcp-server-setup-tests/quickstart.md
- [X] T037 [P] Run optional regression validation via .venv/Scripts/python.exe -m pytest mcp_server/tests/ -v --tb=short
- [X] T038 Reconcile checklist findings and mark completed items in specs/003-mcp-server-setup-tests/checklists/mcp-tooling.md
- [X] T039 Finalize feature traceability note in docs/prompts/prompt_log.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 completion; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can run after US1 config wiring baseline is available.
- **Phase 5 (US3)**: Depends on Phase 4 tool behavior and contract details.
- **Phase 6 (Polish)**: Depends on all user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Independent after foundational setup.
- **US2 (P2)**: Depends on US1 runtime config integration for handler startup behavior.
- **US3 (P3)**: Depends on US2 tool contract implementation and response semantics.

### Parallel Opportunities

- Setup tasks `T003` and `T004` are parallelizable.
- Foundational tasks `T007` and `T008` are parallelizable.
- US2 tasks `T018` and `T019` are parallelizable.
- Polish tasks `T036` and `T037` are parallelizable.

---

## Parallel Example: User Story 2

```bash
# Build core service components in parallel:
Task: "T018 Implement health-check service logic in mcp_server/src/services/system_service.py"
Task: "T019 Implement mock-auth service logic in mcp_server/src/services/auth_service.py"
Task: "T022 Add normalized success/error result builders in mcp_server/src/lib/tool_result.py"
```

## Parallel Example: User Story 3

```bash
# Build runbook verification sections in parallel:
Task: "T031 Add primary SQLite manual table-query verification instructions in docs/mcp_milestone_test_guide.md"
Task: "T032 Add optional PostgreSQL psql equivalent verification instructions in docs/mcp_milestone_test_guide.md"
Task: "T033 Add expected evidence capture format for manual verification in docs/test_evidence.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) runtime configuration readiness.
3. Validate canonical YAML + `.env` startup flow.

### Incremental Delivery

1. Deliver configuration foundation (US1).
2. Add tool contract behavior (US2).
3. Add reviewer runbook + manual verification flow (US3).
4. Complete polish validation and traceability updates.

### Team Parallelization

1. Engineer A: foundational config/loading and app wiring.
2. Engineer B: health/auth service + handler implementation.
3. Engineer C: runbook, SQL verification, and evidence documentation.
4. Merge streams at polish phase for checklist reconciliation.
