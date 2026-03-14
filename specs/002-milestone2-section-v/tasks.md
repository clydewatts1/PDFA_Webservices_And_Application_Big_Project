# Tasks: Milestone 2 Section V Alignment

**Input**: Design documents from `/specs/002-milestone2-section-v/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/section-v-compliance-review.md`, `quickstart.md`

**Tests**: No new automated tests are required by the specification; validation is checklist and review-contract driven, with optional regression pytest execution.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish compliance artifacts and implementation workspace for Section V remediation.

- [X] T001 Create compliance evidence folder and index in specs/002-milestone2-section-v/artifacts/README.md
- [X] T002 Create docstring review rubric in specs/002-milestone2-section-v/artifacts/docstring-rubric.md
- [X] T003 [P] Create boilerplate-comment exception template in specs/002-milestone2-section-v/artifacts/boilerplate-exceptions.md
- [X] T004 [P] Create Section V evidence ledger template in specs/002-milestone2-section-v/artifacts/evidence-ledger.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Produce auditable inventories and traceability mappings required by all user stories.

**⚠️ CRITICAL**: No user story remediation work starts until these artifacts are completed.

- [X] T005 Build in-scope file inventory in specs/002-milestone2-section-v/artifacts/file-inventory.md
- [X] T006 [P] Build custom-logic docstring audit list in specs/002-milestone2-section-v/artifacts/docstring-audit.md
- [X] T007 [P] Build framework-boilerplate review list in specs/002-milestone2-section-v/artifacts/boilerplate-audit.md
- [X] T008 Build major-directory README coverage matrix in specs/002-milestone2-section-v/artifacts/readme-coverage.md
- [X] T009 Build attribution cross-reference matrix in specs/002-milestone2-section-v/artifacts/traceability-matrix.md
- [X] T010 Build commit-traceability checkpoint plan in specs/002-milestone2-section-v/artifacts/commit-traceability-plan.md

**Checkpoint**: Foundation evidence is ready; story work can now proceed.

---

## Phase 3: User Story 1 - Bring Custom Business Logic Documentation into Compliance (Priority: P1) 🎯 MVP

**Goal**: Ensure custom business logic uses required module/function docstrings and framework boilerplate avoids over-commenting.

**Independent Test**: Review sampled files listed in `artifacts/docstring-audit.md` and `artifacts/boilerplate-audit.md`; confirm docstrings exist where required and unnecessary boilerplate comments are absent.

### Implementation for User Story 1

- [X] T011 [P] [US1] Remediate module/function docstrings in mcp_server/src/services/workflow_service.py
- [X] T012 [P] [US1] Remediate module/function docstrings in mcp_server/src/services/dependent_service.py
- [X] T013 [P] [US1] Remediate module/function docstrings in mcp_server/src/services/instance_service.py
- [X] T014 [P] [US1] Remediate module/function docstrings in mcp_server/src/services/validation.py
- [X] T015 [P] [US1] Remediate module/function docstrings in mcp_server/src/api/handlers/workflow_handlers.py
- [X] T016 [P] [US1] Remediate module/function docstrings in mcp_server/src/api/handlers/dependent_handlers.py
- [X] T017 [P] [US1] Remediate module/function docstrings in mcp_server/src/api/handlers/instance_handlers.py
- [X] T018 [P] [US1] Remediate module/function docstrings in mcp_server/src/api/app.py
- [X] T019 [P] [US1] Remediate module/function docstrings in mcp_server/src/db/session.py
- [X] T020 [P] [US1] Remediate module/function docstrings in flask_web/src/clients/mcp_client.py
- [X] T021 [P] [US1] Remediate module/function docstrings in flask_web/src/routes/workflow.py
- [X] T022 [P] [US1] Remediate module/function docstrings in flask_web/src/routes/dependent.py
- [X] T023 [P] [US1] Remediate module/function docstrings in flask_web/src/routes/instance.py
- [X] T024 [US1] Remediate module/function docstrings and boundary notes in flask_web/src/app.py
- [X] T025 [US1] Remove unnecessary inline boilerplate commentary in database/migrations/env.py
- [X] T026 [US1] Remove unnecessary inline boilerplate commentary in database/migrations/versions/0001_current_history_tables.py
- [X] T027 [US1] Record retained-comment justifications with reviewer approval in specs/002-milestone2-section-v/artifacts/boilerplate-exceptions.md
- [X] T028 [US1] Record self-evident function exceptions with rationale in specs/002-milestone2-section-v/artifacts/docstring-exceptions.md

**Checkpoint**: User Story 1 is complete when declared inventory files satisfy docstring and boilerplate-comment policy requirements.

---

## Phase 4: User Story 2 - Complete Major-Directory Documentation Coverage (Priority: P2)

**Goal**: Provide supplementary README coverage for each major directory and align top-level documentation references.

**Independent Test**: Verify each in-scope major directory has a local README describing local architecture and boundary responsibilities.

### Implementation for User Story 2

- [X] T029 [US2] Discover first-level submission-scope directories and mark coverage status in specs/002-milestone2-section-v/artifacts/readme-coverage.md
- [X] T030 [P] [US2] Create local architecture README in database/README.md
- [X] T031 [P] [US2] Create local architecture README in docs/README.md
- [X] T032 [P] [US2] Create local architecture README in mcp_server/README.md
- [X] T033 [P] [US2] Create local architecture README in flask_web/README.md
- [X] T034 [US2] Update top-level Section V guidance and directory links in README.md
- [X] T035 [US2] Update README coverage tracker with final status and out-of-scope rationale in specs/002-milestone2-section-v/artifacts/readme-coverage.md

**Checkpoint**: User Story 2 is complete when all in-scope major directories have compliant supplementary README files and top-level README references them.

---

## Phase 5: User Story 3 - Preserve Attribution and Submission Traceability (Priority: P3)

**Goal**: Keep attribution and prompt traceability current and auditable after Milestone 2 documentation/code updates.

**Independent Test**: From README entry points, reach source attribution and prompt log evidence directly and confirm consistency.

### Implementation for User Story 3

- [X] T036 [US3] Update external-source and AI usage details in docs/source_attribution.md
- [X] T037 [US3] Append Milestone 2 implementation log entry in docs/prompts/prompt_log.md
- [X] T038 [US3] Update attribution linkage map with final paths in specs/002-milestone2-section-v/artifacts/traceability-matrix.md
- [X] T039 [US3] Produce Section V compliance result record in specs/002-milestone2-section-v/artifacts/section-v-compliance-result.json
- [X] T040 [US3] Cross-check compliance output schema against contracts/section-v-compliance-review.md
- [X] T041 [US3] Execute timed discoverability walkthrough and store results in specs/002-milestone2-section-v/artifacts/discoverability-timed-run.md
- [X] T042 [US3] Perform commit-traceability audit against checkpoint plan in specs/002-milestone2-section-v/artifacts/commit-traceability-audit.md

**Checkpoint**: User Story 3 is complete when attribution and prompt-traceability evidence is current, linked, and contract-compliant.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency sweep and end-to-end validation across all stories.

- [X] T043 [P] Run formatting and lint consistency pass on edited Python files via .venv/Scripts/python.exe -m ruff check mcp_server/src flask_web/src database/migrations
- [X] T044 [P] Execute optional regression validation via .venv/Scripts/python.exe -m pytest mcp_server/tests/ -v --tb=short
- [X] T045 Validate quickstart compliance walk-through in specs/002-milestone2-section-v/quickstart.md
- [X] T046 Reconcile checklist findings and mark completed items in specs/002-milestone2-section-v/checklists/section-v.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion; can run in parallel with US1 if staffed.
- **Phase 5 (US3)**: Depends on Phase 2 completion; should run after US2 documentation updates for final traceability consistency.
- **Phase 6 (Polish)**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Independent once foundational inventories are ready.
- **US2 (P2)**: Independent once foundational inventories are ready; benefits from US1 completion for wording consistency.
- **US3 (P3)**: Depends on US2 for final README link targets and on US1 for final docstring/boilerplate evidence status.

### Parallel Opportunities

- Setup artifacts `T003` and `T004` are parallelizable.
- Foundational audits `T006` and `T007` are parallelizable.
- US1 remediation tasks `T011`-`T023` are parallelizable because they target different files.
- US2 README creation tasks `T030`-`T033` are parallelizable.
- Polish tasks `T043` and `T044` are parallelizable.

---

## Parallel Example: User Story 1

```bash
# Run docstring remediation on separate files concurrently:
Task: "T010 Remediate module/function docstrings in mcp_server/src/services/workflow_service.py"
Task: "T019 Remediate module/function docstrings in flask_web/src/clients/mcp_client.py"
Task: "T022 Remediate module/function docstrings in flask_web/src/routes/instance.py"
```

## Parallel Example: User Story 2

```bash
# Create directory-level READMEs concurrently:
Task: "T030 Create local architecture README in database/README.md"
Task: "T031 Create local architecture README in docs/README.md"
Task: "T032 Create local architecture README in mcp_server/README.md"
Task: "T033 Create local architecture README in flask_web/README.md"
```

## Parallel Example: User Story 3

```bash
# Update independent traceability artifacts in parallel:
Task: "T036 Update external-source and AI usage details in docs/source_attribution.md"
Task: "T037 Append Milestone 2 implementation log entry in docs/prompts/prompt_log.md"
Task: "T038 Update attribution linkage map in specs/002-milestone2-section-v/artifacts/traceability-matrix.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) docstring and boilerplate compliance.
3. Validate US1 independently using `artifacts/docstring-audit.md` and `artifacts/boilerplate-audit.md`.

### Incremental Delivery

1. Setup + foundational evidence artifacts.
2. Deliver US1 (code docstring/boilerplate compliance).
3. Deliver US2 (directory-level README coverage).
4. Deliver US3 (attribution and traceability preservation).
5. Run final polish validation before hand-up.

### Team Parallelization

1. One contributor leads foundational audits (T005-T010).
2. One contributor executes US1 code remediation tasks.
3. One contributor executes US2 README creation tasks.
4. One contributor finalizes US3 attribution + prompt traceability + timed and commit-traceability artifacts.
5. Merge all streams into Phase 6 validation.
