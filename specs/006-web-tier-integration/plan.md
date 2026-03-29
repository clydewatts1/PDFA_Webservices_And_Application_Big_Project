# Implementation Plan: Simplified Web Tier Integration (Refinement Pass)

**Branch**: `006-web-tier-integration` | **Date**: 2026-03-16 | **Spec**: [specs/006-web-tier-integration/spec.md](spec.md)
**Input**: Feature specification from `/specs/006-web-tier-integration/spec.md`

## Summary

Deliver a Quart-based web tier over the existing MCP server using official MCP Python SDK SSE transport, with four increments: (1) landing + auth, (2) workflow selection, (3) entity navigation, (4) full CRUD pages. This refinement pass resolves prior inconsistencies by standardizing on: canonical MCP tool names (`workflow.*`, `role.*`, `interaction.*`, `guard.*`, `interaction_component.*`), canonical session key (`active_workflow_name`), and canonical SDK/session model (`mcp.client.sse.sse_client` + `mcp.ClientSession`).

## Technical Context

**Language/Version**: Python 3.13 (`.venv/Scripts/python.exe`)  
**Primary Dependencies**: Quart, `mcp` Python SDK, Jinja2, Bootstrap 5, quart-wtf  
**Storage**: N/A in web tier (all persistence delegated to MCP server)  
**Testing**: pytest + pytest-asyncio + AsyncMock (route isolation)  
**Target Platform**: Linux-hosted web service tier  
**Project Type**: Three-tier web application (presentation tier)  
**Performance Goals**: Landing response target <2s; login round-trip <5s  
**Constraints**: No SQLAlchemy in Quart; no SPA/AJAX state management; full-page GET/POST navigation; 10s MCP call timeout  
**Scale/Scope**: 5 entity domains via MCP tools (Workflow, Role, Interaction, Guard, InteractionComponent)

## Constitution Check

*GATE: Must pass before and after design artifacts.*

- Tier boundaries preserved: Database -> MCP Server -> Quart Web Server.
- Quart-to-MCP communication remains HTTP/SSE contract-only.
- SQLAlchemy remains confined to MCP tier.
- Temporal/SCD integrity remains MCP-owned; Quart forms expose business fields only.
- Incremental delivery remains in reviewable chunks with independent checkpoints.
- Documentation and env-var planning included (`MCP_SERVER_URL`, `SESSION_SECRET`, source attribution, README updates).

**Gate Result**: PASS for this refinement scope.

## Project Structure

### Documentation (feature folder)

```text
specs/006-web-tier-integration/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── workflow-tools.md
│   ├── dependent-entity-tools.md
│   ├── http-session-schema.md
│   └── mcp-session-lifecycle.md
└── tasks.md
```

### Source Code (planned)

```text
mcp_server/
└── src/ ... (existing persistence + tool runtime)

quart_web/
└── src/
    ├── app.py
    ├── clients/
    │   └── mcp_client.py
    ├── routes/
    │   ├── health.py
    │   ├── auth.py
    │   ├── workspace.py
    │   ├── workflow.py
    │   ├── role.py
    │   ├── interaction.py
    │   ├── guard.py
    │   └── interaction_component.py
    ├── forms/
    └── templates/
```

**Structure Decision**: Option 2 (three-tier application) with Quart as isolated presentation tier.

## Refinement Outcomes (I1-I4)

1. **I1 Scope mismatch fixed**: Plan now explicitly includes full CRUD in Phase 4 (not read-only).
2. **I2 SDK naming fixed**: Plan/spec align to `mcp.client.sse.sse_client` + `mcp.ClientSession`.
3. **I3 Session key fixed**: Plan/spec/tasks use `active_workflow_name` consistently.
4. **I4 Tool naming fixed**: Plan/spec/tasks/contracts align to canonical tool names (`role.list`, `role.get`, etc.).

## Phase 0: Research (Complete)

`research.md` completed and retained. It documents:

- Quart app-factory architecture
- Official MCP SDK SSE integration pattern
- Session schema and CSRF behavior
- Business-field-only form strategy
- Boundary-aware testing strategy

No unresolved `NEEDS CLARIFICATION` items remain.

## Phase 1: Design & Contracts (Complete)

### `data-model.md`

Completed with:

- HTTP session schema and state transitions
- MCP session lifecycle and timeout/error states
- Entity field visibility tables
- Phase view models and route map

### `contracts/`

Completed with:

- `workflow-tools.md`
- `dependent-entity-tools.md`
- `http-session-schema.md`
- `mcp-session-lifecycle.md`

### `quickstart.md`

Completed with:

- Setup/run/test commands
- env var contract
- smoke-test checklist

### Agent Context Update

`update-agent-context.ps1 -AgentType copilot` already run; Copilot context updated.

## Post-Design Constitution Re-check

- Tier isolation preserved in all artifacts.
- Tool contracts remain MCP-owned and transport-bound.
- No direct Quart persistence behavior introduced.
- Documentation artifacts and testing strategy remain constitution-aligned.

**Post-design gate**: PASS.

## Complexity Tracking

No constitutional violations introduced by this refinement pass.
