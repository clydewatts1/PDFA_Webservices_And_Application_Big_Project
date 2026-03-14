# Research: MCP Server Configuration and Test Guide

## Decision 1: Canonical MCP Configuration Filename
- Decision: Use `WB-Workflow-Configuration.yaml` as the canonical MCP configuration file.
- Rationale: Preserves required base name while using a valid YAML convention that tools and reviewers can locate consistently.
- Alternatives considered: Extensionless filename (rejected due weaker editor/tool interoperability), dual `.yaml/.yml` support (rejected to avoid ambiguity in reviewer instructions).

## Decision 2: Mock Authentication Validation Strategy
- Decision: Implement `user_logon` against a small in-memory credential map defined in MCP YAML config.
- Rationale: Matches the milestone’s mock-security intent while enabling deterministic `SUCCESS`/`DENIED`/`ERROR` validation paths.
- Alternatives considered: Always-success stub (rejected: insufficient negative-case testing), DB-backed auth (rejected: over-scope and security complexity).

## Decision 3: Table CRUD Scope
- Decision: Mandatory CRUD tooling applies to Workflow, Role, Interaction, Guard, and InteractionComponent current tables.
- Rationale: User clarification explicitly fixed this scope and it aligns with the project’s graph-entity progression.
- Alternatives considered: Include UnitOfWork/Instance in this milestone (rejected by scope clarification), configurable table lists at runtime (rejected as unnecessary complexity for this increment).

## Decision 4: Mandatory `npx` Verification Path
- Decision: Require `npx @modelcontextprotocol/inspector` in the testing document for interactive tool verification.
- Rationale: Provides a consistent reviewer path for invoking MCP tools and observing request/response behavior.
- Alternatives considered: Generic `npx` examples only (rejected due non-deterministic reviewer outcomes).

## Decision 5: Manual Data Verification Procedure
- Decision: Provide primary SQLite CLI (`sqlite3`) direct-query verification steps, with optional PostgreSQL `psql` equivalent commands.
- Rationale: Supports the clarified requirement for manual table-level verification while preserving cross-environment portability.
- Alternatives considered: PostgreSQL-only manual checks (rejected for higher local setup friction), no manual SQL verification (rejected by explicit requirement).
