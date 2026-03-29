# Quickstart: Constitution Documentation Compliance Bundle

## Purpose
Execute a complete constitution-driven documentation audit and remediation pass for this repository.

## Prerequisites
- Repository cloned locally
- Windows PowerShell
- Python environment available (for documented run/test command verification)
- Feature artifacts present under `specs/008-constitution-docs/`

## 1) Build the canonical coverage matrix
Create/update:
- `docs/constitution/coverage-matrix.md`

Required columns:
- `requirement ID`
- `status`
- `evidence path`
- `owner`
- `notes`

## 2) Audit constitution requirements against docs
Compare constitution obligations to:
- `README.md`
- `docs/README.md`
- `mcp_server/README.md`
- `flask_web/README.md`
- `quart_web/README.md`
- `docs/source_attribution.md`
- `docs/test_evidence.md`

Mark each requirement in the matrix as:
- `compliant`
- `partial`
- `missing`

## 3) Normalize startup/run instructions
- Keep one canonical Windows-first flow in `README.md`
- Ensure supplemental READMEs align and point back to canonical flow
- Ensure transport guidance clearly distinguishes use cases (`stdio`, `sse`, `http`)

## 4) Validate traceability pointers
Confirm `README.md` links to:
- source attribution
- test evidence
- relevant spec artifacts
- coverage matrix

## 5) Record unresolved gaps
For any unresolved requirement:
- add a matrix row with `status=missing` or `partial`
- include owner and concrete follow-up in `notes`

## 6) Reviewer smoke check
A reviewer should be able to:
1. Find canonical runbook from `README.md`
2. Start required tiers using documented commands
3. Locate evidence + attribution from README pointers
4. Verify coverage matrix completeness quickly

### Pass/Fail Capture Template

- smoke_start_utc:
- smoke_end_utc:
- elapsed_minutes:
- runbook_found_from_readme: PASS/FAIL
- mcp_runtime_start: PASS/FAIL
- quart_start: PASS/FAIL
- attribution_and_evidence_links: PASS/FAIL
- coverage_matrix_schema_valid: PASS/FAIL
- overall_smoke_result: PASS/FAIL

### Expected Runtime Indicators

- MCP network transport starts on `127.0.0.1:5001` without startup exceptions.
- Quart starts on `127.0.0.1:5002` and serves `/`.
- README links resolve to `docs/constitution/coverage-matrix.md`, `docs/source_attribution.md`, and `docs/test_evidence.md`.

## Expected Outcome
- Constitution documentation obligations are fully mapped
- Contradictions are resolved or explicitly tracked with owners
- Reviewer navigation path is complete and auditable
