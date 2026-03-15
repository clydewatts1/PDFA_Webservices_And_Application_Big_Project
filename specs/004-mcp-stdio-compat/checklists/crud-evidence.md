# CRUD Scope & Evidence Checklist: MCP Stdio Inspector Compatibility

**Purpose**: Validate that CRUD scope boundaries and manual verification/runbook requirements are complete, clear, consistent, and measurable before PR approval.
**Created**: 2026-03-15
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [x] CHK001 Are in-scope CRUD families explicitly and exhaustively listed with no implicit additions? [Completeness, Spec §FR-003]
- [x] CHK002 Are out-of-scope CRUD families (`unit_of_work.*`, `instance.*`) explicitly excluded from required discovery and parity scope? [Completeness, Spec §FR-003]
- [x] CHK003 Are all required CRUD operations (`create|get|list|update|delete`) specified for each in-scope family? [Completeness, Spec §FR-010]
- [x] CHK004 Are manual verification requirements defined for both mandatory SQLite and optional PostgreSQL paths? [Completeness, Spec §FR-014]
- [x] CHK005 Are negative-path verification requirements documented for malformed config, DB failure, auth payload errors, and invalid CRUD inputs? [Completeness, Spec §FR-015]

## Requirement Clarity

- [x] CHK006 Is “in-scope operations” unambiguously tied to FR-003 tool families rather than inferred broadly? [Clarity, Spec §FR-003, Spec §FR-017]
- [x] CHK007 Are `get/update/delete` identifier requirements specific enough to avoid ambiguity between business keys and technical IDs? [Clarity, Spec §FR-012]
- [x] CHK008 Are pagination constraints precise enough to determine valid/invalid `limit` and `offset` inputs objectively? [Clarity, Spec §FR-013]
- [x] CHK009 Are expected CRUD response semantics (`SUCCESS|ERROR` plus `status_message`) defined independently of transport metadata? [Clarity, Spec §FR-011]

## Requirement Consistency

- [x] CHK010 Do spec CRUD scope statements align with transport-contract required tools and exclusions? [Consistency, Spec §FR-003, Contract §Scope]
- [x] CHK011 Do quickstart validation steps align with spec requirements for required tool discovery and parity checks? [Consistency, Spec §FR-003, Spec §FR-014, Quickstart §4-§6]
- [x] CHK012 Do task definitions preserve the same CRUD scope boundaries and avoid reintroducing deferred families? [Consistency, Spec §FR-003, Tasks §US3]
- [x] CHK013 Do parity requirements for CRUD semantics avoid conflicting wording between FR-011 and FR-017? [Consistency, Spec §FR-011, Spec §FR-017]

## Acceptance Criteria Quality

- [x] CHK014 Can SC-002 and SC-004 be objectively validated from the written runbook requirements without hidden assumptions? [Measurability, Spec §SC-002, Spec §SC-004]
- [x] CHK015 Are completion thresholds in SC-005 testable with explicit start/end timing evidence expectations? [Measurability, Spec §SC-005, Tasks §T048]
- [x] CHK016 Are parity outcomes defined with measurable fields (status/status_message/required fields) for equivalent CRUD inputs? [Acceptance Criteria, Spec §FR-011, Spec §FR-017]

## Scenario Coverage

- [x] CHK017 Are requirements defined for CRUD rejection when keys are missing or malformed for `get/update/delete`? [Coverage, Spec §FR-012, Spec §Edge Cases]
- [x] CHK018 Are requirements defined for invalid pagination rejection and documented as negative-path verification steps? [Coverage, Spec §FR-013, Spec §FR-015]
- [x] CHK019 Are requirements defined for persistence-evidence verification after successful CRUD operations (not response-only validation)? [Coverage, Spec §FR-014, Spec §US3 Acceptance 2]

## Edge Case Coverage

- [x] CHK020 Is behavior for tool-discovery mismatch between transports specified as a deterministic failure condition? [Edge Case, Contract §Failure Conditions, Spec §FR-017]
- [x] CHK021 Are requirements explicit on what evidence must be recorded when reviewer prerequisites (`npx`, `sqlite3`) are missing? [Edge Case, Spec §Edge Cases, Gap]

## Dependencies & Assumptions

- [x] CHK022 Are assumptions about local environment tools (Node.js, Inspector, sqlite3) reflected as explicit dependency checks in runbook steps? [Dependency, Spec §Assumptions, Quickstart §1]
- [x] CHK023 Are DB configuration dependencies (`.env`, `DB_URL`, config path) traceably linked to verification steps and failure diagnostics? [Dependency, Spec §FR-005, Quickstart §2, §8]

## Ambiguities & Conflicts

- [x] CHK024 Is any remaining ambiguity documented for reviewer interpretation of optional PostgreSQL verification versus mandatory SQLite verification? [Ambiguity, Spec §FR-014]
- [x] CHK025 Are any conflicts between spec, tasks, and contract explicitly listed for resolution before implementation resumes? [Conflict, Spec §FR-016, Tasks §Polish, Contract §Validation Runbook]

## Notes

- Focus: CRUD scope + runbook evidence
- Depth: Standard
- Audience: PR reviewer
- Use this as a requirements-quality gate; check items after reviewing requirements text, not runtime behavior.
- Validation completed: 2026-03-15.
