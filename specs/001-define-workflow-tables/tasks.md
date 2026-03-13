---
description: "Task list for workflow interaction schema temporary application"
---

# Tasks: Workflow Interaction Schema Foundation

**Input**: Design documents from `/specs/001-define-workflow-tables/`
**Prerequisites**: plan.md, spec.md
**Tests**: Required for this feature (object-creation tests are mandatory)

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup (Shared Infrastructure)

- [x] T001 Create three-tier folders: `mcp_server/`, `flask_web/`, `database/`
- [x] T002 Initialize Python project dependencies for MCP and Flask apps
- [x] T003 [P] Configure linting/formatting (`ruff`, `black`) and pytest config
- [x] T004 [P] Add `.env.example` for database credentials and MCP/Flask URLs

---

## Phase 2: Foundational (Blocking)

- [x] T005 Define SQLAlchemy base models and control-column mixin in `mcp_server/src/models/base.py`
- [x] T006 Create Alembic migration baseline for current and `_Hist` tables in `database/migrations/`
- [x] T007 Implement object factory library skeleton in `mcp_server/src/lib/object_factory.py`
- [x] T008 [P] Implement MCP JSON-RPC routing and error envelope in `mcp_server/src/api/`
- [x] T009 [P] Implement Flask MCP HTTP client wrapper in `flask_web/src/clients/mcp_client.py`
- [x] T010 Add shared validation utilities for temporal and delete-state rules in `mcp_server/src/services/validation.py`

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Workflow with History (P1) 🎯

**Goal**: Create/update/delete Workflow with current/history snapshot behavior.

### Tests (write first)

- [x] T011 [P] [US1] Unit tests for Workflow object creation in `mcp_server/tests/unit/test_object_factory_workflow.py`
- [x] T012 [P] [US1] Contract tests for `workflow.create` and `workflow.update` in `mcp_server/tests/contract/test_workflow_contract.py`
- [x] T013 [P] [US1] Integration test Flask -> MCP -> DB workflow creation in `mcp_server/tests/integration/test_workflow_e2e.py`

### Implementation

- [x] T014 [US1] Implement `Workflow` and `Workflow_Hist` models in `mcp_server/src/models/workflow.py`
- [x] T015 [US1] Implement object factory methods for Workflow defaults/validation
- [x] T016 [US1] Implement MCP handlers for create/update/get/list/delete workflow tools
- [x] T017 [US1] Add temporary Flask route/page for Workflow create/list in `flask_web/src/routes/workflow.py`

**Checkpoint**: Workflow maintenance independently testable.

---

## Phase 4: User Story 2 - Role/Interaction/Guard/InteractionComponent/UnitOfWork (P2)

**Goal**: Manage workflow-scoped dependent objects with history snapshots.

### Tests (write first)

- [x] T018 [P] [US2] Unit tests for object factory methods for Role/Interaction/Guard/InteractionComponent/UnitOfWork in `mcp_server/tests/unit/test_object_factory_dependent_entities.py`
- [x] T019 [P] [US2] Contract tests for dependent-entity create/update methods in `mcp_server/tests/contract/test_dependent_entities_contract.py`
- [x] T020 [P] [US2] Integration tests for invalid workflow linkage and temporal failures in `mcp_server/tests/integration/test_dependent_entities_integrity.py`

### Implementation

- [x] T021 [US2] Implement dependent current/history models in `mcp_server/src/models/`
- [x] T022 [US2] Implement factory and validation methods for all dependent entities
- [x] T023 [US2] Implement MCP handlers for dependent entity CRUD operations
- [x] T024 [US2] Add temporary Flask routes/pages for dependent entity create/list flows

**Checkpoint**: Workflow + dependent entities independently testable.

---

## Phase 5: User Story 3 - Instance Creation and Replication (P3)

**Goal**: Create runnable instances and replicate design-time records at instantiation.

### Tests (write first)

- [x] T025 [P] [US3] Unit tests for Instance object creation and state transitions in `mcp_server/tests/unit/test_object_factory_instance.py`
- [x] T026 [P] [US3] Contract tests for `instance.create` and replication behavior in `mcp_server/tests/contract/test_instance_contract.py`
- [x] T027 [P] [US3] Integration test for end-to-end instantiation replication in `mcp_server/tests/integration/test_instance_replication_e2e.py`

### Implementation

- [x] T028 [US3] Implement `Instance` and `Instance_Hist` models in `mcp_server/src/models/instance.py`
- [x] T029 [US3] Implement instantiation service to replicate Role/Interaction/Guard/InteractionComponent records
- [x] T030 [US3] Implement MCP handlers for instance create/state transitions/listing
- [x] T031 [US3] Add temporary Flask route/page for instance create and state update

**Checkpoint**: All stories independently functional.

---

## Phase 6: Polish & Cross-Cutting

- [x] T032 [P] Add structured logging and error mapping consistency across Flask/MCP
- [x] T033 [P] Add README section for setup/run/test of temporary app
- [x] T034 Update external-source attribution docs (AI prompts, Spec Kit usage)
- [x] T035 Run full test suite and capture results for hand-up evidence

---

## Dependencies & Execution Order

- Setup (T001-T004) -> Foundational (T005-T010) -> US1 (T011-T017) -> US2 (T018-T024) -> US3 (T025-T031) -> Polish (T032-T035)
- Tasks marked [P] can run in parallel once prerequisites are satisfied.
- Test tasks precede implementation tasks within each user story.
