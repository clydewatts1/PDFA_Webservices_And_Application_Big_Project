# Quickstart: Milestone 2 Section V Compliance Validation

## 1) Scope Confirmation
- Confirm working branch is `002-milestone2-section-v`.
- Confirm this milestone is documentation/compliance only and does not change tier architecture or MCP contracts.

## 2) Review Supplementary README Coverage
- Verify top-level `README.md` exists and references directory-level documentation expectations.
- Verify supplementary README presence and content quality in each in-scope major directory:
  - `database/`
  - `docs/`
  - `mcp_server/`
  - `flask_web/`

## 3) Review Docstring Compliance
- Inspect in-scope custom business-logic modules and ensure module-level docstrings are present.
- Inspect non-trivial functions/methods and ensure function-level docstrings are present where intent is not self-evident.

## 4) Review Boilerplate Comment Policy
- Inspect framework boilerplate files (especially Alembic migrations and scaffolding) and remove unnecessary explanatory inline comments.
- Retain comments only when they explain project-specific deviations.

## 5) Validate Attribution and Prompt Traceability
- Verify `docs/source_attribution.md` remains current and consistent with README guidance.
- Verify `docs/prompts/prompt_log.md` remains discoverable and current.
- Verify README artifacts point reviewers to these canonical evidence sources.

## 6) Optional Regression Confidence
Run existing tests to confirm no incidental behavior regressions from non-functional edits:

```powershell
.venv\Scripts\python.exe -m pytest mcp_server/tests/ -v --tb=short
```

## 7) Compliance Review Output
Produce a final Section V compliance result using the contract in `contracts/section-v-compliance-review.md`.
Mark the milestone complete only when all checklist categories pass with zero unresolved issues.
