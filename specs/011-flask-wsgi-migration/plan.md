# Implementation Plan: Full Stack WSGI Migration

**Branch**: `011-flask-wsgi-migration` | **Date**: 2026-04-07 | **Spec**: `specs/011-flask-wsgi-migration/spec.md`
**Input**: Feature specification from `/specs/011-flask-wsgi-migration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Replace the unsupported Quart/ASGI production path with a fully synchronous Flask-based stack for PythonAnywhere. The implementation uses two separate WSGI applications: a new `mcp_server/src/wsgi_app.py` JSON-RPC wrapper that reuses the existing MCP handler/service layer, and an expanded `flask_web` presentation tier that ports the current production Quart routes, forms, templates, and tests while communicating only through synchronous HTTP POST JSON-RPC.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.13.12  
**Primary Dependencies**: Flask 3.x, Flask-WTF, WTForms, requests, SQLAlchemy 2.x, Alembic 1.13+, python-dotenv, PyYAML, pytest, existing `mcp` package for non-canonical MCP metadata/runtime code  
**Storage**: MySQL 8.x via SQLAlchemy in the MCP tier; no new persistence schema for this feature  
**Testing**: pytest with Flask test clients, MCP wrapper contract tests, web-tier integration parity tests, existing MCP server unit/contract/integration suites  
**Target Platform**: Windows local development plus PythonAnywhere WSGI deployment with two separate Flask applications  
**Project Type**: Three-tier web application  
**Performance Goals**: Interactive health, login, dashboard, and entity CRUD flows complete as standard request/response cycles with no persistent connections or streaming semantics  
**Constraints**: Synchronous HTTP POST JSON-RPC only; no SSE/WebSockets/uvicorn/Starlette in the supported path; separate WSGI apps for web tier and MCP wrapper; no SQLAlchemy in `flask_web`; preserve current/`_Hist` MCP-owned behavior  
**Scale/Scope**: Migrate the production Quart route/template/form surface (health, auth, workspace, workflow, role, interaction, guard, interaction component), add one new MCP wrapper entrypoint, update active docs/tests/configuration, and retire supported ASGI/SSE runtime guidance

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Design preserves strict Database -> MCP Server -> Flask Web Server layering by deploying two separate WSGI apps over HTTP.
- PASS: Flask-to-MCP interactions use synchronous HTTP POST JSON-RPC only; the supported path excludes SSE, WebSockets, and in-process web-tier shortcuts into MCP persistence logic.
- PASS: SQLAlchemy remains confined to the MCP server tier, with wrapper dispatch reusing existing MCP handlers/services.
- PASS: `spec.md` was initiated via Spec Kit and is partitioned into MCP (Logic), Web-Tier (Routes), and Page (UI).
- PASS: No schema change is introduced; current/`_Hist` symmetry and MCP-owned temporal orchestration remain preserved by reuse of the existing service layer.
- PASS: The work is sliceable into reviewable increments: wrapper/runtime replacement first, Flask parity second, documentation/test retirement third.
- PASS: Workflow-schema impact is documented as unchanged for Workflow, Role, Interaction, Guard, InteractionComponent, UnitOfWork, and Instance.
- PASS: Environment variables, test strategy, runbook updates, attribution, and README alignment are explicitly planned in this feature.

**Post-Design Recheck**: PASS. Research, contracts, quickstart, and data model all maintain the same layering, transport, and test-isolation commitments.

## Project Structure

### Documentation (this feature)

```text
specs/011-flask-wsgi-migration/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
mcp_server/
├── src/
│   ├── api/
│   ├── wsgi_app.py
│   ├── lib/
│   ├── models/
│   └── services/
└── tests/
  ├── contract/
  ├── integration/
  └── unit/

flask_web/
├── src/
│   ├── forms/
│   ├── routes/
│   ├── templates/
│   └── clients/
└── tests/
  ├── integration/
  └── unit/

quart_web/
├── src/
└── tests/

database/
└── migrations/

docs/
└── [runbooks, evidence, source attribution]
```

**Structure Decision**: Use the existing three-tier repository layout. Add a dedicated Flask MCP wrapper entrypoint under `mcp_server/src/wsgi_app.py`, expand `flask_web` to absorb the current production `quart_web` route/form/template surface, keep `quart_web` only as a legacy transition artifact during implementation, and update docs/runbooks to make the Flask WSGI path authoritative.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
