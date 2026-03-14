# Implementation Plan: MCP Server Configuration and Test Guide

**Branch**: `003-mcp-server-setup-tests` | **Date**: 2026-03-14 | **Spec**: `specs/003-mcp-server-setup-tests/spec.md`
**Input**: Feature specification from `/specs/003-mcp-server-setup-tests/spec.md`

## Summary

Implement MCP milestone coverage by defining a canonical YAML configuration (`WB-Workflow-Configuration.yaml`), adding/aligning MCP tools for health/auth/table CRUD behavior, and delivering a reviewer-grade testing runbook that includes mandatory `npx @modelcontextprotocol/inspector` usage plus direct SQLite table-query verification (with optional `psql` equivalents).

## Technical Context

**Language/Version**: Python 3.13.x, Markdown documentation  
**Primary Dependencies**: Flask, SQLAlchemy, Alembic, pytest, Model Context Protocol tooling (`@modelcontextprotocol/inspector`)  
**Storage**: SQLite (primary local verification path) with optional PostgreSQL equivalent verification  
**Testing**: pytest, MCP inspector-driven manual validation, direct SQL table verification checklists  
**Target Platform**: Windows local development environment (cross-platform repository support)  
**Project Type**: Three-tier web-service architecture with MCP service contracts and review documentation  
**Performance Goals**: Operational readiness over throughput; health/status responses and CRUD behavior verifiable in a single reviewer session (<15 minutes setup)  
**Constraints**: Preserve strict Database -> MCP -> Flask boundaries; no Flask direct DB access; SQLAlchemy MCP-only; YAML-driven MCP configuration naming fixed to `WB-Workflow-Configuration.yaml`; manual verification must prioritize `sqlite3`; required inspector path uses `npx @modelcontextprotocol/inspector`  
**Scale/Scope**: In-scope table tools limited to Workflow, Role, Interaction, Guard, InteractionComponent plus core health and mock auth tools and one dedicated test runbook

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Plan preserves strict Database -> MCP Server -> Flask Web Server layering and keeps feature work in MCP + docs.
- PASS: No direct Flask-to-database shortcuts are introduced; cross-tier interactions remain HTTP MCP contracts.
- PASS: SQLAlchemy usage remains confined to MCP server tier.
- PASS: Work is chunked as one reviewable increment (config + tools + runbook) with independently demonstrable outputs.
- PASS: Workflow-schema impact is bounded to tool contracts for existing entities; no schema expansion required for this increment.
- PASS: Environment/config docs, README traceability expectations, and external-source/AI prompt recording are explicitly included.

## Phase 0 Output (Research)

- `research.md` records final decisions for YAML naming, mock auth strategy, in-scope table list, inspector workflow, and manual DB verification path.

## Phase 1 Outputs (Design & Contracts)

- `data-model.md` defines config + tool result + runbook verification entities.
- `contracts/mcp-milestone-tooling.md` defines reviewable MCP tool contracts and expected response envelopes.
- `quickstart.md` provides setup and verification steps for MCP config, database wiring, inspector usage, and direct SQL checks.

## Post-Design Constitution Check

- PASS: Design artifacts keep DB/MCP/Flask boundaries unchanged.
- PASS: MCP-over-HTTP behavior is preserved and documented via contracts.
- PASS: SQLAlchemy containment remains MCP-only; manual verification docs do not alter runtime access boundaries.
- PASS: Documentation and traceability expectations are embedded in runbook + contract outputs.

## Project Structure

### Documentation (this feature)

```text
specs/003-mcp-server-setup-tests/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-milestone-tooling.md
└── tasks.md
```

### Source Code (repository root)

```text
mcp_server/
├── src/
│   ├── api/
│   ├── tools/
│   ├── models/
│   └── services/
└── tests/

flask_web/
├── src/
│   ├── routes/
│   ├── templates/
│   └── clients/
└── tests/

database/
└── migrations/

docs/
└── prompts/
```

**Structure Decision**: Retain the existing three-tier layout; introduce this feature’s planning and review artifacts under `specs/003-mcp-server-setup-tests` and implement runtime/documentation updates in existing MCP/docs paths.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
