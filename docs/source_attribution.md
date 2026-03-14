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
