# Research: Constitution Documentation Compliance Bundle

## Decision 1: Canonical coverage matrix location and schema
- Decision: Use `docs/constitution/coverage-matrix.md` as the single canonical coverage matrix.
- Rationale: A single reviewer-facing location minimizes drift and satisfies clarification A + FR-011.
- Alternatives considered:
  - Keep matrix inline in `spec.md` (rejected: mixes planning artifact with operational compliance artifact).
  - Use JSON as primary matrix (rejected: less reviewer-friendly for manual audit workflows).

## Decision 2: Source of truth hierarchy for conflicting documentation
- Decision: Resolve conflicts in this order: constitution -> current feature spec/contracts -> canonical coverage matrix (`docs/constitution/coverage-matrix.md`) -> implementation documentation surfaces (all README/evidence docs as derived artifacts).
- Rationale: Constitution and feature artifacts are normative; README files are delivery surfaces that must be synchronized, not treated as authority sources.
- Alternatives considered:
  - Root README as global authority (rejected: README content can lag and is not a normative governance source).
  - Last-modified file wins (rejected: non-deterministic and unsafe).

## Decision 3: Startup/runbook normalization strategy
- Decision: Normalize to one canonical Windows-first runbook in root `README.md`, with supplementary READMEs linking back and adding local detail only.
- Rationale: Reduces contradictory command drift while preserving component-level context.
- Alternatives considered:
  - Full duplicated runbook in each README (rejected: high drift risk).
  - No canonical runbook, only component docs (rejected: poor onboarding and review flow).

## Decision 4: Transport documentation policy
- Decision: Document transport modes by intended use case: `stdio` (inspector/local tool use), `sse`/`http` (network/web tier use), and keep endpoint expectations explicit.
- Rationale: Existing docs already include multiple transport commands; intent labeling resolves confusion.
- Alternatives considered:
  - Remove non-primary transports from docs (rejected: loses required compatibility evidence context).

## Decision 5: Evidence and attribution traceability model
- Decision: Maintain explicit pointers from root `README.md` to `docs/source_attribution.md`, `docs/test_evidence.md`, and feature artifacts.
- Rationale: Supports constitutional traceability and fast reviewer navigation (SC-005).
- Alternatives considered:
  - Keep evidence references only inside `docs/` (rejected: lower discoverability from onboarding entry point).

## Decision 6: Documentation gap handling
- Decision: Record unresolved or intentionally deferred constitutional items in a structured gap list with owner and follow-up note.
- Rationale: Satisfies FR-008 while avoiding silent non-compliance.
- Alternatives considered:
  - Leave unresolved items undocumented (rejected: violates auditability).

## Resolved Clarifications
- All `NEEDS CLARIFICATION` items are resolved for planning.
- Canonical matrix location/schema fixed: `docs/constitution/coverage-matrix.md` with columns `requirement ID`, `status`, `evidence path`, `owner`, `notes`.
