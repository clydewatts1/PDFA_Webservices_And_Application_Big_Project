# External Source Attribution

This project records external assistance and references used during design and implementation.

## AI-Assisted Development

### GitHub Copilot (GPT-5.3-Codex)
- Used for iterative implementation across all phases.
- Prompt-level traceability is maintained in `docs/prompts/prompt_log.md` (PRM-001 onward).
- Output included code generation, refactoring support, and test authoring under user direction.

### Google Gemini
- Used as brainstorming and high-level architecture support during early planning.
- Mentioned in `README.md` under development tooling context.

## Specification Tooling

### Spec Kit
- Used to drive constitution/specification/planning/tasks flow.
- Repository reference: https://github.com/github/spec-kit
- Project-local Spec Kit artifacts and workflow prompts are present under `.specify/` and `.github/prompts/speckit.*`.

## Source of Requirements

- Primary requirements source: `specs/001-define-workflow-tables/spec.md`
- Technical design source: `specs/001-define-workflow-tables/plan.md`
- Execution ledger: `specs/001-define-workflow-tables/tasks.md`
- Milestone 2 specification source: `specs/002-milestone2-section-v/spec.md`
- Milestone 2 implementation plan source: `specs/002-milestone2-section-v/plan.md`
- Milestone 2 execution ledger: `specs/002-milestone2-section-v/tasks.md`
- Milestone 2 compliance contract: `specs/002-milestone2-section-v/contracts/section-v-compliance-review.md`

## Traceability Notes

- Every implementation phase is logged in `docs/prompts/prompt_log.md` with:
  - prompt summary,
  - affected files,
  - validation outcomes,
  - major decisions.
- This document plus `prompt_log.md` together satisfy external-source attribution requirements for hand-up review.

## Milestone 2 Section V Compliance Sources

- Constitution requirement baseline: `.specify/memory/constitution.md` (Principle V, version 1.2.0).
- Supplementary directory README set:
  - `database/README.md`
  - `docs/README.md`
  - `mcp_server/README.md`
  - `flask_web/README.md`
- Compliance evidence artifacts: `specs/002-milestone2-section-v/artifacts/`

## MCP Milestone Configuration/Test Sources

- Specification source: `specs/003-mcp-server-setup-tests/spec.md`
- Implementation plan source: `specs/003-mcp-server-setup-tests/plan.md`
- Contract source: `specs/003-mcp-server-setup-tests/contracts/mcp-milestone-tooling.md`
- Runbook source: `docs/mcp_milestone_test_guide.md`

## MCP Transport Compatibility Sources (Feature 004)

- Specification source: `specs/004-mcp-stdio-compat/spec.md`
- Implementation plan source: `specs/004-mcp-stdio-compat/plan.md`
- Contract source: `specs/004-mcp-stdio-compat/contracts/mcp-transport-compatibility.md`
- Quickstart source: `specs/004-mcp-stdio-compat/quickstart.md`
- Task execution ledger: `specs/004-mcp-stdio-compat/tasks.md`

## Quart Web Tier Integration Sources (Feature 006)

- Specification source: `specs/006-web-tier-integration/spec.md`
- Implementation plan source: `specs/006-web-tier-integration/plan.md`
- Task execution ledger: `specs/006-web-tier-integration/tasks.md`
- Quickstart runbook source: `specs/006-web-tier-integration/quickstart.md`
- Framework docs reference: Quart documentation (`https://quart.palletsprojects.com/`)
- Forms/CSRF reference: Flask-WTF documentation (`https://flask-wtf.readthedocs.io/`)
- Compatibility/legacy note reference: quart-wtf package metadata (used to evaluate package compatibility with current Quart stack)
- SDK reference: MCP Python SDK (`mcp` package) docs and examples in-repo

## Constitution Documentation Compliance Sources (Feature 008)

- Specification source: `specs/008-constitution-docs/spec.md`
- Implementation plan source: `specs/008-constitution-docs/plan.md`
- Contract source: `specs/008-constitution-docs/contracts/documentation-compliance-contract.md`
- Research and rationale source: `specs/008-constitution-docs/research.md`
- Data model source: `specs/008-constitution-docs/data-model.md`
- Quickstart verification source: `specs/008-constitution-docs/quickstart.md`
- Task execution ledger: `specs/008-constitution-docs/tasks.md`
- Canonical coverage matrix artifact: `docs/constitution/coverage-matrix.md`

Traceability policy used for this feature:
- Constitution and feature contracts are normative.
- README and evidence documents are synchronized delivery surfaces.
