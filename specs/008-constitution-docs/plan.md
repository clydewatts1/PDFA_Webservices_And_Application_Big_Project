# Implementation Plan: Constitution Documentation Compliance Bundle

**Branch**: `008-constitution-docs` | **Date**: 2026-03-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-constitution-docs/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Produce constitution-compliant project documentation by (1) auditing all constitution documentation obligations, (2) remediating contradictions and stale setup guidance, (3) formalizing a canonical constitution coverage matrix at `docs/constitution/coverage-matrix.md`, and (4) ensuring traceability links (README -> evidence/artifacts/source attribution) are complete and reviewer-friendly for Windows-first setup.

## Technical Context

**Language/Version**: Markdown + PowerShell command examples, Python 3.13 runtime references for reproducibility checks  
**Primary Dependencies**: Spec Kit workflow artifacts, repository README set, constitution, pytest command surface, MCP/Quart documented runtime commands  
**Storage**: Filesystem markdown artifacts in repository (`docs/`, root `README.md`, `specs/008-constitution-docs/`, `docs/constitution/`)  
**Testing**: Manual documentation verification checklist and command reproducibility spot checks in Windows PowerShell  
**Target Platform**: Windows developer/reviewer environment (with cross-platform notes where already documented)
**Project Type**: Three-tier web application documentation and governance compliance update  
**Performance Goals**: Reviewer can locate required documentation surfaces in <=5 minutes (SC-005)  
**Constraints**: No architecture boundary violations; no runtime feature invention; preserve constitutional terminology and transport semantics  
**Scale/Scope**: Update and align root README, supplementary READMEs, docs evidence files, and create canonical coverage matrix contract artifact

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Confirm the design preserves strict Database -> MCP Server -> Quart Web Server layering.
- Confirm Quart-to-MCP interactions use HTTP contracts only (JSON-RPC and/or SSE), with no
  direct database or in-process shortcut.
- Confirm SQLAlchemy usage is confined to the MCP server tier.
- Confirm the source `spec.md` was initiated via Spec Kit and is explicitly partitioned
  into MCP (Logic), Web-Tier (Routes), and Page (UI) sections before design proceeds.
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

**Gate Result (Pre-Research)**: PASS

- This feature is documentation-only and does not introduce cross-tier runtime shortcuts.
- Architecture, MCP-over-HTTP constraint, SQLAlchemy confinement, and temporal ownership are documented constraints, not modified behavior.
- Required Spec Kit initiation and partitioned spec sections are present in `spec.md`.

## Project Structure

### Documentation (this feature)

```text
specs/008-constitution-docs/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
├── artifacts/           # Validation logs, gap tracking, and review evidence
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
mcp_server/
├── src/
│   ├── api/
│   ├── models/
│   └── services/
└── tests/

quart_web/
├── src/
│   ├── routes/
│   ├── templates/
│   └── clients/
└── tests/

flask_web/
├── src/
│   ├── routes/
│   └── clients/
└── README.md

docs/
├── README.md
├── source_attribution.md
├── test_evidence.md
└── constitution/
    └── coverage-matrix.md   # New canonical matrix (FR-011)

specs/008-constitution-docs/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── artifacts/

README.md

database/
└── [schema, migrations, seed assets as applicable]
```

**Structure Decision**: Use existing three-tier repository with documentation-first updates across root and supplementary docs; add canonical coverage matrix under `docs/constitution/` and retain spec-local design artifacts under `specs/008-constitution-docs/`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Phase 0: Research Output

- Completed: `research.md`
- All prior clarification gaps are resolved, including canonical matrix location and schema.

## Phase 1: Design Output

- Completed: `data-model.md`
- Completed: `contracts/documentation-compliance-contract.md`
- Completed: `quickstart.md`
- Completed: agent context update via `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`

## Constitution Check (Post-Design)

**Gate Result (Post-Design)**: PASS

- Design artifacts preserve constitutional architecture boundaries and do not introduce runtime bypasses.
- Documentation contract enforces canonical coverage matrix schema and reviewer traceability requirements.
- Spec partitioning and Spec Kit governance requirements remain satisfied.

## Implementation Outcomes (2026-03-23)

- Created canonical matrix at `docs/constitution/coverage-matrix.md` with required schema columns.
- Added feature artifacts under `specs/008-constitution-docs/artifacts/` for audit index,
  contradiction remediation, gap handling, requirement registry, authority policy,
  language guardrails, and story validation summaries.
- Normalized runbook and transport guidance across root and tier READMEs.
- Added README traceability pointers to matrix, attribution, evidence, and feature artifacts.
- Captured feature-level validation evidence and prompt traceability updates.
