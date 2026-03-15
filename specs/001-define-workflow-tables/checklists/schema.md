# Schema & Integrity Checklist: Workflow Interaction Schema Foundation

**Purpose**: Validate requirements quality for schema, temporal history lifecycle, and key integrity across spec/plan/tasks
**Created**: 2026-03-13
**Feature**: [Link to spec.md](../spec.md)

## Requirement Completeness

- [x] CHK001 Are control columns required for all seven canonical tables and their `_Hist` counterparts, not only described globally? [Completeness, Spec §FR-001, Spec §FR-003, Spec §FR-024]
- [x] CHK002 Are business-key definitions explicitly stated for every dependent entity (Role, Interaction, Guard, InteractionComponent) and Instance? [Completeness, Spec §FR-005, Spec §FR-006, Spec §FR-007, Spec §FR-008, Spec §FR-016]
- [x] CHK003 Are requirements explicit about which entities must be replicated during instantiation and whether UnitOfWork is intentionally excluded? [Completeness, Spec §FR-013]

## Requirement Clarity

- [x] CHK004 Is “instance-scoped rows in fixed tables” defined with unambiguous identifying fields (for example, InstanceName/InstanceId scoping columns)? [Clarity, Spec §FR-022]
- [x] CHK005 Is the rule “exactly one current primary-table row per business key” quantified with precise current-row criteria (DeleteInd and EffToDateTime semantics)? [Clarity, Spec §FR-019, Spec §FR-020]
- [x] CHK006 Is deferred SSE behavior clearly bounded so readers know it is out of scope for acceptance in this increment? [Clarity, Spec §FR-018]

## Requirement Consistency

- [x] CHK007 Do spec protocol requirements (JSON-RPC required, SSE deferred) align with plan constraints and contract artifact wording? [Consistency, Spec §FR-017, Spec §FR-018, Plan §Technical Context, Plan §Post-Design Constitution Check]
- [x] CHK008 Do key strategy requirements in spec align with data-model keys and relationships for all entities? [Consistency, Spec §FR-005..FR-008, Spec §FR-016, Data-Model §Entity Definitions]
- [x] CHK009 Do temporal lifecycle requirements align across spec requirements, assumptions, and success criteria without conflicting interpretations? [Consistency, Spec §FR-019, Spec §Assumptions, Spec §SC-002, Spec §SC-006]
- [x] CHK010 Are tasks written to preserve SQLAlchemy containment in MCP and avoid persistence leakage into Flask? [Consistency, Constitution Constraint, Plan §Constitution Check, Tasks §Phase 2]

## Acceptance Criteria Quality

- [x] CHK011 Can SC-002 and SC-006 be objectively validated from requirement text without implementation assumptions? [Measurability, Spec §SC-002, Spec §SC-006]
- [x] CHK012 Are failure expectations for invalid temporal windows and duplicate active keys defined as requirement outcomes (not just test ideas)? [Acceptance Criteria, Spec §Edge Cases, Spec §FR-023]

## Scenario & Edge Case Coverage

- [x] CHK013 Are recovery requirements defined for partial failures during instantiation replication (for example, rollback/atomicity behavior)? [Coverage, Exception Flow, Spec §FR-021]
- [x] CHK014 Are delete/restoration lifecycle requirements defined for previously deleted rows under single-primary-row constraints? [Coverage, Edge Case, Spec §FR-025, Spec §FR-026, Spec §FR-027]
- [x] CHK015 Are requirements explicit on how historical retrieval works when multiple versions share the same business key and close timestamps? [Coverage, Spec §FR-014, Spec §FR-028]

## Dependencies & Assumptions

- [x] CHK016 Is the assumption of globally unique `InstanceName` validated against long-term operability (rename/collision constraints) or explicitly bounded to MVP? [Assumption, Spec §FR-016, Spec §Assumptions]
- [x] CHK017 Are environment-variable requirements complete for all cross-tier dependencies referenced by plan and quickstart? [Dependency, Spec §Constitutional Constraints, Spec §FR-029, Plan §Technical Context, Quickstart]

## Notes

- Lightweight depth selected: checklist emphasizes high-impact schema and lifecycle quality checks.
- Scope selected: checks include consistency across spec, plan, tasks, and generated design artifacts.
- Review pass result: 17 passed, 0 gaps.
- Highest-priority gap: None.
