# Data Model: Constitution Documentation Compliance Bundle

## Entity: ConstitutionRequirement
- Purpose: Represents a documentation obligation derived from constitution principles and quality gates.
- Fields:
  - `requirement_id` (string, required, unique)
  - `principle_ref` (string, required)
  - `description` (string, required)
  - `layer_scope` (enum: `MCP`, `Web-Tier`, `Page`, `Cross-cutting`)
  - `is_mandatory` (boolean, required)

## Entity: DocumentationArtifact
- Purpose: A concrete repository document used to satisfy one or more requirements.
- Fields:
  - `artifact_path` (string, required, unique)
  - `artifact_type` (enum: `README`, `evidence`, `attribution`, `spec`, `contract`, `runbook`)
  - `owner` (string, optional)
  - `last_reviewed` (date, optional)

## Entity: CoverageMatrixEntry
- Purpose: Canonical mapping record linking requirement to evidence.
- Canonical location: `docs/constitution/coverage-matrix.md`
- Required fields/columns:
  - `requirement ID` (string, required)
  - `status` (enum: `compliant`, `partial`, `missing`, required)
  - `evidence path` (string, required for `compliant`/`partial`)
  - `owner` (string, required)
  - `notes` (string, optional)
- Validation rules:
  - `requirement ID` must correspond to an existing `ConstitutionRequirement`.
  - `status=missing` may have empty `evidence path`, but must include remediation note in `notes`.

## Entity: DocumentationGap
- Purpose: Captures unresolved compliance issue for follow-up.
- Fields:
  - `gap_id` (string, required, unique)
  - `related_requirement_id` (string, required)
  - `severity` (enum: `high`, `medium`, `low`)
  - `impact` (string, required)
  - `proposed_fix` (string, required)
  - `owner` (string, required)
  - `target_milestone` (string, optional)

## Entity: RemediationAction
- Purpose: Planned/implemented action that closes a gap.
- Fields:
  - `action_id` (string, required, unique)
  - `gap_id` (string, required)
  - `changed_artifacts` (list[string], required)
  - `verification_method` (string, required)
  - `result` (enum: `pass`, `fail`, `partial`)

## Relationships
- `ConstitutionRequirement` 1..* -> 0..* `CoverageMatrixEntry`
- `DocumentationArtifact` 1..* -> 0..* `CoverageMatrixEntry`
- `CoverageMatrixEntry` 0..1 -> 0..1 `DocumentationGap`
- `DocumentationGap` 1 -> 0..* `RemediationAction`

## Lifecycle / State Transitions
- Coverage entry states: `missing` -> `partial` -> `compliant`
- Gap states (modeled in notes/actions): `identified` -> `planned` -> `resolved`
