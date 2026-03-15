# Tasks: MCP Stdio Inspector Compatibility

**Input**: Design documents from `/specs/004-mcp-stdio-compat/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/mcp-transport-compatibility.md`, `quickstart.md`

**Tests**: This feature uses runbook-driven/manual transport and data verification. No new automated test tasks are required by the current spec.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare canonical runtime/configuration and documentation scaffolding.

- [X] T001 Confirm canonical MCP configuration filename usage in `WB-Workflow-Configuration.yaml`
- [X] T002 Confirm transport and DB environment placeholders in `.env.example`
- [X] T003 Ensure dedicated stdio entrypoint module exists in `mcp_server/src/server.py`
- [X] T004 [P] Prepare dual-transport runbook scaffold in `docs/mcp_milestone_test_guide.md`
- [X] T005 [P] Prepare evidence capture scaffold in `docs/test_evidence.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement cross-story transport/config/parity contracts that all stories depend on.

**⚠️ CRITICAL**: No user story work should begin before this phase completes.

- [X] T006 Implement configuration loading and required-tool validation in `mcp_server/src/lib/mcp_config.py`
- [X] T007 Implement transport compatibility validation primitives in `mcp_server/src/services/validation.py`
- [X] T008 [P] Implement shared tool name mapping for dotted MCP methods in `mcp_server/src/lib/tool_adapter.py`
- [X] T009 [P] Implement parity comparison helper for stdio vs HTTP/SSE outcomes in `mcp_server/src/lib/transport_parity.py`
- [X] T010 Wire HTTP JSON-RPC and SSE runtime bootstrap for parity behavior in `mcp_server/src/api/app.py`
- [X] T011 Align transport contract baseline and failure mapping in `specs/004-mcp-stdio-compat/contracts/mcp-transport-compatibility.md`
- [X] T012 Align quickstart startup and parity flow steps in `specs/004-mcp-stdio-compat/quickstart.md`

**Checkpoint**: Shared transport and contract foundation is complete.

---

## Phase 3: User Story 1 - Connect Inspector to MCP Server (Priority: P1) 🎯 MVP

**Goal**: Enable canonical Inspector connection via stdio with required tool discovery.

**Independent Test**: Run `python -m mcp_server.src.server`, connect via Inspector, and verify required tool discovery.

### Implementation for User Story 1

- [X] T013 [US1] Implement stdio MCP server startup and lifecycle handling in `mcp_server/src/server.py`
- [X] T014 [US1] Register required tool discovery metadata for in-scope tool families in `mcp_server/src/server.py`
- [X] T015 [US1] Bind stdio tool handlers to existing MCP services in `mcp_server/src/server.py`
- [X] T016 [US1] Document canonical Inspector command configuration in `docs/mcp_milestone_test_guide.md`
- [X] T017 [US1] Document stdio startup troubleshooting and failure triage in `docs/mcp_milestone_test_guide.md`
- [X] T018 [US1] Add US1 connection/discovery evidence template entries in `docs/test_evidence.md`

**Checkpoint**: Inspector connectivity and required discovery are independently verifiable.

---

## Phase 4: User Story 2 - Verify Health and Auth Contract Behavior (Priority: P2)

**Goal**: Ensure deterministic health/auth semantics and parity across stdio and HTTP/SSE.

**Independent Test**: Execute health/auth calls via both transports and verify equivalent semantics, including session-dependent logoff behavior.

### Implementation for User Story 2

- [X] T019 [P] [US2] Normalize health/auth result envelope shaping in `mcp_server/src/lib/tool_result.py`
- [X] T020 [P] [US2] Implement health status semantics and failure-detail mapping in `mcp_server/src/services/system_service.py`
- [X] T021 [US2] Implement mock-auth validation and non-production disclaimer behavior in `mcp_server/src/services/auth_service.py`
- [X] T022 [US2] Implement active-session tracking for auth lifecycle in `mcp_server/src/services/auth_service.py`
- [X] T023 [US2] Enforce `user_logoff` success only after prior successful `user_logon` in `mcp_server/src/services/auth_service.py`
- [X] T024 [US2] Enforce process-local in-memory session reset behavior across server restarts in `mcp_server/src/server.py`
- [X] T025 [US2] Expose aligned health/auth semantics on HTTP/SSE handlers in `mcp_server/src/api/handlers/system_handlers.py`
- [X] T026 [US2] Expose aligned health/auth semantics on stdio tools in `mcp_server/src/server.py`
- [X] T027 [US2] Enforce standard JSON-RPC transport error codes with project diagnostics in `error.data` in `mcp_server/src/api/app.py`
- [X] T028 [US2] Enforce standard JSON-RPC transport error codes with project diagnostics in `error.data` in `mcp_server/src/server.py`
- [X] T029 [US2] Update health/auth parity and negative-path runbook steps in `docs/mcp_milestone_test_guide.md`
- [X] T030 [US2] Add US2 parity evidence fields for session lifecycle and error mapping in `docs/test_evidence.md`

**Checkpoint**: Health/auth parity (including session-dependent logoff and error-code strategy) is independently verifiable.

---

## Phase 5: User Story 3 - Execute CRUD and Manually Verify Data Outcomes (Priority: P3)

**Goal**: Deliver in-scope CRUD parity across transports with reproducible manual DB verification.

**Independent Test**: Execute one full in-scope CRUD lifecycle through Inspector and validate persisted rows via sqlite3 queries.

### Implementation for User Story 3

- [X] T031 [P] [US3] Register in-scope dotted CRUD tools (excluding `unit_of_work.*` and `instance.*`) on stdio in `mcp_server/src/server.py`
- [X] T032 [P] [US3] Expose matching in-scope dotted CRUD tools on HTTP/SSE in `mcp_server/src/api/app.py`
- [X] T033 [US3] Align workflow CRUD status/status_message semantics in `mcp_server/src/api/handlers/workflow_handlers.py`
- [X] T034 [US3] Align dependent-entity CRUD status/status_message semantics in `mcp_server/src/api/handlers/dependent_handlers.py`
- [X] T035 [US3] Enforce missing-key and pagination validation parity for workflow operations in `mcp_server/src/services/workflow_service.py`
- [X] T036 [US3] Enforce missing-key and pagination validation parity for dependent operations in `mcp_server/src/services/dependent_service.py`
- [X] T037 [US3] Document end-to-end in-scope CRUD walkthrough in `docs/mcp_milestone_test_guide.md`
- [X] T038 [US3] Document SQLite verification commands and expected outcomes in `docs/mcp_milestone_test_guide.md`
- [X] T039 [US3] Document optional PostgreSQL equivalent verification steps in `docs/mcp_milestone_test_guide.md`
- [X] T040 [US3] Add US3 manual verification evidence schema and examples in `docs/test_evidence.md`

**Checkpoint**: In-scope CRUD parity and direct data verification are independently reproducible.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final artifact consistency, protocol-gate closure, and reviewer-readiness.

- [X] T041 [P] Reconcile transport contract with final clarifications in `specs/004-mcp-stdio-compat/contracts/mcp-transport-compatibility.md`
- [X] T042 [P] Reconcile quickstart commands and parity checks in `specs/004-mcp-stdio-compat/quickstart.md`
- [X] T043 Reconcile explicit protocol/transport/auth-session gates in `specs/004-mcp-stdio-compat/checklists/requirements.md`
- [X] T044 [P] Reconcile top-level runbook links and milestone notes in `README.md`
- [X] T045 [P] Reconcile source attribution and prompt traceability in `docs/source_attribution.md`
- [X] T046 [P] Reconcile prompt traceability log for this feature in `docs/prompts/prompt_log.md`
- [X] T047 Execute Inspector-based parity smoke run and capture evidence in `docs/test_evidence.md`
- [X] T048 Execute timed first-time reviewer dry-run and capture SC-001/SC-005 evidence in `docs/test_evidence.md`

---

## Phase 6 Sign-Off

- Date (UTC): 2026-03-15
- Status: COMPLETE
- Reviewer handoff summary:
	- All tasks `T001` through `T048` are complete.
	- Phase 6 evidence for `T047`/`T048` is recorded in `docs/test_evidence.md`.
	- Latest regression confirmation: `pytest mcp_server/tests/ -q` (pass, exit code `0`).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2 and uses US1 connectivity baseline.
- **Phase 5 (US3)**: Depends on Phase 2 and uses US2 semantic/error parity baseline.
- **Phase 6 (Polish)**: Depends on all user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Starts after foundational completion; no dependency on US2/US3.
- **US2 (P2)**: Starts after foundational completion; references US1 transport baseline.
- **US3 (P3)**: Starts after foundational completion; depends on stabilized parity/error semantics from US2.

### Parallel Opportunities

- Setup: `T004`, `T005` can run in parallel.
- Foundational: `T008`, `T009` can run in parallel.
- US2: `T019` and `T020` can run in parallel; `T027` and `T028` can run in parallel.
- US3: `T031` and `T032` can run in parallel.
- Polish: `T041`, `T042`, `T044`, `T045`, `T046` can run in parallel.

---

## Parallel Example: User Story 2

```bash
Task: "T019 Normalize health/auth result envelope shaping in mcp_server/src/lib/tool_result.py"
Task: "T020 Implement health status semantics and failure-detail mapping in mcp_server/src/services/system_service.py"
Task: "T027 Enforce standard JSON-RPC transport error codes with project diagnostics in error.data in mcp_server/src/api/app.py"
Task: "T028 Enforce standard JSON-RPC transport error codes with project diagnostics in error.data in mcp_server/src/server.py"
```

## Parallel Example: User Story 3

```bash
Task: "T031 Register in-scope dotted CRUD tools on stdio in mcp_server/src/server.py"
Task: "T032 Expose matching in-scope dotted CRUD tools on HTTP/SSE in mcp_server/src/api/app.py"
Task: "T040 Add US3 manual verification evidence schema and examples in docs/test_evidence.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate Inspector connectivity and required in-scope tool discovery.

### Incremental Delivery

1. Deliver transport/connectivity baseline (US1).
2. Deliver health/auth parity and error/session behavior (US2).
3. Deliver in-scope CRUD parity and manual DB verification (US3).
4. Close protocol gates and reviewer evidence (Phase 6).

### Team Parallelization

1. Engineer A: runtime transport entrypoints, adapter/parity helpers.
2. Engineer B: health/auth behavior, session lifecycle, error mapping.
3. Engineer C: CRUD parity, runbook/evidence artifacts, traceability docs.
