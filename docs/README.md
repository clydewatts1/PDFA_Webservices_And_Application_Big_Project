# Documentation Layer

This directory contains hand-up and traceability documentation used for project review.

This README is a navigation hub (delivery surface). Normative authority order is:
constitution → feature spec/contracts → coverage matrix → README/evidence documents.

## Responsibilities

- Maintain external-source attribution records.
- Preserve prompt-level traceability for AI-assisted development.
- Capture validation evidence and review-oriented notes.

## Boundary Notes

- Documentation supports all architectural tiers but does not implement runtime behavior.
- Runtime architecture remains Database -> MCP Server -> Flask Web Server, with the Flask MCP wrapper and Flask web tier as the only canonical run path.

## Canonical Runbook Alignment

- Canonical Windows run/test flow: `README.md`
- MCP network transport command: `python -m mcp_server.src.wsgi_app`
- Flask startup command: `python -m flask_web.src.app`
- Legacy supplemental Quart startup command: `python -m quart_web.src.app` (manual only)
- Required env vars for canonical web tier: `SESSION_SECRET`, `MCP_RPC_URL`, `MCP_TIMEOUT_SECONDS`

## Key Documents

- `constitution/coverage-matrix.md`
- `source_attribution.md`
- `test_evidence.md`
- `prompts/prompt_log.md`

## Reviewer Navigation Path

1. Start at root `README.md` canonical runbook.
2. Open `constitution/coverage-matrix.md` for requirement-to-evidence mapping.
3. Review `source_attribution.md` and `test_evidence.md` for supporting evidence.
4. Inspect feature artifacts under `specs/008-constitution-docs/`.
