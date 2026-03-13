# Research: Workflow Interaction Schema Foundation

## Decision 1: Instantiation Replication Strategy
- Decision: Use fixed current/history tables and replicate instance baseline as instance-scoped rows.
- Rationale: Keeps schema stable, avoids runtime DDL complexity, and is easier to validate with SQLAlchemy and migrations.
- Alternatives considered: Dynamic per-instance physical tables; rejected due to migration/testing/operational complexity.

## Decision 2: Key Strategy
- Decision: Use workflow-scoped natural/composite keys for dependent entities; keep `InstanceName` globally unique.
- Rationale: Matches business semantics and aligns with user-provided naming model while preserving relational integrity.
- Alternatives considered: Surrogate IDs for all entities; deferred for later if operational needs require it.

## Decision 3: MCP Communication Contract
- Decision: Require JSON-RPC for all mandatory operations in this increment; defer SSE.
- Rationale: JSON-RPC gives deterministic request/response behavior and simplifies contract and integration testing for MVP.
- Alternatives considered: JSON-RPC + SSE both mandatory; rejected as unnecessary scope expansion for first increment.

## Decision 4: Current/History Lifecycle Rule
- Decision: Enforce exactly one active current row per business key; close prior active row (`EffToDateTime`) before activating replacement row.
- Rationale: Removes ambiguity in reads, makes history deterministic, and supports strict temporal assertions in tests.
- Alternatives considered: Multiple active rows with latest-timestamp resolution; rejected due to conflict risk and weaker invariants.

## Decision 5: Object-Creation Library Design
- Decision: Implement an MCP-local object factory library with typed builders, defaulting, and temporal validations.
- Rationale: Centralizes construction/validation logic and prevents duplication across tool handlers.
- Alternatives considered: Validation distributed across route handlers and services; rejected for maintainability concerns.

## Decision 6: Temporary Delivery Scope
- Decision: Build a temporary three-tier app that demonstrates workflow maintenance first, then dependent entities, then instantiation.
- Rationale: Aligns to constitution chunking requirement and creates demonstrable milestones.
- Alternatives considered: Full-stack feature parity in a single phase; rejected due to reduced reviewability.

## Decision 7: Test Pyramid for This Increment
- Decision: Use unit tests for object factory behavior, contract tests for JSON-RPC shape/errors, and integration tests for Flask -> MCP -> DB paths.
- Rationale: Balances fast feedback with end-to-end confidence and directly verifies architectural boundaries.
- Alternatives considered: Integration-only validation; rejected because root-cause diagnosis and edge-case coverage are weaker.
