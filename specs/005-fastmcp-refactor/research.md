# Research: MCP Server FastMCP Refactor

## Decision 1: FastMCP-Native Runtime Ownership
- Decision: Replace MCP-tier custom Flask/Quart protocol handling with FastMCP runtime ownership for `stdio`, `sse`, and `streamable-http`.
- Rationale: Constitution Principle II.a mandates FastMCP and explicitly rejects custom framework-managed JSON-RPC/event routing in the MCP tier.
- Alternatives considered: Keep existing Flask runtime and wrap FastMCP partially; rejected because it preserves forbidden custom protocol orchestration.

## Decision 2: MCP-Only Refactor Scope
- Decision: Limit this feature to MCP-tier runtime refactor with no required Flask-side integration changes.
- Rationale: Keeps the increment reviewable and isolates risk to runtime migration while preserving the architecture boundary.
- Alternatives considered: Include Flask integration migration in the same feature; rejected to avoid scope coupling and mixed-failure diagnosis.

## Decision 3: In-Scope Tool Set Preservation
- Decision: Preserve only the clarified in-scope tool family set for this increment (`get_system_health`, `user_logon`, `user_logoff`, `workflow.*`, `role.*`, `interaction.*`, `guard.*`, `interaction_component.*`).
- Rationale: Matches feature 004 milestone boundary and avoids broadening migration risk.
- Alternatives considered: Migrate all tools including `unit_of_work.*` and `instance.*`; rejected as out-of-scope expansion.

## Decision 4: Tool Metadata Source Migration
- Decision: Deprecate YAML as the source of MCP tool metadata and define tool metadata/registration directly in Python FastMCP code.
- Rationale: Reduces indirection in runtime registration and aligns with explicit decorator/native registration goals for FastMCP.
- Alternatives considered: Keep YAML as canonical tool metadata source; rejected by clarification decision.

## Decision 5: HTTP Contract Migration Strategy
- Decision: Adopt FastMCP-native `sse` and `streamable-http` behavior; do not preserve custom Flask `/rpc` and custom SSE envelope compatibility shims.
- Rationale: Supports complete removal of custom MCP-tier protocol routing and reduces duplicate protocol maintenance.
- Alternatives considered: Preserve legacy custom HTTP contracts during migration; rejected to prevent long-lived dual contract complexity.

## Decision 6: Transport Test Strategy
- Decision: Use full in-scope behavior coverage on `stdio`; use startup/discovery/basic-call smoke coverage on `sse` and `streamable-http`.
- Rationale: Maximizes confidence in shared tool logic while avoiding triple duplicated end-to-end behavioral suite overhead.
- Alternatives considered: full behavioral tests for all transports; rejected for maintenance cost in this refactor increment.

## Decision 7: Temporal Integrity Validation
- Decision: Keep temporal persistence logic in existing MCP services and assert `_Hist` + single-current-row behavior in MCP-tier tests after runtime migration.
- Rationale: Constitution Principle III.a and VI require temporal invariants independent of runtime transport framework.
- Alternatives considered: defer temporal assertions until later transport stabilization; rejected due to governance gate requirements.