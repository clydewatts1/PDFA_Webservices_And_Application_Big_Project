# WSGI Migration Checklist: Full Stack WSGI Migration

**Purpose**: Validate the completeness, clarity, consistency, and measurability of the WSGI migration requirements before implementation begins.  
**Created**: 2026-04-07  
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [x] CHK001 Are the required production route groups fully enumerated for migration, including health, authentication, dashboard/workspace, and each supported entity CRUD surface? [Completeness, Spec §FR-004, Spec §FR-009]
- [x] CHK002 Does the spec define the full supported MCP wrapper interface beyond `POST /rpc`, including whether any health or operational endpoints are required or intentionally excluded? [Completeness, Spec §MCP (Logic), Gap]
- [x] CHK003 Are the required environment variables for both WSGI applications explicitly specified in the requirements, not only in planning artifacts or quickstart guidance? [Completeness, Spec §FR-011, Gap]
- [x] CHK004 Does the spec state whether all current production Quart forms have direct Flask-WTF replacements, or which forms are intentionally out of scope? [Completeness, Spec §Web-Tier (Routes), Gap]

## Requirement Clarity

- [x] CHK005 Is “supported workflow-entity CRUD pages” defined precisely enough that reviewers can identify the exact in-scope entities without inferring from repository structure? [Clarity, Spec §FR-004, Ambiguity]
- [x] CHK006 Is “the only supported MCP server entrypoint” explicit about whether unsupported legacy entrypoints must be deleted, disabled, or merely undocumented? [Clarity, Spec §FR-002, Spec §FR-012]
- [ ] CHK007 Is the phrase “current production workflow UI” constrained with enough specificity that experimental Quart pages can be distinguished consistently during review? [Clarity, Spec §User Story 2, Spec §FR-004]
- [x] CHK008 Is “separately deployable WSGI service consumed by the Flask web tier over HTTP” specific about whether private/internal routing, hostnames, or URL boundaries must be documented for PythonAnywhere deployment? [Clarity, Spec §MCP (Logic), Spec §FR-003b]

## Requirement Consistency

- [ ] CHK009 Do the route-parity requirements align consistently between User Story 2, MCP/Web/Page partitions, and FR-004/FR-009 without expanding or shrinking scope across sections? [Consistency, Spec §User Story 2, Spec §Web-Tier (Routes), Spec §Page (UI), Spec §FR-004, Spec §FR-009]
- [x] CHK010 Do the transport requirements consistently state that valid JSON-RPC application errors return HTTP 200 while malformed transport cases use HTTP 400/500, without conflicting wording elsewhere in the spec? [Consistency, Spec §Clarifications, Spec §MCP (Logic), Spec §FR-003c, Spec §SC-003a]
- [ ] CHK011 Are the deployment requirements consistent with the constitution’s three-tier boundary and with the spec’s decision to keep the web tier and MCP wrapper as separate WSGI apps? [Consistency, Spec §Clarifications, Spec §Constitutional Constraints, Spec §FR-003b]
- [x] CHK012 Do the legacy-retirement requirements align with the assumption that some async-only assets may remain temporarily, or is there a conflict between “removed from supported operation” and “marked legacy during migration”? [Conflict, Spec §FR-012, Spec §Assumptions]

## Acceptance Criteria Quality

- [ ] CHK013 Can “successful end-to-end response over HTTP” be objectively verified from the User Story 1 acceptance scenarios without relying on unstated infrastructure assumptions? [Acceptance Criteria, Spec §User Story 1]
- [ ] CHK014 Are the route-parity acceptance scenarios measurable enough to determine whether navigation, submission, and validation behavior are “the same” as the current tier? [Measurability, Spec §User Story 2, Ambiguity]
- [x] CHK015 Do the success criteria define what evidence counts for “100% of reviewed active runbooks and setup documents,” including which documents are authoritative? [Acceptance Criteria, Spec §SC-004, Gap]
- [x] CHK016 Is SC-006 specific about which migration validation tests are mandatory so the implementation can be judged complete without interpretation drift? [Measurability, Spec §SC-006, Ambiguity]

## Scenario Coverage

- [ ] CHK017 Are requirements defined for the full happy-path chain of web tier request -> MCP wrapper -> handler dispatch -> response rendering, rather than only the endpoint and route endpoints in isolation? [Coverage, Spec §User Story 1, Spec §MCP (Logic), Spec §Web-Tier (Routes)]
- [x] CHK018 Are authenticated workflow-selection and active-workflow-context requirements documented clearly enough to cover the dashboard/workspace transition flows, not just CRUD pages? [Coverage, Spec §User Story 2, Spec §FR-004, Gap]
- [x] CHK019 Are deprecation requirements defined for how maintainers should treat Quart tests and docs during the migration window, not only after the migration is complete? [Coverage, Spec §User Story 3, Spec §FR-010, Spec §FR-012]

## Edge Case Coverage

- [x] CHK020 Are wrapper requirements complete for malformed JSON, malformed JSON-RPC envelopes, and unexpected server exceptions, with clear separation between transport-level and application-level failures? [Edge Case, Spec §Edge Cases, Spec §FR-003c]
- [ ] CHK021 Does the spec define what should happen if a route is migrated but its corresponding template, form, or MCP method parity is incomplete? [Edge Case, Spec §Edge Cases, Gap]
- [x] CHK022 Are requirements specified for the case where PythonAnywhere can host two WSGI apps but cross-app HTTP reachability or configuration is miswired? [Edge Case, Spec §Assumptions, Spec §FR-011, Gap]

## Non-Functional Requirements

- [ ] CHK023 Are performance expectations for synchronous HTTP request/response flows quantified enough to judge whether the WSGI migration remains acceptable for interactive use? [Non-Functional, Spec §Technical Context in plan.md, Gap]
- [x] CHK024 Are operational observability requirements defined for the new wrapper and Flask tier, such as required logs or error-trace semantics needed to debug migration regressions? [Non-Functional, Gap]
- [x] CHK025 Are security requirements for session handling, CSRF protection, and inter-app HTTP communication explicitly stated in the spec rather than assumed from framework defaults? [Non-Functional, Spec §Web-Tier (Routes), Gap]

## Dependencies & Assumptions

- [ ] CHK026 Is the assumption that the existing MCP handler/tool adapter is reusable validated with explicit requirements for unsupported async-only handler behavior, if any exists? [Assumption, Spec §Assumptions, Spec §FR-003a]
- [ ] CHK027 Does the spec document dependency expectations for PythonAnywhere hosting topology strongly enough to distinguish hard requirements from environmental assumptions? [Dependency, Spec §Assumptions, Ambiguity]
- [x] CHK028 Are dependency changes around `quart`, `quart-wtf`, `flask`, `flask-wtf`, and `requests` reflected as requirement-level expectations for the active stack, not just implementation intent? [Dependency, Spec §FR-010, Gap]

## Ambiguities & Conflicts

- [x] CHK029 Is it explicit whether the existing Flask JSON-RPC code in `mcp_server/src/api/app.py` is superseded, reused, or split, so reviewers can judge whether the design creates one wrapper path or two? [Ambiguity, Spec §MCP (Logic), Spec §FR-002]
- [x] CHK030 Does the spec resolve whether Quart artifacts remain only as historical references or as temporary transition assets during implementation, and how that affects acceptance of the final state? [Ambiguity, Spec §FR-012, Spec §Assumptions]

## Notes

- Focus areas selected: full feature scope, standard reviewer depth, with transport contract, boundary isolation, route parity, documentation/deployment, and testability treated as gating review areas.