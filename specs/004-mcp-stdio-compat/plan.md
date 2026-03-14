# Implementation Plan: MCP Stdio Inspector Compatibility

**Branch**: `004-mcp-stdio-compat` | **Date**: 2026-03-14 | **Spec**: `specs/004-mcp-stdio-compat/spec.md`
**Input**: Feature specification from `/specs/004-mcp-stdio-compat/spec.md`

## Summary

Implement a standards-compliant MCP server milestone that adds a dedicated stdio entrypoint (`python -m mcp_server.src.server`) and required HTTP/SSE transport parity so `npx @modelcontextprotocol/inspector` can connect and discover/execute health, auth, and dotted-name CRUD tools consistently. Preserve canonical YAML config (`WB-Workflow-Configuration.yaml`), `.env` database sourcing, and mock-auth non-production constraints while delivering a reviewer-grade runbook with direct SQL verification.

## Technical Context

**Language/Version**: Python 3.13.x, Markdown documentation  
**Primary Dependencies**: Flask, SQLAlchemy, Alembic, pytest, python-dotenv, PyYAML, MCP Python SDK, Model Context Protocol Inspector (`@modelcontextprotocol/inspector`)  
**Storage**: SQLite (primary local verification) with PostgreSQL-capable equivalents  
**Testing**: pytest regression suite, Inspector-driven manual MCP validation, direct SQL verification checklists  
**Target Platform**: Windows local development (cross-platform repo usage)  
**Project Type**: Three-tier web-service architecture with MCP service contracts and runbook-driven validation  
**Performance Goals**: Reviewer-ready operational correctness; end-to-end setup + verification in under 15 minutes for first-time reviewer  
**Constraints**: Must support both stdio and HTTP/SSE transports with parity; preserve Database -> MCP -> Flask boundaries; SQLAlchemy MCP-only; canonical tool naming stays dotted style; mock auth explicitly non-production only  
**Scale/Scope**: Health/auth + CRUD tools for Workflow/Role/Interaction/Guard/InteractionComponent across dual MCP transports with deterministic result semantics

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Design preserves strict Database -> MCP Server -> Flask Web Server layering.
- PASS: Flask-to-MCP interactions remain HTTP contract-based; stdio transport is for Inspector/reviewer tooling, not Flask bypass.
- PASS: SQLAlchemy usage remains confined to the MCP server tier.
- PASS: Scope is a reviewable increment: transport compliance + contract parity + runbook validation.
- PASS: Workflow-schema impact is bounded to existing entities/tools; no schema redesign required.
- PASS: Environment variables, traceability updates, README/runbook expectations, and documentation standards are explicitly included.

## Phase 0 Output (Research)

- `research.md` resolves transport strategy, parity rules, mock-auth boundary, command conventions, and validation evidence model.

## Phase 1 Outputs (Design & Contracts)

- `data-model.md` defines runtime profile, session evidence, and tool-result entities.
- `contracts/mcp-transport-compatibility.md` defines stdio + HTTP/SSE contract parity and required tool behavior.
- `quickstart.md` documents canonical startup, Inspector configuration, transport verification sequence, and SQL validation flow.

## Post-Design Constitution Check

- PASS: Phase 1 artifacts preserve three-tier separation and SQLAlchemy containment.
- PASS: Transport expansion does not introduce Flask-to-database or in-process shortcut behavior.
- PASS: Contract parity requirements are explicit across stdio and HTTP/SSE.
- PASS: Documentation and attribution expectations remain embedded as delivery gates.

## Project Structure

### Documentation (this feature)

```text
specs/004-mcp-stdio-compat/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-transport-compatibility.md
└── tasks.md
```

### Source Code (repository root)

```text
mcp_server/
├── src/
│   ├── api/
│   ├── lib/
│   ├── models/
│   ├── services/
│   └── server.py            # planned dedicated stdio MCP entrypoint
└── tests/

flask_web/
├── src/
│   ├── routes/
│   ├── templates/
│   └── clients/
└── tests/

docs/
├── mcp_milestone_test_guide.md
└── [traceability docs]
```

**Structure Decision**: Continue using the existing three-tier layout, adding a dedicated MCP stdio entrypoint within `mcp_server/src` and updating contracts/runbook under the feature spec directory plus existing docs paths.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
