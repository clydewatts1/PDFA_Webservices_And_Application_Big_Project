# Research: Continue PostgreSQL to MySQL Refactor

Feature: 010-postgres-mysql-refactor  
Date: 2026-04-03  
Status: Complete

## Scope Clarification Resolution

All previously open scope decisions are resolved from clarification sessions:
- Migration scripts are proactively updated for MySQL compatibility.
- Contract and integration validation runs on MySQL only.
- No historical PostgreSQL backfill is performed.
- Rollback is permitted only in a 24-hour post-cutover window.

## Decision 1: Proactive Alembic MySQL Compatibility Updates

Decision: Update migration scripts where required before cutover, then verify baseline-to-head on MySQL.

Rationale:
- Reduces deployment-time uncertainty by resolving dialect issues ahead of runtime cutover.
- Aligns with explicit feature requirement FR-010 and FR-011.
- Preserves controlled, reviewable migration history.

Alternatives considered:
- Validate-only with no migration edits: rejected because it defers known risk to deployment.
- Full migration rewrite: rejected as unnecessary scope expansion and history disruption.

## Decision 2: MySQL-Only Contract and Integration Validation

Decision: Run contract and integration suites against MySQL as the required validation target.

Rationale:
- Prevents false confidence from SQLite-only behavior that may differ from MySQL dialect semantics.
- Directly satisfies clarified requirement FR-006.
- Makes pass/fail outcomes representative of production cutover target.

Alternatives considered:
- Hybrid SQLite plus MySQL gate: rejected due to clarification selecting MySQL-only for these tiers.
- SQLite-only execution: rejected due to insufficient cutover confidence.

## Decision 3: No Historical Data Backfill Strategy

Decision: Initialize MySQL schema baseline and accept only post-cutover writes; legacy PostgreSQL data remains in legacy store.

Rationale:
- Significantly lowers migration complexity and avoids data transform risk in current increment.
- Keeps feature focused on runtime and operational migration completion.
- Matches clarified requirements FR-012 and FR-013.

Alternatives considered:
- One-time export/import: rejected by clarification.
- Dual-write transition: rejected by clarification and operational complexity.

## Decision 4: Time-Boxed Rollback Model

Decision: Allow rollback to PostgreSQL only within a 24-hour post-cutover validation window with explicit trigger criteria.

Rationale:
- Balances safety and decisiveness: meaningful rollback protection without indefinite split operation.
- Supports predictable incident response and governance sign-off.
- Matches FR-014, FR-015, and SC-009.

Alternatives considered:
- No rollback (fix-forward only): rejected due to operational risk concentration.
- Extended dual-run fallback: rejected for operational overhead and boundary complexity.

## Decision 5: SCD and Seven-Table Workflow Integrity Preservation

Decision: Preserve current plus `_Hist` structural symmetry and MCP-owned temporal orchestration without schema redesign.

Rationale:
- Required by constitution Principle III.a and existing domain behavior.
- Avoids introducing business-regression risk while changing database backend.
- Keeps increment focused on migration completion, not domain remodeling.

Alternatives considered:
- Schema consolidation or history model changes: rejected as out of scope and constitutionally risky.

## Decision 6: Documentation and Environment Contract Updates

Decision: Update active runbooks and setup guides to reflect MySQL-first runtime, MySQL-only validation target, no-backfill cutover model, and 24-hour rollback governance.

Rationale:
- Prevents operational ambiguity across developer, reviewer, and deployment workflows.
- Needed for constitutional traceability and auditability.
- Ensures reproducible execution across local and CI environments.

Alternatives considered:
- Code-only change with minimal docs: rejected because migration operations are documentation-sensitive.

## Reviewer Grep Procedure

Before sign-off, run a repository search for active PostgreSQL runtime defaults:

```powershell
rg -n "postgres|postgresql|sqlite:///./local.db" README.md .env.example docs specs mcp_server quart_web database
```

Interpretation rules:
- Matches in `specs/009-postgres-to-mysql-refactor/` and `specs/010-postgres-mysql-refactor/` are allowed when they describe lineage, rollback policy, or rejected alternatives.
- Matches in operational docs are allowed only when they explicitly describe rollback-window governance or historical comparison.
- Matches in active runtime examples, environment defaults, or contract/integration validation commands must be treated as defects.

## Historical Reference Allowlist

The following categories may retain PostgreSQL references without blocking sign-off:
- Feature-history references that explain continuation from feature 009.
- Rollback-window guidance that documents how PostgreSQL remains available for 24 hours after cutover.
- Archived evidence entries describing pre-MySQL validation history.
