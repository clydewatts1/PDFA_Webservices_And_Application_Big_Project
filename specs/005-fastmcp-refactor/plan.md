# Implementation Plan: MCP Server FastMCP Refactor

**Branch**: `[005-fastmcp-refactor]` | **Date**: 2026-03-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-fastmcp-refactor/spec.md`

## Summary

Replace MCP-tier custom Flask/JSON-RPC/SSE runtime handling with an official FastMCP runtime that supports `stdio`, `sse`, and `streamable-http` while preserving in-scope tool names and temporal business behavior. Feature scope is MCP-tier only, keeps Flask unchanged, deprecates YAML as MCP tool-metadata source, and applies a testing strategy of full `stdio` behavior coverage plus `sse`/`streamable-http` smoke coverage.

## Technical Context

**Language/Version**: Python 3.13.x  
**Primary Dependencies**: `mcp` Python SDK (`FastMCP`), SQLAlchemy, Alembic, pytest, python-dotenv, PyYAML (non-tool config), Flask (web tier only)  
**Storage**: SQLite/PostgreSQL through SQLAlchemy in MCP tier  
**Testing**: pytest with FastMCP-aware/asyncio runtime harnesses; MCP-tier temporal persistence assertions  
**Target Platform**: Windows/Linux local dev and reviewer environments  
**Project Type**: Three-tier web service with MCP server runtime refactor (MCP tier only)  
**Performance Goals**: Maintain current functional behavior with no added protocol-layer regressions; no new throughput target in this increment  
**Constraints**: Preserve strict three-tier boundaries, preserve temporal `_Hist` invariants, remove MCP-tier Flask routing code, require all 3 transports (`stdio`, `sse`, `streamable-http`)  
**Scale/Scope**: In-scope tools only (`get_system_health`, `user_logon`, `user_logoff`, `workflow.*`, `role.*`, `interaction.*`, `guard.*`, `interaction_component.*`); defer `unit_of_work.*`, `instance.*`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Confirm the design preserves strict Database -> MCP Server -> Flask Web Server layering.
- Confirm Flask-to-MCP interactions use HTTP contracts only (JSON-RPC and/or SSE), with no
  direct database or in-process shortcut.
- Confirm SQLAlchemy usage is confined to the MCP server tier.
- Confirm persistence changes preserve symmetric current and `_Hist` schemas, required
  temporal/audit columns, a single current row per business key in the primary table, and
  MCP-owned current-state plus history orchestration.
- Confirm the work is sliced into a reviewable chunk and identifies the first independently
  demonstrable increment.
- Confirm workflow-schema impact on Workflow, Role, Interaction, Guard,
  InteractionComponent, UnitOfWork, and Instance is documented when relevant.
- Confirm environment variables, external-source citations, README updates, directory-level
  README updates where applicable, and docstring/comment expectations are planned when the
  change affects them.

Constitution gate assessment (pre-Phase 0): PASS
- Layering preserved: MCP-tier framework refactor only.
- Flask-to-MCP HTTP-only boundary preserved; no in-process Flask shortcuts introduced.
- SQLAlchemy remains in MCP service layer.
- Temporal current+`_Hist` orchestration remains MCP-owned and test-mandated.
- Increment is reviewable and independently demonstrable via three FastMCP transports.
- Workflow schema impact is runtime/protocol only; entity model ownership unchanged.
- Documentation/test/source-attribution updates are included in scope.

## Project Structure

### Documentation (this feature)

```text
specs/005-fastmcp-refactor/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
mcp_server/
├── src/
│   ├── api/
│   ├── lib/
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
```

Structure Decision: Use the existing three-tier repository layout. Implementation changes are concentrated in `mcp_server/src/server.py`, `mcp_server/src/api/app.py` (deprecation/removal path), `mcp_server/src/lib/tool_adapter.py`, and MCP-tier tests in `mcp_server/tests/`. Flask and database directory structure remain unchanged for this increment.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

Post-Design Constitution Re-Check: PASS
- Design artifacts preserve MCP-only change scope and do not push persistence/UI behavior across tiers.
- Transport requirements include all constitution-mandated FastMCP modes (`stdio`, `sse`, `streamable-http`).
- Temporal test obligations remain explicit in design and quickstart/test guidance.
