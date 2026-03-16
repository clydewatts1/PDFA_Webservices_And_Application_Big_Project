# Tasks: MCP Server FastMCP Refactor

**Input**: Design documents from `/specs/005-fastmcp-refactor/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/mcp-runtime-fastmcp.md`, `quickstart.md`

**Tests**: Include automated tests because the specification explicitly requires runtime/transport, temporal, and cross-transport parity validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`) for story-phase tasks only
- Every task includes an explicit file path

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare FastMCP runtime scaffolding and transport startup configuration surfaces.

- [X] T001 Add FastMCP runtime startup argument parsing for `stdio|sse|streamable-http` in `mcp_server/src/server.py`
- [X] T002 Add typed runtime profile/config helpers for transport/host/port/env validation in `mcp_server/src/lib/runtime_profile.py`
- [X] T003 [P] Create FastMCP runtime package exports for MCP-tier entrypoints in `mcp_server/src/api/__init__.py`
- [X] T004 [P] Document required transport environment variables and examples in `.env.example`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Remove custom MCP-tier protocol orchestration and establish shared FastMCP registration infrastructure.

**⚠️ CRITICAL**: Complete this phase before any user story implementation.

- [X] T005 Remove MCP-tier custom Flask JSON-RPC/queue/SSE routing surfaces from runtime wiring in `mcp_server/src/api/app.py`
- [X] T006 Replace custom runtime bootstrap with FastMCP server construction and transport dispatch in `mcp_server/src/server.py`
- [X] T007 Build in-code tool metadata and registration catalog for in-scope tools in `mcp_server/src/lib/tool_catalog.py`
- [X] T008 [P] Refactor adapter registration to bind handlers via FastMCP-native registration flow in `mcp_server/src/lib/tool_adapter.py`
- [X] T009 [P] Add startup guardrails and invalid-transport error handling for runtime profile validation in `mcp_server/src/lib/runtime_profile.py`
- [X] T010 [P] Add shared FastMCP test harness helpers for stdio/sse/http runtime bootstrapping in `mcp_server/tests/conftest.py`

**Checkpoint**: Foundation complete; user stories can be implemented and validated independently.

---

## Phase 3: User Story 1 - Replace Custom MCP Runtime (Priority: P1) 🎯 MVP

**Goal**: Deliver MCP-tier FastMCP runtime ownership for all required transports without legacy MCP-tier Flask protocol handlers.

**Independent Test**: Start MCP runtime on `stdio`, `sse`, and `streamable-http` and verify startup works through FastMCP entrypoints with no custom `/rpc` envelope path in MCP tier.

### Tests for User Story 1

- [ ] T011 [P] [US1] Add runtime startup test coverage for `stdio` transport boot path in `mcp_server/tests/runtime/test_runtime_startup.py`
- [ ] T012 [P] [US1] Add runtime startup smoke coverage for `sse` and `streamable-http` boot paths in `mcp_server/tests/runtime/test_runtime_startup.py`

### Implementation for User Story 1

- [ ] T013 [US1] Remove remaining MCP-tier legacy protocol helper functions and dead routing code in `mcp_server/src/api/app.py`
- [ ] T014 [US1] Implement canonical FastMCP runtime factory used by all transports in `mcp_server/src/server.py`
- [ ] T015 [US1] Wire `stdio` execution mode to the shared FastMCP runtime factory in `mcp_server/src/server.py`
- [ ] T016 [US1] Wire `sse` execution mode to the shared FastMCP runtime factory in `mcp_server/src/server.py`
- [ ] T017 [US1] Wire `streamable-http` execution mode to the shared FastMCP runtime factory in `mcp_server/src/server.py`
- [ ] T018 [US1] Remove YAML-dependent MCP tool-metadata loading from runtime startup flow in `mcp_server/src/lib/tool_adapter.py`

**Checkpoint**: User Story 1 is independently functional and demonstrable as the MVP runtime migration.

---

## Phase 4: User Story 2 - Preserve Tool Contracts Across Transports (Priority: P2)

**Goal**: Keep in-scope tool names and business semantics stable while using FastMCP-native transport contracts.

**Independent Test**: Discover and call in-scope tools through FastMCP-backed runtime and confirm canonical tool names, response-shape contract (`status`, `status_message`, `data`), and equivalent business semantics.

### Tests for User Story 2

- [ ] T019 [P] [US2] Add in-scope tool discovery contract test for canonical names in `mcp_server/tests/runtime/test_tool_discovery_catalog.py`
- [ ] T020 [P] [US2] Add `stdio` behavioral parity tests for health/auth/workflow-domain tools in `mcp_server/tests/runtime/test_stdio_tool_behavior.py`
- [ ] T021 [P] [US2] Add `sse` startup/discovery/basic-call smoke tests in `mcp_server/tests/runtime/test_sse_smoke.py`
- [ ] T022 [P] [US2] Add `streamable-http` startup/discovery/basic-call smoke tests in `mcp_server/tests/runtime/test_streamable_http_smoke.py`
- [ ] T023 [P] [US2] Add cross-transport parity assertions for equivalent tool inputs (`stdio` vs `sse` vs `streamable-http`) with metadata-normalized comparison in `mcp_server/tests/runtime/test_transport_parity.py`

### Implementation for User Story 2

- [ ] T024 [US2] Register `get_system_health`, `user_logon`, and `user_logoff` with unchanged names in `mcp_server/src/lib/tool_catalog.py`
- [ ] T025 [US2] Register `workflow.*` and `role.*` tool families with unchanged canonical names in `mcp_server/src/lib/tool_catalog.py`
- [ ] T026 [US2] Register `interaction.*`, `guard.*`, and `interaction_component.*` with unchanged canonical names in `mcp_server/src/lib/tool_catalog.py`
- [ ] T027 [US2] Enforce out-of-scope exclusion of `unit_of_work.*` and `instance.*` from required migration catalog in `mcp_server/src/lib/tool_catalog.py`
- [ ] T028 [US2] Align tool result mapping to standardized MCP call-tool response shape in `mcp_server/src/lib/tool_adapter.py`
- [ ] T029 [US2] Ensure transport-agnostic execution path routes all in-scope tool calls through shared service handlers in `mcp_server/src/lib/tool_adapter.py`

**Checkpoint**: User Story 2 preserves in-scope tool contracts and transport parity expectations.

---

## Phase 5: User Story 3 - Modernize MCP Test Coverage (Priority: P3)

**Goal**: Validate FastMCP runtime behavior with boundary-aware tests while preserving temporal `_Hist` invariants.

**Independent Test**: Run MCP-tier suite showing full `stdio` behavior coverage, `sse`/`streamable-http` smoke coverage, transport parity assertions, and explicit temporal assertions for update/delete flows.

### Tests for User Story 3

- [ ] T030 [P] [US3] Add temporal update assertions for `_Hist` writes and single-current-row invariants in `mcp_server/tests/runtime/test_temporal_integrity.py`
- [ ] T031 [P] [US3] Add temporal delete assertions for `_Hist` writes and atomicity in `mcp_server/tests/runtime/test_temporal_integrity.py`
- [ ] T032 [P] [US3] Add boundary-aware MCP-only runtime tests ensuring no Flask request-handler dependency in `mcp_server/tests/runtime/test_boundary_runtime.py`

### Implementation for User Story 3

- [ ] T033 [US3] Update MCP runtime test fixtures to use FastMCP/asyncio harness patterns in `mcp_server/tests/conftest.py`
- [ ] T034 [US3] Update existing workflow-domain MCP tests to consume new runtime fixtures in `mcp_server/tests/test_workflow.py`
- [ ] T035 [US3] Update existing role/interaction/guard MCP tests to consume new runtime fixtures in `mcp_server/tests/test_role_interaction_guard.py`
- [ ] T036 [US3] Update existing interaction-component MCP tests to consume new runtime fixtures in `mcp_server/tests/test_interaction_component.py`

**Checkpoint**: User Story 3 verifies runtime migration quality and constitutional temporal guarantees.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finalize docs, validation commands, and cleanups spanning multiple stories.

- [ ] T037 [P] Update MCP runtime startup and transport validation guidance in `specs/005-fastmcp-refactor/quickstart.md`
- [ ] T038 [P] Update reviewer-facing FastMCP transport run instructions in `README.md`
- [ ] T039 Remove obsolete MCP-tier custom runtime documentation references from `docs/prompts/prompt_log.md`
- [ ] T040 Run and record full MCP-tier regression command set for this feature in `docs/test_evidence.md`
- [ ] T041 Verify in-code tool metadata replaces YAML runtime dependency and note deprecation outcome in `specs/005-fastmcp-refactor/research.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2 completion.
- **Phase 4 (US2)**: Depends on Phase 2 completion and benefits from US1 runtime factory completion.
- **Phase 5 (US3)**: Depends on Phase 2 completion and on US1/US2 runtime + tool registration outputs.
- **Phase 6 (Polish)**: Depends on completion of desired user stories.

### User Story Dependencies

- **US1 (P1)**: Starts immediately after foundational phase; no dependency on other stories.
- **US2 (P2)**: Starts after foundational phase; depends on shared runtime scaffolding from US1 for parity verification.
- **US3 (P3)**: Starts after foundational phase; depends on US1/US2 artifacts to validate runtime/contract behavior.

### Dependency Graph

- `Setup -> Foundational -> US1 -> US2 -> US3 -> Polish`
- `Setup -> Foundational -> US2` (can begin once foundation is complete if runtime factory tasks are ready)
- `Setup -> Foundational -> US3` (test modernization begins once runtime/tool registrations are stabilized)

### Within Each User Story

- Tests are authored before or alongside implementation and must fail before implementation is finalized.
- Registration/catalog tasks precede behavior-parity assertions.
- Runtime fixtures precede suite-wide test migration tasks.

---

## Parallel Execution Examples

## Parallel Example: User Story 1

```bash
Task: "T011 [US1] Add runtime startup test coverage for stdio transport boot path in mcp_server/tests/runtime/test_runtime_startup.py"
Task: "T012 [US1] Add runtime startup smoke coverage for sse and streamable-http boot paths in mcp_server/tests/runtime/test_runtime_startup.py"
```

## Parallel Example: User Story 2

```bash
Task: "T019 [US2] Add in-scope tool discovery contract test in mcp_server/tests/runtime/test_tool_discovery_catalog.py"
Task: "T021 [US2] Add sse startup/discovery/basic-call smoke tests in mcp_server/tests/runtime/test_sse_smoke.py"
Task: "T022 [US2] Add streamable-http startup/discovery/basic-call smoke tests in mcp_server/tests/runtime/test_streamable_http_smoke.py"
Task: "T023 [US2] Add cross-transport parity assertions in mcp_server/tests/runtime/test_transport_parity.py"
```

## Parallel Example: User Story 3

```bash
Task: "T030 [US3] Add temporal update assertions in mcp_server/tests/runtime/test_temporal_integrity.py"
Task: "T031 [US3] Add temporal delete assertions in mcp_server/tests/runtime/test_temporal_integrity.py"
Task: "T032 [US3] Add boundary-aware MCP-only runtime tests in mcp_server/tests/runtime/test_boundary_runtime.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate all three transports start through FastMCP without custom MCP-tier routing.

### Incremental Delivery

1. Deliver US1 runtime migration (MVP).
2. Deliver US2 tool contract parity and transport smoke/parity validations.
3. Deliver US3 test modernization and temporal/boundary assertions.
4. Finish with Phase 6 documentation and evidence updates.

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. After foundation:
   - Developer A: US1 runtime transport wiring.
   - Developer B: US2 tool registration and parity tests.
   - Developer C: US3 temporal/boundary test modernization.

---

## Notes

- `[P]` tasks are parallelizable when they do not depend on unfinished tasks and do not create same-file merge contention.
- Story labels are applied only in user-story phases for traceability.
- Task list reflects clarified feature scope: MCP-tier only, FastMCP-native HTTP contracts, in-code tool metadata, response-shape contract enforcement, and split transport test depth.