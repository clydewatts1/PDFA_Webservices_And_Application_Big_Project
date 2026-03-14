# Research: MCP Stdio Inspector Compatibility

## Decision 1: Dual Transport Requirement (stdio + HTTP/SSE)
- Decision: Require both stdio and HTTP/SSE transport support with equivalent tool behavior.
- Rationale: Clarified requirements demand Inspector compatibility through stdio while preserving HTTP/SSE contract path for broader integration parity.
- Alternatives considered: stdio-only (rejected: violates clarified transport scope), HTTP/SSE-only (rejected: fails Inspector-driven validation requirement).

## Decision 2: Canonical Inspector Launch Command
- Decision: Canonical stdio launch command is `python -m mcp_server.src.server`.
- Rationale: A dedicated MCP protocol entrypoint prevents ambiguity with Flask JSON-RPC runtime startup and aligns with Inspector expectations.
- Alternatives considered: reuse `python -m mcp_server.src.api.app` (rejected: transport/protocol mismatch risk), dual canonical commands (rejected: increases reviewer confusion).

## Decision 3: Tool Naming Convention
- Decision: Preserve dotted tool names (`workflow.create`, `role.list`, etc.) as canonical across both transports.
- Rationale: Existing handler contracts and prior milestone artifacts already use dotted naming, minimizing migration risk and preserving continuity.
- Alternatives considered: underscore names only (rejected: larger migration surface), dual naming aliases (rejected: unnecessary ambiguity for this increment).

## Decision 4: Mock Authentication Boundary
- Decision: Keep YAML-defined plain-text mock credentials for this milestone with explicit non-production-only disclaimer.
- Rationale: Satisfies current testability goals without introducing production auth redesign outside scope.
- Alternatives considered: hashed credentials now (rejected: additional complexity without milestone value), DB-backed auth (rejected: out-of-scope redesign).

## Decision 5: Transport Parity Verification Strategy
- Decision: Define transport parity gate requiring identical required tool set and status semantics for stdio and HTTP/SSE.
- Rationale: Prevents drift between protocol paths and ensures reviewer outcomes are deterministic regardless of transport.
- Alternatives considered: subset parity (rejected: weakens acceptance confidence), no explicit parity gate (rejected: allowed prior mismatch risk).

## Decision 6: Validation Evidence Standard
- Decision: Use runbook-driven evidence capture combining Inspector call results and direct SQLite verification as primary, with optional PostgreSQL equivalents.
- Rationale: Meets explicit manual database verification requirements and supports reproducible reviewer workflows.
- Alternatives considered: response-only evidence (rejected: insufficient persistence validation), PostgreSQL-only verification (rejected: higher setup friction).
