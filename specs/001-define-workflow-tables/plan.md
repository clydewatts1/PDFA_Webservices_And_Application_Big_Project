# Implementation Plan: Workflow Interaction Schema Foundation (Temporary Application)

**Branch**: `001-define-workflow-tables` | **Date**: 2026-03-13 | **Spec**: `specs/001-define-workflow-tables/spec.md`
**Input**: Feature specification from `specs/001-define-workflow-tables/spec.md`

## Summary

Implement a temporary three-tier application that demonstrates end-to-end object creation and
history tracking for Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork,
and Instance. The MCP tier owns a reusable object factory library plus SQLAlchemy persistence;
the Flask tier consumes MCP tools over HTTP JSON-RPC only for this increment.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Flask, SQLAlchemy, Alembic, python-dotenv, pydantic/dataclasses, requests/httpx  
**Storage**: PostgreSQL (primary), SQLite (local temporary tests only)  
**Testing**: pytest, pytest-cov, unit tests, JSON-RPC contract tests, Flask->MCP->DB integration tests  
**Target Platform**: Windows/Linux developer machines  
**Project Type**: Three-tier web service with temporary web interface  
**Performance Goals**: p95 object-creation latency < 300ms in local environment  
**Constraints**: Strict three-tier boundaries, SQLAlchemy only in MCP, JSON-RPC required (SSE deferred), one active current row per business key, phase-scoped environment variables (database-only for current schema phase)  
**Scale/Scope**: Instructional MVP for schema, object creation, and deterministic current/history behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Preserves strict Database -> MCP Server -> Flask Web Server layering.
- PASS: Enforces Flask-to-MCP HTTP interaction via JSON-RPC contracts.
- PASS: Constrains SQLAlchemy usage to MCP tier.
- PASS: Delivers in granular chunks beginning with workflow maintenance.
- PASS: Uses canonical seven-table schema (Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, Instance).
- PASS: Plans phase-scoped environment-variable config, source attribution, and docs/README updates.

## Phase 0 Output (Research)

- `research.md` produced with resolved decisions on:
  - fixed-table instantiation replication,
  - workflow-scoped composite key strategy,
  - JSON-RPC required / SSE deferred,
  - one-active-current-row temporal lifecycle,
  - object-factory-first architecture.

## Phase 1 Outputs (Design & Contracts)

- `data-model.md` defines entities, keys, relations, control columns, and validation invariants.
- `contracts/mcp-jsonrpc.md` defines MCP JSON-RPC request/response/error envelopes and methods.
- `quickstart.md` defines local setup, env vars, migration steps, run order, and smoke tests.
- `tasks.md` exists and should be regenerated/verified after any further clarify decisions.

## Post-Design Constitution Check

- PASS: `data-model.md` specifies relational integrity and lifecycle rules for all seven tables.
- PASS: `contracts/mcp-jsonrpc.md` keeps external integration on MCP-over-HTTP.
- PASS: JSON-RPC-only requirement for this increment is explicit; SSE is deferred.
- PASS: Design artifacts preserve MCP data access encapsulation and SQLAlchemy containment.
- PASS: Quickstart includes phase-scoped `.env` configuration (database now; service URLs later).

## Project Structure

### Documentation (this feature)

```text
specs/001-define-workflow-tables/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-jsonrpc.md
└── tasks.md
```

### Source Code (repository root)

```text
mcp_server/
├── src/
│   ├── api/
│   ├── tools/
│   ├── models/
│   ├── services/
│   └── lib/
└── tests/

flask_web/
├── src/
│   ├── routes/
│   ├── templates/
│   └── clients/
└── tests/

database/
└── migrations/
```

**Structure Decision**: Adopt the three-tier web application structure to preserve constitutional boundaries and support testable object-creation workflows.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
