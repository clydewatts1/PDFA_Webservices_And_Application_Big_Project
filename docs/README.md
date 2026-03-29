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
- Runtime architecture remains Database -> MCP Server -> Quart Web Server (with legacy Flask tier retained for backward compatibility).

## Canonical Runbook Alignment

- Canonical Windows run/test flow: `README.md`
- MCP network transport command: `python -m mcp_server.src.server --transport http --host 127.0.0.1 --port 5001`
- Quart startup command: `python -m quart_web.src.app`
- Legacy supplemental Flask startup command: `python -m flask_web.src.app`
- Required env vars for web tier: `MCP_SERVER_URL`, `SESSION_SECRET`

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
