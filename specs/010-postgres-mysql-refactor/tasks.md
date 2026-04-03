# Tasks: Continue PostgreSQL to MySQL Refactor

**Input**: Design documents from `/specs/010-postgres-mysql-refactor/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/migration-and-cutover-contract.md`, `quickstart.md`

**Tests**: MySQL-backed contract and integration validation is required by the specification.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: `US1`, `US2`, `US3` only for user-story phases
- Every task includes an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare baseline dependencies and shared runbook scaffolding.

- [X] T001 Align runtime dependencies for MySQL validation in `requirements.txt`
- [X] T002 Add MySQL-first environment and cutover prerequisites in `README.md`
- [X] T003 [P] Add feature-010 evidence capture section scaffold in `docs/test_evidence.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core migration and validation infrastructure that blocks all user stories.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [X] T004 Review and patch MySQL-incompatible migration directives in `database/migrations/versions/0001_current_history_tables.py`
- [X] T005 Update MySQL runtime engine/session reliability configuration in `mcp_server/src/db/session.py`
- [X] T006 [P] Add MySQL test database fixtures and lifecycle management in `mcp_server/tests/conftest.py`
- [X] T007 [P] Add MySQL connection preflight and DB_URL scheme guard logic in `mcp_server/src/services/system_service.py`
- [X] T008 Define rollback-window configuration parsing and startup logging hooks in `mcp_server/src/server.py`

**Checkpoint**: Foundation complete. User story implementation can now proceed.

---

## Phase 3: User Story 1 - Complete Runtime Migration (Priority: P1) 🎯 MVP

**Goal**: Runtime starts on MySQL reliably, migrations execute baseline-to-head, and health checks report success.

**Independent Test**: Set MySQL `DB_URL`, run migration baseline-to-head, start MCP runtime, and verify health success plus rollback-window activation metadata.

### Tests for User Story 1

- [X] T009 [P] [US1] Add MySQL migration smoke validation for baseline-to-head execution in `mcp_server/tests/integration/test_workflow_e2e.py`
- [X] T010 [P] [US1] Add MySQL runtime health contract assertion for DB connectivity success/failure in `mcp_server/tests/contract/test_workflow_contract.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement actionable MySQL startup error mapping and legacy PostgreSQL URL rejection messaging in `mcp_server/src/services/system_service.py`
- [X] T012 [US1] Implement cutover start event logging with 24-hour rollback deadline fields in `mcp_server/src/server.py`
- [X] T013 [US1] Document baseline-to-head MySQL migration execution and expected outcomes in `specs/010-postgres-mysql-refactor/quickstart.md`
- [ ] T014 [US1] Record migration and runtime health evidence for MVP validation in `docs/test_evidence.md`

**Checkpoint**: US1 is independently runnable and demonstrable as MVP.

---

## Phase 4: User Story 2 - Preserve Functional Behavior and Data Semantics (Priority: P2)

**Goal**: Contract and integration behavior remains correct on MySQL, including temporal current plus `_Hist` assertions.

**Independent Test**: Execute designated contract and integration suites on MySQL and confirm temporal assertions pass unchanged.

### Tests for User Story 2

- [X] T015 [P] [US2] Update workflow contract suite to use MySQL fixture target in `mcp_server/tests/contract/test_workflow_contract.py`
- [X] T016 [P] [US2] Update dependent-entities contract suite to use MySQL fixture target in `mcp_server/tests/contract/test_dependent_entities_contract.py`
- [X] T017 [P] [US2] Update workflow integration journey to run with MySQL fixture target in `mcp_server/tests/integration/test_workflow_e2e.py`
- [X] T018 [P] [US2] Update instance replication integration journey to run with MySQL fixture target in `mcp_server/tests/integration/test_instance_replication_e2e.py`

### Implementation for User Story 2

- [X] T019 [US2] Verify and adjust temporal integrity assertions for current plus `_Hist` behavior on MySQL in `mcp_server/tests/integration/test_dependent_entities_integrity.py`
- [ ] T020 [US2] Execute MySQL-only contract and integration validation commands and record outputs in `docs/test_evidence.md`
- [X] T021 [US2] Update validation-target contract and SQLite exclusion sign-off language in `specs/010-postgres-mysql-refactor/contracts/migration-and-cutover-contract.md`

**Checkpoint**: US2 validates behavioral and temporal parity on MySQL.

---

## Phase 5: User Story 3 - Align Documentation and Handover Guidance (Priority: P3)

**Goal**: Handover documentation reflects MySQL-first operation, no-backfill cutover policy, and rollback governance.

**Independent Test**: Follow docs from clean setup and confirm MySQL-first runbook succeeds without relying on PostgreSQL runtime defaults.

### Implementation for User Story 3

- [X] T022 [P] [US3] Update canonical MySQL setup and runtime guidance in `README.md`
- [X] T023 [P] [US3] Update milestone guide with no-backfill cutover and rollback-window governance in `docs/mcp_milestone_test_guide.md`
- [X] T024 [P] [US3] Update attribution log for migration continuation decisions and operational constraints in `docs/source_attribution.md`
- [X] T025 [US3] Add reviewer grep procedure and historical-reference allowlist notes in `specs/010-postgres-mysql-refactor/research.md`
- [X] T026 [US3] Finalize handover checklist for rollback decision gate and window controls in `specs/010-postgres-mysql-refactor/quickstart.md`

**Checkpoint**: US3 documentation is independently usable for deployment and review.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, evidence completion, and release-readiness checks.

- [X] T027 [P] Run repository grep validation for active PostgreSQL runtime references and capture results in `docs/test_evidence.md`
- [X] T028 Finalize cutover decision log template with rollback start/end control points in `docs/test_evidence.md`
- [X] T029 [P] Reconcile final plan/spec/tasks consistency notes in `specs/010-postgres-mysql-refactor/plan.md`
- [ ] T030 Run full quickstart rehearsal and capture final pass/fail evidence in `docs/test_evidence.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2 and should start after US1 runtime path is stable.
- **Phase 5 (US3)**: Depends on Phase 2 and should finalize after US1/US2 validation outcomes are known.
- **Phase 6 (Polish)**: Depends on all user stories.

### User Story Dependencies

- **US1 (P1)**: First deliverable after Foundational.
- **US2 (P2)**: Depends on foundational MySQL fixture/runtime setup; functionally validates US1 behavior.
- **US3 (P3)**: Depends on validated runtime/test outcomes to produce accurate handover docs.

### Within Each User Story

- Add or update tests first.
- Implement runtime/service changes second.
- Execute validation and capture evidence last.

---

## Parallel Opportunities

- **Setup**: T003 can run in parallel with T001 and T002.
- **Foundational**: T006 and T007 can run in parallel after T004/T005 planning alignment.
- **US1**: T009 and T010 can run in parallel; T013 can run while T011/T012 stabilize.
- **US2**: T015, T016, T017, and T018 can run in parallel across separate test files.
- **US3**: T022, T023, and T024 can run in parallel.
- **Polish**: T027 and T029 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T009 Add MySQL migration smoke validation in mcp_server/tests/integration/test_workflow_e2e.py"
Task: "T010 Add runtime health contract assertion in mcp_server/tests/contract/test_workflow_contract.py"
Task: "T013 Document migration execution outcomes in specs/010-postgres-mysql-refactor/quickstart.md"
```

## Parallel Example: User Story 2

```bash
Task: "T015 Update workflow contract MySQL fixture target in mcp_server/tests/contract/test_workflow_contract.py"
Task: "T016 Update dependent-entities contract MySQL fixture target in mcp_server/tests/contract/test_dependent_entities_contract.py"
Task: "T017 Update workflow integration MySQL fixture target in mcp_server/tests/integration/test_workflow_e2e.py"
Task: "T018 Update instance integration MySQL fixture target in mcp_server/tests/integration/test_instance_replication_e2e.py"
```

## Parallel Example: User Story 3

```bash
Task: "T022 Update canonical MySQL setup guidance in README.md"
Task: "T023 Update cutover and rollback governance in docs/mcp_milestone_test_guide.md"
Task: "T024 Update migration attribution entries in docs/source_attribution.md"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate migration plus runtime health on MySQL.
4. Demonstrate rollback-window metadata emission.

### Incremental Delivery

1. Deliver US1 runtime and migration success path.
2. Deliver US2 behavioral parity on MySQL through contract/integration evidence.
3. Deliver US3 documentation and handover governance.
4. Finish with cross-cutting polish and evidence closure.

### Parallel Team Strategy

1. Developer A: migration/session/runtime code (`database/migrations/versions/0001_current_history_tables.py`, `mcp_server/src/db/session.py`, `mcp_server/src/server.py`).
2. Developer B: contract/integration suite targeting (`mcp_server/tests/contract/`, `mcp_server/tests/integration/`, `mcp_server/tests/conftest.py`).
3. Developer C: handover/evidence docs (`README.md`, `docs/`, `specs/010-postgres-mysql-refactor/`).

---

## Notes

- [P] tasks run on separate files with no dependency on incomplete work.
- Story labels map each task to independently testable user outcomes.
- Commit by task or logical task group for traceable history.
- Keep tier boundaries intact: no Quart direct DB access and no MCP contract shape drift.
