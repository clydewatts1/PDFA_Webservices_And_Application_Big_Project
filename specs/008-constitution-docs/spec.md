# Feature Specification: Constitution Documentation Compliance Bundle

**Feature Branch**: `008-constitution-docs`  
**Created**: 2026-03-23  
**Status**: Draft  
**Input**: User description: "generate all documentation as required by constitution"

## Clarifications

### Session 2026-03-23

- Q: What canonical file path and minimum schema should be mandated for the constitution coverage matrix? → A: Use `docs/constitution/coverage-matrix.md` with required columns: requirement ID, status, evidence path, owner, notes.

## User Scenarios & Testing *(mandatory)*


### User Story 1 - Constitution Coverage Audit (Priority: P1)

As a project maintainer, I need a complete audit of constitution-required documentation so I can see exactly what is compliant, missing, outdated, or contradictory.

**Why this priority**: No remediation can be trusted until the documentation baseline is verified against constitutional obligations.

**Independent Test**: Can be fully tested by producing a coverage matrix that maps each constitutional documentation requirement to one or more concrete repository documents, with each requirement marked as compliant, partial, or missing.

**Acceptance Scenarios**:

1. **Given** the current constitution and repository docs, **When** the audit is run, **Then** each constitution documentation obligation has an explicit status and evidence path.
2. **Given** conflicting guidance between documents, **When** the audit is completed, **Then** each conflict is listed with the authoritative source and required correction.
3. **Given** missing documentation items, **When** the audit report is generated, **Then** each missing item includes ownership and a recommended destination file.

---

### User Story 2 - Remediation and Canonical Runbooks (Priority: P1)

As a developer or reviewer, I need startup/run/test documentation to be accurate and consistent across top-level and tier-level docs so I can reproduce the system without tribal knowledge.

**Why this priority**: Reproducible setup and execution are core constitutional quality gates and required for review.

**Independent Test**: Can be fully tested by following the documented Windows setup and runbook from a clean environment and reaching a successful start of required tiers plus documented tests.

**Acceptance Scenarios**:

1. **Given** a clean environment, **When** a reviewer follows the runbook, **Then** they can start the documented MCP and web tier services without undocumented steps.
2. **Given** multiple documentation files that reference startup commands, **When** remediation is complete, **Then** equivalent commands and environment variable names are aligned.
3. **Given** transport-related instructions, **When** reviewed, **Then** each transport mode is described consistently with a clear intended use case.

---

### User Story 3 - Traceability and Attribution Completion (Priority: P2)

As an assessor, I need external-source attribution, prompt traceability, and evidence references to be complete and discoverable so the development process is auditable.

**Why this priority**: Constitutional compliance explicitly requires source attribution and traceable process evidence.

**Independent Test**: Can be fully tested by verifying that every referenced external source class and workflow artifact has a documented path and that links resolve to existing files.

**Acceptance Scenarios**:

1. **Given** documentation updates are complete, **When** attribution is reviewed, **Then** all external references used by feature documentation are recorded in a dedicated attribution file.
2. **Given** prompt/process evidence requirements, **When** traceability docs are checked, **Then** a reviewer can navigate from README pointers to concrete evidence files.
3. **Given** section-V compliance artifacts are required, **When** validation is run, **Then** documented artifact paths exist and are consistent.

---

### Edge Cases

- What happens when a constitutional requirement maps to multiple documents with conflicting instructions?
- What happens when a required documentation file exists but contains stale commands that no longer match current runtime behavior?
- What happens when a required documentation area has no suitable existing file location?
- What happens when environment-specific instructions differ between Windows and non-Windows contexts?

## Layer Partition *(mandatory)*

- **MCP (Logic)**: Documentation must define MCP runtime responsibilities, transport interfaces, tool-contract expectations, and MCP-owned persistence boundaries.
- **Web-Tier (Routes)**: Documentation must define route-level responsibilities, tier boundaries, startup/run behavior, and error/interaction expectations with MCP.
- **Page (UI)**: Documentation must define user-facing navigation flow, page-level behavior expectations, and reviewer-visible outcomes.
- Each partition must explicitly state what is in scope and what remains out of scope for that layer.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project documentation set MUST provide a constitution-to-document mapping that covers all documentation obligations defined in the constitution.
- **FR-002**: The documentation set MUST include one canonical Windows setup/run/test flow for the three-tier architecture and clearly label legacy or alternative flows.
- **FR-003**: Startup instructions for MCP transports and web tiers MUST be internally consistent across top-level and supplementary README files.
- **FR-004**: The documentation set MUST include explicit environment variable requirements, example values for local setup, and where those values are consumed.
- **FR-005**: The documentation set MUST include explicit references to external-source attribution and prompt/process evidence required for auditability.
- **FR-006**: The documentation set MUST include a clear pointer structure from the main README to all critical runbooks and evidence artifacts.
- **FR-007**: Documentation updates MUST identify and resolve contradictions in architecture wording, tier naming, and expected communication boundaries.
- **FR-008**: The feature deliverable MUST include a documented gap list for any constitution-required items that cannot be completed in this increment, with rationale and follow-up owner.
- **FR-009**: The feature deliverable MUST include explicit section coverage for MCP (Logic), Web-Tier (Routes), and Page (UI) documentation responsibilities.
- **FR-010**: The feature deliverable MUST remain technology-agnostic at requirement level and avoid introducing undocumented implementation commitments.
- **FR-011**: The constitution coverage matrix MUST be maintained at `docs/constitution/coverage-matrix.md` and include, at minimum, the columns: `requirement ID`, `status`, `evidence path`, `owner`, and `notes`.

### Key Entities

- **ConstitutionRequirement**: A single documentation obligation derived from constitutional principles and quality gates.
- **DocumentationArtifact**: A repository document that satisfies one or more constitutional requirements.
- **CoverageMatrixEntry**: A traceable mapping record linking a ConstitutionRequirement to DocumentationArtifact(s), with status and evidence note.
- **CoverageMatrixEntry** fields: `requirement ID`, `status`, `evidence path`, `owner`, `notes`.
- **DocumentationGap**: A missing, stale, or conflicting documentation item that prevents full constitutional compliance.
- **RemediationAction**: A concrete update operation that resolves a DocumentationGap and records verification evidence.

### Constitutional Constraints *(mandatory when applicable)*

- Identify which layer or layers are affected and explain how Database -> MCP Server -> Quart
  Web Server boundaries remain intact.
- Confirm the feature was initiated through Spec Kit and that MCP (Logic), Web-Tier
  (Routes), and Page (UI) sections are present and complete.
- Describe any MCP contract additions or changes, including whether the interaction is
  JSON-RPC, SSE, or both.
- If the feature touches persistence, state how SQLAlchemy remains confined to the MCP server
  and how workflow schema integrity is preserved across Workflow, Role, Interaction, Guard,
  InteractionComponent, UnitOfWork, and Instance.
- If the feature touches persistence, describe how current and `_Hist` tables remain
  structurally symmetric, how `EffFromDateTime`, `EffToDateTime`, `DeleteInd`,
  `InsertUserName`, and `UpdateUserName` are preserved, how the primary table keeps only
  the current row per business key, and how MCP-owned current-state plus history logic
  maintains point-in-time integrity.
- List required environment variables or configuration changes.
- Record external sources, AI prompts, and Spec Kit guidance referenced while producing the
  feature materials, and note any README or directory-level README expectations triggered by
  the feature.

For this feature:

- **Affected layers**: All three documentation layers (MCP logic docs, web-tier route docs, UI/page behavior docs), with no runtime behavior changes required.
- **Boundary integrity**: The documentation must preserve Database -> MCP Server -> Quart Web Server ownership boundaries and MCP-over-HTTP communication constraints.
- **MCP contracts**: No new runtime contracts are introduced by this feature; documentation clarifies existing JSON-RPC/SSE and transport guidance.
- **Persistence constraints**: No schema mutation is in scope; documentation must keep MCP ownership of SQLAlchemy and temporal history orchestration explicit.
- **Environment variables**: Documentation must preserve and align required configuration variables for local startup.
- **Attribution and evidence**: Documentation updates must maintain source attribution and prompt/evidence traceability links.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of constitution-defined documentation obligations are mapped in a coverage matrix with status (`compliant`, `partial`, or `missing`).
- **SC-002**: 100% of required startup commands and environment variable instructions referenced by the primary runbook are reproducible from documentation alone in a Windows local setup.
- **SC-003**: 0 unresolved high-impact documentation contradictions remain for architecture boundary wording, tier naming, and transport startup guidance.
- **SC-004**: 100% of constitution-required attribution and evidence references are present and navigable from the main README.
- **SC-005**: A reviewer can locate all mandatory project documentation surfaces in under 5 minutes using only README-linked navigation (mandatory surfaces: canonical runbook, coverage matrix, source attribution, test evidence, and feature spec).
