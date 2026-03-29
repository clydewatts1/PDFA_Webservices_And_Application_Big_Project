# Implementation Plan: Refactor Database Driver from PostgreSQL to MySQL

**Branch**: `009-postgres-to-mysql-refactor` | **Date**: 2026-03-23 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/009-postgres-to-mysql-refactor/spec.md`

## Summary

Replace the project's database driver from PostgreSQL (`psycopg`) to MySQL (`PyMySQL`) by
adding `PyMySQL>=1.1,<2.0` to `requirements.txt`, updating `session.py` to include MySQL
connection-pool reliability settings (`pool_recycle`, `pool_pre_ping`), and updating all
`DB_URL` documentation examples to use `mysql+pymysql://` with `?charset=utf8mb4`.
Schema migrations are not part of this feature. The automated test suite is unaffected:
all tests use SQLite in-process.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: SQLAlchemy 2.0+, Alembic 1.13+, PyMySQL 1.1+ (new), FastMCP 1.x  
**Storage**: MySQL 8.x (production/integration), SQLite (automated tests — unchanged)  
**Testing**: pytest, SQLite in-process via `DB_URL` fixture  
**Target Platform**: Linux/Windows server, developer workstation  
**Project Type**: Three-tier web service — MCP server tier only (infrastructure driver swap)  
**Performance Goals**: None for this feature (no performance acceptance criteria)  
**Constraints**: `pool_recycle=3600`, `pool_pre_ping=True` mandatory; `?charset=utf8mb4` mandatory in all `DB_URL` examples; no tier boundary changes; SSL/TLS out of scope  
**Scale/Scope**: Driver/configuration and documentation updates only; no schema migration changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ **Three-tier boundary**: Only the MCP server tier and its infrastructure dependencies are modified. The Quart web server is not touched. Database → MCP → Quart layering is preserved.
- ✅ **HTTP-only Quart-to-MCP**: No changes to Quart routes, clients, or forms. All existing HTTP contracts remain in place.
- ✅ **SQLAlchemy containment**: `PyMySQL` and `SQLAlchemy` remain exclusively in the MCP tier (`mcp_server/src/db/session.py` and `requirements.txt`). No Quart-side imports.
- ✅ **Spec Kit initiation**: `spec.md` was created via `/speckit.specify` with explicit MCP (Logic), Web-Tier (Routes), and Page (UI) sections, per Principle VII.
- ✅ **SCD / `_Hist` symmetry**: No schema structure changes. The 14 tables (7 current + 7 `_Hist`), temporal columns, and SCD orchestration in MCP services are all unchanged.
- ✅ **Reviewable increment**: The work is a single self-contained driver swap. The independently demonstrable increment is MCP startup + `get_system_health` returning healthy using MySQL `DB_URL`.
- ✅ **Workflow schema impact**: No schema changes to Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, or Instance tables.
- ✅ **Environment variables**: `DB_URL` format change documented. `docs/`, `specs/001/quickstart.md`, and `specs/009/quickstart.md` updated. External source attribution recorded in spec.

**Gate result**: PASS — no violations. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/009-postgres-to-mysql-refactor/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── no-interface-changes.md   # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code Changes (repository root)

```text
requirements.txt                                  # ADD: PyMySQL>=1.1,<2.0

mcp_server/
└── src/
    └── db/
        └── session.py                            # UPDATE: add pool_recycle=3600, pool_pre_ping=True

database/
└── migrations/                                   # NO CHANGE (out of scope for this feature)
```

### Documentation Updates (active docs only)

```text
docs/
├── mcp_milestone_test_guide.md                   # UPDATE: DB_URL example, pg section headers
└── test_evidence.md                              # UPDATE: DB_URL examples

specs/001-define-workflow-tables/
└── quickstart.md                                 # UPDATE: DB_URL connection string example

.github/agents/
└── copilot-instructions.md                       # UPDATE: storage entry for spec 001
```

**Structure Decision**: Three-tier web application layout (Option 2). This change touches only the MCP server tier infrastructure. No Quart web tier files are in scope.

## Complexity Tracking

> No Constitution Check violations — table intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|

## Post-Design Constitution Check

*Re-evaluated after Phase 1 artifacts completed.*

- ✅ **Three-tier boundary**: Only `requirements.txt` and `mcp_server/src/db/session.py` change at the code level. Quart web tier is zero-touch.
- ✅ **HTTP-only Quart-to-MCP**: No Quart routes, clients, or SSE contracts modified.
- ✅ **SQLAlchemy containment**: `PyMySQL` enters only via `requirements.txt`; used only by `mcp_server/`. Quart imports unchanged.
- ✅ **Spec-Kit + partitioned spec**: `spec.md` has explicit MCP (Logic), Web-Tier (Routes), and Page (UI) sections. All three present and complete.
- ✅ **SCD / `_Hist` integrity**: `data-model.md` confirms zero schema changes. All 14 tables, temporal columns, and SCD orchestration unchanged.
- ✅ **Reviewable increment**: MCP startup with MySQL `DB_URL` + `get_system_health` returning `"ok"` is the independently demonstrable outcome.
- ✅ **Workflow schema**: No impact. `data-model.md` explicitly states no table or column changes.
- ✅ **Env/docs/attribution**: `DB_URL` format documented in `contracts/no-interface-changes.md` and `quickstart.md`. Attribution in `spec.md`. 4 active docs identified for update in `research.md`. No new business-logic functions, so no additional docstrings required.

**Final gate result: PASS.**
