# Tasks: Refactor Database Driver from PostgreSQL to MySQL

**Input**: Design documents from `/specs/009-postgres-to-mysql-refactor/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/no-interface-changes.md`, `quickstart.md`

**Tests**: Automated test execution evidence is mandatory for acceptance. Existing suites and smoke validations MUST be executed and evidenced (no new test files required).

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: `US1`, `US2`, `US3` only for user-story phases
- Every task includes an exact file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare baseline dependencies and implementation scaffolding.

- [ ] T001 Add `PyMySQL>=1.1,<2.0` dependency in `requirements.txt`
- [ ] T002 Capture feature-level implementation scope summary in `specs/009-postgres-to-mysql-refactor/plan.md`
- [ ] T003 [P] Capture final MySQL driver and DB_URL decisions (charset, pool behavior) in `specs/009-postgres-to-mysql-refactor/research.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core runtime changes that block all stories until complete.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [ ] T004 Update SQLAlchemy engine creation with `pool_recycle=3600` and `pool_pre_ping=True` in `mcp_server/src/db/session.py`
- [ ] T005 Verify no schema or migration file changes are introduced (`database/migrations/`, Alembic config) and record scope confirmation in `specs/009-postgres-to-mysql-refactor/research.md`
- [ ] T007 [P] Confirm environment-variable contract examples use `mysql+pymysql://...?...charset=utf8mb4` in `specs/009-postgres-to-mysql-refactor/contracts/no-interface-changes.md`
- [ ] T008 [P] Record constitution re-check evidence after foundational updates in `specs/009-postgres-to-mysql-refactor/plan.md`

**Checkpoint**: Foundation complete — user-story implementation can proceed.

---

## Phase 3: User Story 1 - Developer Configures MySQL Connection (Priority: P1) 🎯 MVP

**Goal**: Developer can configure `DB_URL`, start MCP server, and observe healthy service state on MySQL.

**Independent Test**: Set `DB_URL=mysql+pymysql://...?...charset=utf8mb4`, start MCP server, call `get_system_health`, and capture successful evidence.

### Implementation for User Story 1

- [ ] T009 [US1] Update MySQL environment-variable setup and mandatory charset instructions in `specs/009-postgres-to-mysql-refactor/quickstart.md`
- [ ] T010 [US1] Add MySQL startup prerequisites and expected output steps in `specs/009-postgres-to-mysql-refactor/quickstart.md`
- [ ] T011 [US1] Add MCP startup and health-check walkthrough in `specs/009-postgres-to-mysql-refactor/quickstart.md`
- [ ] T012 [US1] Record MySQL startup and health-check evidence in `docs/test_evidence.md`
- [ ] T012a [US1] Validate unreachable-MySQL behavior using a non-routable `DB_URL` and record `get_system_health` `status=error` evidence in `docs/test_evidence.md`

**Checkpoint**: US1 works independently and is demo-ready.

---

## Phase 4: User Story 2 - Existing Tests Continue to Pass (Priority: P2)

**Goal**: Existing automated tests continue to pass using SQLite fixtures after the MySQL driver refactor.

**Independent Test**: Execute `pytest mcp_server/tests/ -v` and verify no fixture/test changes were required.

### Implementation for User Story 2

- [ ] T013 [US2] Add explicit regression execution steps (`pytest mcp_server/tests/ -v`) in `specs/009-postgres-to-mysql-refactor/quickstart.md`
- [ ] T014 [US2] Add SQLite-fixture compatibility verification note in `specs/009-postgres-to-mysql-refactor/data-model.md`
- [ ] T015 [US2] Record automated test regression results in `docs/test_evidence.md`
- [ ] T016 [US2] Add stale-connection edge-case verification expectations in `specs/009-postgres-to-mysql-refactor/quickstart.md`

**Checkpoint**: US2 passes independently with evidence.

---

## Phase 5: User Story 3 - Documentation Updated to Reflect MySQL (Priority: P3)

**Goal**: Active documentation uses MySQL/PyMySQL examples and only approved historical artifacts retain PostgreSQL references.

**Independent Test**: Run grep verification for `psycopg|postgresql\+psycopg` and confirm only approved historical paths remain.

### Implementation for User Story 3

- [ ] T017 [P] [US3] Replace active `DB_URL` example in `specs/001-define-workflow-tables/quickstart.md`
- [ ] T018 [P] [US3] Update MySQL-primary wording and connection context in `docs/mcp_milestone_test_guide.md`
- [ ] T019 [P] [US3] Replace active PostgreSQL connection examples in `docs/test_evidence.md`
- [ ] T020 [P] [US3] Update feature-001 storage guidance to MySQL in `.github/agents/copilot-instructions.md`
- [ ] T021 [US3] Record explicit historical-reference allowlist for FR-007 validation in `specs/009-postgres-to-mysql-refactor/research.md`
- [ ] T022 [US3] Add grep-based verification procedure and expected pass criteria against the FR-007 allowlist in `specs/009-postgres-to-mysql-refactor/quickstart.md`

**Checkpoint**: US3 documentation outcomes are independently verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks and evidence completion.

- [ ] T023 [P] Execute repo-wide grep verification for `psycopg|postgresql\+psycopg`, validate only FR-007 allowlist matches remain, and record output in `docs/test_evidence.md`
- [ ] T024 Execute final health smoke validation and record output in `docs/test_evidence.md`
- [ ] T025 [P] Update external-source and AI attribution entries for this feature in `docs/source_attribution.md`
- [ ] T026 Reconcile final quickstart command sequence and troubleshooting with validated outputs in `specs/009-postgres-to-mysql-refactor/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2 and validates behavior introduced in US1.
- **Phase 5 (US3)**: Depends on Phase 2; should finalize after US1/US2 so docs reflect validated outcomes.
- **Phase 6 (Polish)**: Depends on completion of all user stories.

### User Story Dependencies

- **US1 (P1)**: Starts immediately after Foundational.
- **US2 (P2)**: Starts after Foundational; uses US1 runtime path for regression confirmation.
- **US3 (P3)**: Starts after Foundational; best completed after US1/US2 evidence is available.

### Within Each User Story

- Update implementation/runbook content first.
- Execute validations and collect evidence second.
- Complete story checkpoint before advancing.

---

## Parallel Opportunities

- **Setup**: `T003` can run in parallel with `T001` and `T002`.
- **Foundational**: `T007` and `T008` can run in parallel after `T004`.
- **US3**: `T017`, `T018`, `T019`, and `T020` can run in parallel (different files).
- **Polish**: `T023` and `T025` can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: "T009 Update MySQL env and charset instructions in specs/009-postgres-to-mysql-refactor/quickstart.md"
Task: "T010 Add startup prerequisite steps in specs/009-postgres-to-mysql-refactor/quickstart.md"
Task: "T011 Add MCP health-check walkthrough in specs/009-postgres-to-mysql-refactor/quickstart.md"
Task: "T012 Record startup and health evidence in docs/test_evidence.md"
```

## Parallel Example: User Story 2

```bash
Task: "T014 Add SQLite fixture compatibility verification in specs/009-postgres-to-mysql-refactor/data-model.md"
Task: "T015 Record pytest regression results in docs/test_evidence.md"
Task: "T013 Add regression execution steps in specs/009-postgres-to-mysql-refactor/quickstart.md"
Task: "T016 Add stale-connection validation expectations in specs/009-postgres-to-mysql-refactor/quickstart.md"
```

## Parallel Example: User Story 3

```bash
Task: "T017 Replace DB_URL example in specs/001-define-workflow-tables/quickstart.md"
Task: "T018 Update MySQL-primary wording in docs/mcp_milestone_test_guide.md"
Task: "T019 Replace PostgreSQL connection examples in docs/test_evidence.md"
Task: "T020 Update storage guidance in .github/agents/copilot-instructions.md"
Task: "T021 Record FR-007 historical allowlist in specs/009-postgres-to-mysql-refactor/research.md"
Task: "T022 Add grep pass criteria in specs/009-postgres-to-mysql-refactor/quickstart.md"
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate US1 independently (startup + health smoke).

### Incremental Delivery

1. Deliver US1 (runtime MySQL path).
2. Deliver US2 (regression confidence for existing tests).
3. Deliver US3 (documentation harmonization and verification).
4. Complete final polish checks.

### Parallel Team Strategy

- **Developer A**: Runtime and dependency updates (`requirements.txt`, `mcp_server/src/db/session.py`, quickstart runtime steps).
- **Developer B**: Validation and evidence (`docs/test_evidence.md`, regression/smoke verification outputs).
- **Developer C**: Documentation harmonization (`docs/`, `specs/001-define-workflow-tables/quickstart.md`, `.github/agents/copilot-instructions.md`).
