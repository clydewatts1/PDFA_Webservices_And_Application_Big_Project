# Tasks: MCP Stdio Inspector Compatibility

**Input**: Design documents from `/specs/004-mcp-stdio-compat/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/mcp-transport-compatibility.md`, `quickstart.md`

**Tests**: No new automated tests are explicitly required by the specification; validation is primarily transport-contract and runbook driven, with optional regression test execution.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare baseline files and validation artifacts for the transport-compatibility milestone.

- [X] T001 Create dedicated stdio MCP entrypoint module scaffold in `mcp_server/src/server.py`
- [X] T002 Add MCP SDK dependency pinning in `requirements.txt`
- [X] T003 Update transport-related environment placeholders in `.env.example`
- [X] T004 [P] Add feature runbook section scaffold for dual-transport validation in `docs/mcp_milestone_test_guide.md`
- [X] T005 [P] Add feature evidence section scaffold in `docs/test_evidence.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared transport, config, and contract infrastructure required by all user stories.

**⚠️ CRITICAL**: No user story implementation should begin before this phase is complete.

- [X] T006 Implement dual-transport config loading and validation helpers in `mcp_server/src/lib/mcp_config.py`
- [X] T007 Implement transport compatibility validation rules in `mcp_server/src/services/validation.py`
- [X] T008 [P] Add shared MCP tool adapter mapping for dotted tool names in `mcp_server/src/lib/tool_adapter.py`
- [X] T009 [P] Add transport parity response comparison helper in `mcp_server/src/lib/transport_parity.py`
- [X] T010 Update HTTP/SSE runtime bootstrap wiring for parity integration in `mcp_server/src/api/app.py`
- [X] T011 Update acceptance contract details for parity gates in `specs/004-mcp-stdio-compat/contracts/mcp-transport-compatibility.md`
- [X] T012 Align quickstart transport startup and validation sequence in `specs/004-mcp-stdio-compat/quickstart.md`

**Checkpoint**: Transport foundation and parity primitives are complete.

---

## Phase 3: User Story 1 - Connect Inspector to MCP Server (Priority: P1) 🎯 MVP

**Goal**: Provide a standards-compliant stdio MCP entrypoint and successful Inspector connectivity with required tool discovery.

**Independent Test**: Start `python -m mcp_server.src.server`, connect via `npx @modelcontextprotocol/inspector`, and confirm required tools are discoverable.

### Implementation for User Story 1

- [X] T013 [US1] Implement stdio MCP server process startup in `mcp_server/src/server.py`
- [X] T014 [US1] Register required tool discovery metadata in `mcp_server/src/server.py`
- [X] T015 [US1] Wire stdio handlers to existing health/auth/CRUD services in `mcp_server/src/server.py`
- [X] T016 [US1] Add canonical Inspector command configuration instructions in `docs/mcp_milestone_test_guide.md`
- [X] T017 [US1] Add stdio startup troubleshooting section in `docs/mcp_milestone_test_guide.md`
- [X] T018 [US1] Record US1 connectivity evidence template entries in `docs/test_evidence.md`

**Checkpoint**: Inspector connects through stdio and required tools are discoverable.

---

## Phase 4: User Story 2 - Verify Health and Auth Contract Behavior (Priority: P2)

**Goal**: Ensure deterministic health/auth status semantics and cross-transport behavior parity.

**Independent Test**: Invoke health/auth tools through stdio and HTTP/SSE transports and verify equivalent status semantics.

### Implementation for User Story 2

- [X] T019 [P] [US2] Normalize health/auth response envelope builders in `mcp_server/src/lib/tool_result.py`
- [X] T020 [P] [US2] Implement health status handling refinements in `mcp_server/src/services/system_service.py`
- [X] T021 [P] [US2] Implement mock-auth validation/disclaimer handling in `mcp_server/src/services/auth_service.py`
- [X] T022 [US2] Expose health/auth tools on stdio transport in `mcp_server/src/server.py`
- [X] T023 [US2] Expose equivalent health/auth behavior on HTTP/SSE transport in `mcp_server/src/api/app.py`
- [X] T024 [US2] Update health/auth handler behavior alignment in `mcp_server/src/api/handlers/system_handlers.py`
- [X] T025 [US2] Add transport parity verification procedure for health/auth in `docs/mcp_milestone_test_guide.md`
- [X] T026 [US2] Add explicit non-production mock-auth disclaimer in `WB-Workflow-Configuration.yaml`
- [X] T027 [US2] Update contract examples for health/auth parity in `specs/004-mcp-stdio-compat/contracts/mcp-transport-compatibility.md`
- [X] T028 [US2] Record US2 parity evidence template entries in `docs/test_evidence.md`

**Checkpoint**: Health/auth tools behave consistently across stdio and HTTP/SSE transports.

---

## Phase 5: User Story 3 - Execute CRUD and Manually Verify Data Outcomes (Priority: P3)

**Goal**: Deliver full dotted-name CRUD parity across transports and manual database verification workflow.

**Independent Test**: Run one full CRUD lifecycle from Inspector and verify expected persisted outcomes via sqlite3 (and optional psql).

### Implementation for User Story 3

- [X] T029 [P] [US3] Register dotted-name CRUD tools on stdio transport in `mcp_server/src/server.py`
- [X] T030 [P] [US3] Ensure HTTP/SSE transport exposes matching dotted-name CRUD tools in `mcp_server/src/api/app.py`
- [X] T031 [US3] Align workflow CRUD status/status_message semantics in `mcp_server/src/api/handlers/workflow_handlers.py`
- [X] T032 [US3] Align dependent-entity CRUD status/status_message semantics in `mcp_server/src/api/handlers/dependent_handlers.py`
- [X] T033 [US3] Enforce missing-key and pagination validation parity in `mcp_server/src/services/workflow_service.py`
- [X] T034 [US3] Enforce missing-key and pagination validation parity in `mcp_server/src/services/dependent_service.py`
- [X] T035 [US3] Add end-to-end CRUD execution walkthrough in `docs/mcp_milestone_test_guide.md`
- [X] T036 [US3] Add primary sqlite3 verification commands and expected outcomes in `docs/mcp_milestone_test_guide.md`
- [X] T037 [US3] Add optional PostgreSQL `psql` equivalent checks in `docs/mcp_milestone_test_guide.md`
- [X] T038 [US3] Add manual verification evidence schema and examples in `docs/test_evidence.md`
- [X] T039 [US3] Link runbook and transport parity requirements in `README.md`
- [X] T040 [US3] Update source attribution and prompt traceability in `docs/source_attribution.md`
- [X] T041 [US3] Update prompt traceability log in `docs/prompts/prompt_log.md`

**Checkpoint**: CRUD parity is complete and manual database verification is reproducible.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks across transports, contracts, docs, and traceability.

- [X] T042 [P] Validate quickstart steps against implemented commands in `specs/004-mcp-stdio-compat/quickstart.md`
- [X] T043 [P] Run optional regression suite via `.venv/Scripts/python.exe -m pytest mcp_server/tests/ -v --tb=short`
- [X] T044 [P] Execute Inspector-based transport parity smoke run and document output in `docs/test_evidence.md`
- [X] T045 Reconcile requirement checklist outcomes in `specs/004-mcp-stdio-compat/checklists/requirements.md`
- [X] T046 Add constitution guard check proving Flask remains HTTP-only and does not consume stdio transport in `docs/mcp_milestone_test_guide.md`
- [X] T047 Execute timed first-time reviewer dry-run for SC-001/SC-005 and record setup/total elapsed minutes plus threshold pass/fail outcome in `docs/test_evidence.md`
- [X] T048 Finalize feature tasks checklist and closeout notes in `specs/004-mcp-stdio-compat/tasks.md`

## Closeout Notes

- Implementation run completed on 2026-03-14.
- Dual transport paths (stdio + HTTP/SSE) implemented with shared handler adapter mapping.
- Inspector CLI smoke flow and timed dry-run evidence captured in `docs/test_evidence.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Setup; blocks all user stories.
- **Phase 3 (US1)**: Depends on Foundational completion.
- **Phase 4 (US2)**: Depends on Foundational completion; uses US1 stdio baseline.
- **Phase 5 (US3)**: Depends on US2 parity and shared tool semantics.
- **Phase 6 (Polish)**: Depends on all user stories complete.

### User Story Dependencies

- **US1 (P1)**: Independent once foundational transport primitives exist.
- **US2 (P2)**: Depends on US1 canonical stdio connectivity path.
- **US3 (P3)**: Depends on US2 parity and status semantics readiness.

### Parallel Opportunities

- Setup tasks `T004` and `T005` can run in parallel.
- Foundational tasks `T008` and `T009` can run in parallel.
- US2 tasks `T019`, `T020`, and `T021` can run in parallel.
- US3 tasks `T029` and `T030` can run in parallel.
- Polish tasks `T042`, `T043`, and `T044` can run in parallel.

---

## Parallel Example: User Story 2

```bash
Task: "T019 Normalize health/auth response envelope builders in mcp_server/src/lib/tool_result.py"
Task: "T020 Implement health status handling refinements in mcp_server/src/services/system_service.py"
Task: "T021 Implement mock-auth validation/disclaimer handling in mcp_server/src/services/auth_service.py"
```

## Parallel Example: User Story 3

```bash
Task: "T029 Register dotted-name CRUD tools on stdio transport in mcp_server/src/server.py"
Task: "T030 Ensure HTTP/SSE transport exposes matching dotted-name CRUD tools in mcp_server/src/api/app.py"
Task: "T038 Add manual verification evidence schema and examples in docs/test_evidence.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) stdio transport + Inspector connectivity.
3. Validate required tool discovery via Inspector.

### Incremental Delivery

1. Deliver transport foundation + canonical stdio path (US1).
2. Add health/auth parity behavior (US2).
3. Add full CRUD parity + manual DB verification flow (US3).
4. Run polish/traceability closeout checks.

### Team Parallelization

1. Engineer A: transport runtime/server entrypoint + parity infrastructure.
2. Engineer B: health/auth service and handler parity behavior.
3. Engineer C: CRUD parity and runbook/evidence documentation.
4. Merge all streams during polish with shared acceptance verification.
