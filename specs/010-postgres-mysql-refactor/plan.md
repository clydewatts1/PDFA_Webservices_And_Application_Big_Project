# Implementation Plan: Continue PostgreSQL to MySQL Refactor

**Branch**: `010-postgres-mysql-refactor` | **Date**: 2026-04-03 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-postgres-mysql-refactor/spec.md`

## Summary

Complete the MySQL migration continuation by making MySQL the only validation target for
contract/integration test flows, proactively updating Alembic migration scripts for MySQL
compatibility, preserving current plus `_Hist` temporal semantics, and formalizing an
operational cutover model with no historical backfill and a 24-hour rollback window to
PostgreSQL. The implementation stays inside the MCP/database boundary and updates runtime
and documentation guidance accordingly.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: SQLAlchemy 2.x, Alembic 1.13+, FastMCP 1.x, PyMySQL 1.1+  
**Storage**: MySQL 8.x (runtime + contract/integration validation), PostgreSQL (legacy pre-cutover retention only), SQLite (unit-only where already applicable)  
**Testing**: pytest (`tests/contract`, `tests/integration`, selected MCP smoke checks), MySQL-backed validation environment  
**Target Platform**: Windows and Linux developer/CI environments running MCP and Quart tiers over HTTP
**Project Type**: Three-tier web application with MCP service boundary and database-backed workflow model  
**Performance Goals**: Preserve current MCP health and workflow operation responsiveness; no new throughput target introduced by this feature  
**Constraints**: Maintain strict tier boundaries; no Quart direct DB access; no historical PostgreSQL backfill; 24-hour rollback window with explicit gate criteria; migration baseline-to-head must execute on MySQL  
**Scale/Scope**: Incremental migration-completion slice spanning migration scripts, validation pipeline targeting, and cutover/rollback documentation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Design preserves strict Database -> MCP Server -> Quart Web Server layering.
- ✅ Quart-to-MCP interactions remain HTTP contracts only (JSON-RPC and SSE); no direct DB or in-process shortcut.
- ✅ SQLAlchemy usage remains confined to MCP server tier.
- ✅ Source `spec.md` is Spec-Kit initiated and partitioned into MCP (Logic), Web-Tier (Routes), and Page (UI).
- ✅ Persistence design preserves symmetric current and `_Hist` schema, required temporal/audit columns, one current row per business key, and MCP-owned history orchestration.
- ✅ Work is a reviewable migration-completion increment with demonstrable outcome: MySQL-only validation and successful MySQL migration execution.
- ✅ Workflow-schema impact on Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, and Instance is documented as structurally unchanged.
- ✅ Environment variables, source attribution, README impacts, and documentation updates are planned.

**Gate result**: PASS.

## Project Structure

### Documentation (this feature)

```text
specs/010-postgres-mysql-refactor/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── migration-and-cutover-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
mcp_server/
├── src/
│   ├── db/
│   ├── services/
│   └── api/
└── tests/

quart_web/
├── src/
│   ├── routes/
│   └── clients/
└── tests/

database/
└── migrations/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Three-tier web-application structure is retained. Planned implementation touches migration artifacts and MCP-owned persistence/runtime validation setup; Quart and page layers remain behaviorally stable and contract-consumer only.

## Complexity Tracking

No Constitution Check violations identified.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|

## Post-Design Constitution Check

*Re-evaluated after Phase 1 design artifacts (research, data-model, contracts, quickstart).* 

- ✅ Layering preserved: no design action requires bypassing MCP boundary.
- ✅ HTTP-only Quart-to-MCP contract remains unchanged.
- ✅ SQLAlchemy and migration mechanics remain MCP/database scoped.
- ✅ Spec partitioning remains complete and aligned with Principle VII.
- ✅ SCD/current+`_Hist` integrity preserved with no structural table changes.
- ✅ Increment remains independently demonstrable: baseline-to-head MySQL migration plus MySQL contract/integration validation and rollback-window runbook.
- ✅ Workflow seven-table integrity and temporal semantics documented as unchanged.
- ✅ Environment/config, attribution, and documentation updates captured in quickstart/contracts outputs.

**Final gate result**: PASS.

## Implementation Consistency Notes

- Runtime and contract/integration guidance now assume a MySQL-first `DB_URL` and a shared MySQL test fixture path.
- PostgreSQL references are limited to rollback-window governance, feature lineage, and explicitly historical documentation.
- Live evidence capture tasks remain dependent on access to a reachable MySQL validation target.
