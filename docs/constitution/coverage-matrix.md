# Constitution Coverage Matrix

Canonical path mandated by FR-011.

| requirement ID | status | evidence path | owner | notes |
|---|---|---|---|---|
| FR-001 | compliant | `docs/constitution/coverage-matrix.md` | docs-maintainer | Matrix maps all required documentation obligations. |
| FR-002 | compliant | `README.md` | docs-maintainer | Canonical Windows setup/run/test flow defined; supplementary docs link back. |
| FR-003 | compliant | `README.md`, `mcp_server/README.md`, `quart_web/README.md`, `flask_web/README.md`, `docs/README.md` | docs-maintainer | Transport labels and startup guidance normalized. |
| FR-004 | compliant | `README.md`, `quart_web/README.md`, `mcp_server/README.md` | docs-maintainer | Environment variables and consumption points documented. |
| FR-005 | compliant | `README.md`, `docs/source_attribution.md`, `docs/prompts/prompt_log.md`, `docs/test_evidence.md` | docs-maintainer | Attribution and process evidence pointers are explicit. |
| FR-006 | compliant | `README.md`, `docs/README.md` | docs-maintainer | README pointer structure includes runbook + evidence + matrix. |
| FR-007 | compliant | `specs/008-constitution-docs/artifacts/remediation-log.md`, `docs/README.md` | docs-maintainer | Contradictions recorded and reconciled with authority order. |
| FR-008 | compliant | `specs/008-constitution-docs/artifacts/gap-list.md` | docs-maintainer | Gap list includes owner/follow-up semantics; no open gaps in this increment. |
| FR-009 | compliant | `specs/008-constitution-docs/spec.md`, `specs/008-constitution-docs/artifacts/spec-partition-validation.md` | docs-maintainer | MCP/Web-Tier/Page partition validated. |
| FR-010 | compliant | `specs/008-constitution-docs/artifacts/requirement-language-rules.md` | docs-maintainer | Requirement language guardrails are technology-agnostic. |
| FR-011 | compliant | `docs/constitution/coverage-matrix.md` | docs-maintainer | Required schema preserved: requirement ID, status, evidence path, owner, notes. |
| SC-001 | compliant | `docs/constitution/coverage-matrix.md`, `specs/008-constitution-docs/artifacts/us1-validation.md` | docs-maintainer | 100% requirement mapping completed. |
| SC-002 | partial | `README.md`, `docs/test_evidence.md` | docs-maintainer | Documentation reproducibility verified; full clean-machine runtime proof remains periodic reviewer task. |
| SC-003 | compliant | `specs/008-constitution-docs/artifacts/remediation-log.md`, `docs/README.md` | docs-maintainer | No unresolved high-impact documentation contradictions. |
| SC-004 | compliant | `README.md`, `docs/source_attribution.md`, `docs/test_evidence.md`, `docs/prompts/prompt_log.md` | docs-maintainer | Attribution/evidence references are navigable from README. |
| SC-005 | compliant | `README.md`, `docs/README.md`, `specs/008-constitution-docs/artifacts/us3-validation.md` | docs-maintainer | Mandatory surfaces are discoverable via README-linked navigation. |

## Ownership and Follow-Up

- Primary owner: `docs-maintainer`
- Review cadence: each feature closure and pre-hand-up validation sweep.
