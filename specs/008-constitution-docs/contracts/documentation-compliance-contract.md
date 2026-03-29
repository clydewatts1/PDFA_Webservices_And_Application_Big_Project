# Contract: Documentation Compliance Review Interface

## Purpose
Define the required input/output structure for constitution documentation audit and remediation reviews in this feature.

## Consumer
- Human reviewer
- Documentation maintainer
- Spec Kit task execution flow (`/speckit.tasks`)

## Inputs
- Constitution source: `.specify/memory/constitution.md`
- Feature spec: `specs/008-constitution-docs/spec.md`
- Current documentation set:
  - `README.md`
  - `docs/README.md`
  - `mcp_server/README.md`
  - `flask_web/README.md`
  - `quart_web/README.md`
  - `docs/source_attribution.md`
  - `docs/test_evidence.md`

## Normative Authority Order
Conflict resolution authority is:
1. Constitution (`.specify/memory/constitution.md`)
2. Current feature specification and contracts (`specs/008-constitution-docs/spec.md`, `specs/008-constitution-docs/contracts/`)
3. Canonical coverage matrix (`docs/constitution/coverage-matrix.md`)
4. Derived delivery documents (`README.md`, directory READMEs, evidence docs)

All README/evidence documents MUST be synchronized to the higher-order sources and MUST NOT be treated as source-of-truth authorities.

## Required Output Artifacts
1. Canonical coverage matrix: `docs/constitution/coverage-matrix.md`
2. Updated documentation files with normalized startup/architecture guidance
3. Explicit unresolved gap notes (if any) with owner and follow-up

## Coverage Matrix Schema (Normative)
The matrix **must** contain columns:
- `requirement ID`
- `status`
- `evidence path`
- `owner`
- `notes`

### Status Domain
- `compliant`
- `partial`
- `missing`

### Validation Rules
- `requirement ID` maps to a constitutional or derived feature requirement.
- `status` must be one of the defined domain values.
- `evidence path` is required for `compliant` and `partial` rows.
- `owner` is required for all rows.
- `notes` is required when `status` is `partial` or `missing`.

## Review Acceptance Contract
A review is accepted when all are true:
1. Canonical matrix exists at the required path and matches schema.
2. README entry points can navigate to runbook + evidence + attribution + matrix.
3. No unresolved contradiction remains undocumented.
4. Any unresolved items are explicitly tracked with owner and follow-up notes.

## Non-Goals
- Introducing new runtime features
- Changing architecture boundaries
- Altering transport semantics beyond documentation clarification
