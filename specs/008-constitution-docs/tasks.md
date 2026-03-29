# Tasks: Constitution Documentation Compliance Bundle

**Input**: Design documents from `/specs/008-constitution-docs/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/documentation-compliance-contract.md`, `quickstart.md`

**Tests**: Manual compliance checks per `quickstart.md`. Automated documentation compliance tests are out of scope for this feature increment (documentation-only feature).

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

**Authority order** (per `research.md` Decision 2 and `contracts/documentation-compliance-contract.md`):  
Constitution → feature spec/contracts → coverage matrix → README/evidence docs  
All README files are **synchronized delivery surfaces**, not source-of-truth authorities.

---

## Implementation Strategy

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only).  
Completing US1 (coverage matrix) unblocks all subsequent remediation work and is the first independently reviewable increment.

**Delivery Order**: US1 → US2 → US3 (priority-ordered per spec.md).  
User Story 2 should incorporate the conflict-resolution baseline surfaced by US1.  
User Story 3 is best finalized after US1/US2 so attribution/evidence paths are stable.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create working artifacts required for structured documentation remediation.

- [x] T001 Create documentation audit index in `specs/008-constitution-docs/artifacts/doc-audit-index.md`
- [x] T002 Create canonical coverage matrix scaffold at `docs/constitution/coverage-matrix.md` with required columns: `requirement ID`, `status`, `evidence path`, `owner`, `notes` (FR-011, schema from `contracts/documentation-compliance-contract.md`)
- [x] T003 [P] Create remediation work log in `specs/008-constitution-docs/artifacts/remediation-log.md`
- [x] T004 [P] Create unresolved gap tracker template in `specs/008-constitution-docs/artifacts/gap-list.md` (FR-008)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish standards and guardrails that block all user story execution until complete.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [x] T005 Validate partitioned spec coverage — confirm `specs/008-constitution-docs/spec.md` includes MCP (Logic), Web-Tier (Routes), and Page (UI) sections and that all FR-001–FR-011 requirements are present (FR-009); record pass/fail result in `specs/008-constitution-docs/artifacts/spec-partition-validation.md`
- [x] T006 [P] Define constitutional requirement ID registry and canonical naming rules in `specs/008-constitution-docs/artifacts/requirement-registry.md`
- [x] T007 [P] Record normative authority order and README-as-delivery-surface policy in `specs/008-constitution-docs/artifacts/source-of-truth.md` (research.md Decision 2)
- [x] T008 [P] Define technology-agnostic requirement-language guardrails in `specs/008-constitution-docs/artifacts/requirement-language-rules.md` (FR-010)

**Checkpoint**: Foundation complete; user story work can proceed independently.

---

## Phase 3: User Story 1 - Constitution Coverage Audit (Priority: P1) 🎯 MVP

**Goal**: Produce a complete constitution-to-document compliance audit with explicit status, evidence, and ownership for every documented obligation.

**Independent Test**: Verify `docs/constitution/coverage-matrix.md` maps all constitutional documentation obligations with valid `requirement ID`, `status`, `evidence path`, `owner`, and `notes` columns populated (SC-001). Each `partial` or `missing` row has a remediation note.

### Implementation for User Story 1

- [x] T009 [P] [US1] Extract all constitution documentation obligation rows into `docs/constitution/coverage-matrix.md` — one row per requirement (FR-001, FR-011)
- [x] T010 [P] [US1] Map evidence artifact paths from `README.md`, `docs/README.md`, `mcp_server/README.md`, `flask_web/README.md`, `quart_web/README.md`, `docs/source_attribution.md`, and `docs/test_evidence.md` into `docs/constitution/coverage-matrix.md`
- [x] T011 [US1] Set `compliant`/`partial`/`missing` status and complete notes column per row in `docs/constitution/coverage-matrix.md`
- [x] T012 [US1] Record all identified documentation contradictions and their authoritative source resolutions in `specs/008-constitution-docs/artifacts/remediation-log.md` (FR-007)
- [x] T013 [US1] Capture all missing documentation obligations with ownership assignment and recommended destination file in `specs/008-constitution-docs/artifacts/gap-list.md` (FR-008)
- [x] T014 [US1] Write US1 audit validation summary capturing SC-001 result in `specs/008-constitution-docs/artifacts/us1-validation.md`

**Checkpoint**: User Story 1 is independently complete. Coverage matrix exists; all obligations mapped; contradictions and gaps recorded.

---

## Phase 4: User Story 2 - Remediation and Canonical Runbooks (Priority: P1)

**Goal**: Make startup/run/test documentation accurate, consistent, and reproducible from a clean Windows environment.

**Independent Test**: Following only the documented Windows runbook in `README.md`, a reviewer can start required MCP and web tier services and run documented tests without any undocumented steps (SC-002, SC-003).

### Implementation for User Story 2

- [x] T015 [P] [US2] Normalize canonical Windows-first run/test flow in `README.md` — one primary runbook with transport use-case labels (`stdio` for inspector/local, `http`/`sse` for network/web-tier) and environment variable table (FR-002, FR-003, FR-004, research.md Decisions 3 & 4)
- [x] T016 [P] [US2] Align MCP startup commands, transport guidance, and environment variable names in `mcp_server/README.md` — link back to canonical runbook in root `README.md`
- [x] T017 [P] [US2] Align Quart startup instructions and environment variable guidance in `quart_web/README.md` — link back to canonical runbook in root `README.md`
- [x] T018 [P] [US2] Align supplementary Flask web-tier guidance in `flask_web/README.md` — link back to canonical runbook and label as legacy/supplementary where applicable
- [x] T019 [US2] Reconcile cross-document command consistency and resolve naming conflicts identified in US1 remediation log in `docs/README.md` (FR-003, FR-007)
- [x] T020 [US2] Update reproducibility verification procedure and expected terminal output in `specs/008-constitution-docs/quickstart.md`
- [x] T021 [US2] Record startup reproducibility evidence and verification outcome in `docs/test_evidence.md` (SC-002)

**Checkpoint**: User Story 2 is independently reproducible. Canonical runbook exists; all supplementary READMEs aligned and linked.

---

## Phase 5: User Story 3 - Traceability and Attribution Completion (Priority: P2)

**Goal**: Complete attribution records, evidence references, and reviewer navigation so the development process is auditable from the main README entry point.

**Independent Test**: Starting from `README.md` only, a reviewer can navigate to: source attribution, test evidence, spec artifacts, and coverage matrix. All referenced paths resolve to existing files (SC-004, SC-005).

### Implementation for User Story 3

- [x] T022 [P] [US3] Complete external source attribution records for all documentation references in `docs/source_attribution.md` (FR-005)
- [x] T023 [P] [US3] Add README traceability section with pointer links to coverage matrix, source attribution, test evidence, and feature spec artifacts in `README.md` (FR-005, FR-006)
- [x] T024 [US3] Add cross-reference links and reviewer navigation cues from docs hub in `docs/README.md` (FR-006)
- [x] T025 [US3] Update prompt/process trace entries for this feature in `docs/prompts/prompt_log.md` (FR-005)
- [x] T026 [US3] Validate Principle V (Traceable Academic-Quality Delivery) evidence artifact path consistency and resolve any broken references in `docs/test_evidence.md` (FR-005)
- [x] T027 [US3] Capture traceability validation results for SC-004 and SC-005 in `specs/008-constitution-docs/artifacts/us3-validation.md`

**Checkpoint**: User Story 3 is independently auditable. All attribution/evidence paths present; README navigation path complete.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency pass across all stories and artifacts to confirm constitutional compliance before feature close.

- [x] T028 [P] Perform cross-document terminology and architecture boundary consistency sweep across `README.md`, `docs/README.md`, `mcp_server/README.md`, `quart_web/README.md`, and `flask_web/README.md` — verify tier naming and MCP communication boundary language aligns (FR-007, SC-003)
- [x] T029 [P] Finalize ownership assignments and unresolved-gap follow-up notes in `docs/constitution/coverage-matrix.md` (FR-008)
- [x] T030 Update implementation outcomes and decisions in `specs/008-constitution-docs/plan.md`
- [x] T031 Run final reviewer smoke check per `quickstart.md` Section 6 and capture pass/fail results in `specs/008-constitution-docs/artifacts/final-validation.md`

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Blocks |
|-------|-----------|--------|
| Phase 1 (Setup) | — | Phase 2 |
| Phase 2 (Foundational) | Phase 1 | Phases 3, 4, 5 |
| Phase 3 (US1) | Phase 2 | Final Phase |
| Phase 4 (US2) | Phase 2 + US1 conflict-resolution baseline | Final Phase |
| Phase 5 (US3) | Phase 2 + best after US1/US2 | Final Phase |
| Final Phase | All user stories selected for increment | — |

### User Story Dependencies

- **US1 (P1)**: Independent — starts after Phase 2.
- **US2 (P1)**: Starts after Phase 2; should incorporate US1 contradiction-resolution baseline for command consistency.
- **US3 (P2)**: Starts after Phase 2; best finalized after US1/US2 so attribution and evidence paths are stable.

Recommended completion order: **US1 → US2 → US3**.

### Within Each User Story

- Core audit/documentation updates before validation summaries
- Evidence capture after primary documentation is complete
- Story validation artifact written last

---

## Parallel Execution Opportunities

### Phase 1
- `T003` and `T004` can run in parallel with `T001`/`T002` (different files).

### Phase 2
- `T006`, `T007`, `T008` can run in parallel (different files) after `T005`.

### Phase 3 (US1) — Parallel example
- `T009` (extract requirements) and `T010` (map evidence paths) can run in parallel before merging at `T011`.

### Phase 4 (US2) — Parallel example
- `T015` (`README.md`), `T016` (`mcp_server/README.md`), `T017` (`quart_web/README.md`), `T018` (`flask_web/README.md`) can all run in parallel (different files).

### Phase 5 (US3) — Parallel example
- `T022` (`docs/source_attribution.md`) and `T023` (`README.md`) can run in parallel before `T024`–`T027`.

### Final Phase
- `T028` and `T029` can run in parallel (different files).

### Parallel Example: User Story 3

- Task: `T022` in `docs/source_attribution.md`
- Task: `T023` in `README.md`
