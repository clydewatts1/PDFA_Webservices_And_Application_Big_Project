# Research: Milestone 2 Section V Alignment

## Decision 1: Docstring Remediation Scope
- Decision: Apply module-level and function-level docstrings to custom business-logic modules/functions in MCP and Flask codepaths, prioritizing files where intent is not obvious from naming/signature alone.
- Rationale: Section V requires traceable, reviewer-friendly explanation of custom logic while avoiding mechanical over-documentation of trivial code.
- Alternatives considered: Add docstrings to every function indiscriminately; rejected as noisy and contrary to readability goals.

## Decision 2: Boilerplate Comment Policy
- Decision: Remove or avoid inline explanatory commentary in framework boilerplate (especially Alembic migration scaffolding) unless a project-specific deviation must be justified.
- Rationale: Constitution Section V explicitly prohibits over-commenting standard framework boilerplate.
- Alternatives considered: Keep legacy commentary for historical context; rejected because it conflicts with the amended rule.

## Decision 3: Major Directory README Coverage
- Decision: Require supplementary README files in major project directories (`database`, `docs`, `mcp_server`, `flask_web`) with concise local architecture and responsibility statements.
- Rationale: Section V now requires directory-level documentation that complements the top-level README for hand-up review.
- Alternatives considered: Top-level README only; rejected because it fails the explicit constitution requirement.

## Decision 4: Attribution and Prompt Traceability Continuity
- Decision: Keep `docs/source_attribution.md` and `docs/prompts/prompt_log.md` as canonical provenance records and cross-reference them from relevant README content.
- Rationale: Preserves audit trail continuity and avoids fragmentation of evidence sources.
- Alternatives considered: Move attribution into multiple ad-hoc README sections only; rejected because it weakens centralized traceability.

## Decision 5: Compliance Verification Method
- Decision: Define a repeatable compliance review checklist contract and quickstart validation steps rather than introducing runtime enforcement.
- Rationale: This milestone is governance/documentation focused and should remain non-invasive to system runtime behavior.
- Alternatives considered: Build automated AST/comment lint enforcement in this milestone; deferred to avoid scope expansion beyond requested Milestone 2 planning.
