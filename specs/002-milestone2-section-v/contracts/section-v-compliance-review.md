# Section V Compliance Review Contract

## Purpose
Define the review contract for Milestone 2 to verify compliance with Constitution Section V requirements without altering runtime application behavior.

## Inputs
- Updated top-level README and supplementary directory READMEs.
- In-scope custom business-logic modules/functions in MCP and Flask layers.
- Attribution and prompt-traceability records (`docs/source_attribution.md`, `docs/prompts/prompt_log.md`).

## Review Checklist Interface

### 1) Directory README Coverage
- Required directories in scope provide a local README with:
  - directory purpose,
  - architecture responsibility,
  - boundary relationship to Database -> MCP -> Flask chain.
- Expected result: `pass` when all in-scope directories are covered or explicitly justified.

### 2) Docstring Compliance
- Custom business-logic modules contain module-level docstrings.
- Non-trivial functions/methods contain function-level docstrings.
- Any self-evident exceptions are documented in a rationale inventory and reviewer-approved.
- Expected result: `pass` when all reviewed items are either documented or justified as self-evident.

### 3) Boilerplate Comment Policy
- Framework boilerplate files do not contain unnecessary explanatory inline comments.
- Any retained commentary has explicit project-specific justification and reviewer approval.
- Expected result: `pass` when no unjustified boilerplate commentary remains.

### 4) Attribution and Prompt Traceability
- README artifacts link to or reference canonical attribution and prompt-log records.
- Evidence paths remain accurate and discoverable.
- Expected result: `pass` when a reviewer can navigate from README content to provenance records directly.

### 5) Commit Traceability Quality
- Task execution history is reflected in meaningful Git commit checkpoints aligned to major remediation chunks.
- Commit messages are specific enough to map changes to Section V compliance outcomes.
- Expected result: `pass` when commit history demonstrates reviewable progression, not coarse undifferentiated batches.

## Output Schema

```json
{
  "check_date": "YYYY-MM-DD",
  "overall_result": "pass|fail",
  "results": {
    "directory_readme_coverage": "pass|fail",
    "docstring_compliance": "pass|fail",
    "boilerplate_comment_policy": "pass|fail",
    "attribution_traceability": "pass|fail",
    "commit_traceability_quality": "pass|fail"
  },
  "evidence_paths": [
    "README.md",
    "docs/source_attribution.md",
    "docs/prompts/prompt_log.md"
  ],
  "open_issues": []
}
```

## Failure Conditions
- Any required directory lacks a supplementary README without explicit scope justification.
- Any reviewed non-trivial custom business-logic symbol lacks a required docstring.
- Unnecessary inline boilerplate commentary remains without justification.
- Attribution or prompt-traceability records are missing, stale, or undiscoverable from README context.
- Commit history is too coarse to demonstrate meaningful milestone progression.

## Non-Goals
- Introducing new MCP JSON-RPC or SSE methods.
- Modifying persistence schema or runtime architecture.
- Adding automated policy enforcement tooling in this milestone.
