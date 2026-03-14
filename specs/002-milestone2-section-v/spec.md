# Feature Specification: Milestone 2 Section V Alignment

**Feature Branch**: `002-milestone2-section-v`  
**Created**: 2026-03-13  
**Status**: Draft  
**Input**: User description: "Milestone 2 - update the code and documentation according to the changes to the constitution section V"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bring Custom Business Logic Documentation into Compliance (Priority: P1)

As an instructor or reviewer, I need custom business logic to carry clear module-level and function-level docstrings so that I can understand the intent of the codebase without reverse-engineering implementation details.

**Why this priority**: This is the most direct behavioral change introduced by the amended constitution and is the fastest way to make the codebase reviewable under the new grading criteria.

**Independent Test**: Can be fully tested by reviewing a representative sample of custom business-logic modules and functions across the repository and confirming required docstrings are present while standard framework boilerplate remains free of explanatory inline commentary.

**Acceptance Scenarios**:

1. **Given** a custom business-logic module without a descriptive module docstring, **When** the milestone changes are applied, **Then** the module includes a docstring that explains its responsibility in reviewer-facing language.
2. **Given** a custom business-logic function without a descriptive function docstring, **When** the milestone changes are applied, **Then** the function includes a docstring that explains its purpose, inputs, or outputs at the level needed for academic review.
3. **Given** framework-generated or boilerplate code such as migration scaffolding, **When** the milestone changes are applied, **Then** unnecessary inline commentary is absent unless a non-obvious customization must be justified.

---

### User Story 2 - Complete Major-Directory Documentation Coverage (Priority: P2)

As a new project reviewer, I need each major directory to explain its local role in the overall design so that I can navigate the repository and understand how responsibilities are split across the three-tier architecture.

**Why this priority**: Section V now requires supplementary README files in major directories, and without them the repository fails the updated submission standard even if the code itself is correct.

**Independent Test**: Can be fully tested by inspecting each major project directory and confirming that the required README explains local responsibilities, architecture boundaries, and how the directory fits into the overall project.

**Acceptance Scenarios**:

1. **Given** a major project directory that currently lacks a local README, **When** the milestone changes are applied, **Then** the directory includes a supplementary README describing its purpose and relationship to the rest of the system.
2. **Given** a major project directory with a local README, **When** a reviewer reads it, **Then** it explains the directory's responsibilities clearly enough to orient someone reviewing the repository for the first time.

---

### User Story 3 - Preserve Attribution and Submission Traceability (Priority: P3)

As a hand-up reviewer, I need the repository documentation to preserve external-source attribution and prompt/tool traceability after the Milestone 2 updates so that academic provenance remains auditable.

**Why this priority**: The constitution change raises the documentation bar, but the project still needs continuity with the existing prompt log and attribution records rather than creating disconnected documentation.

**Independent Test**: Can be fully tested by reviewing the top-level documentation set and confirming that source attribution, AI/tool usage notes, and hand-up guidance remain current after the new Section V documentation changes.

**Acceptance Scenarios**:

1. **Given** existing attribution and prompt-traceability records, **When** Milestone 2 documentation updates are completed, **Then** those records still identify external assistance and remain aligned with the updated README guidance.
2. **Given** the final repository documentation set, **When** an instructor audits the submission evidence, **Then** the documentation consistently points to the relevant attribution and traceability records without contradictions.

### Edge Cases

- A module mixes custom business logic with thin framework integration, making it unclear whether docstrings or boilerplate-comment removal takes precedence.
- A major directory exists primarily for generated or support assets and needs documentation proportional to its role rather than unnecessary repetition.
- Existing comments in business logic explain behavior that is still non-obvious and should be retained or rewritten rather than removed blindly.
- Existing top-level and local READMEs duplicate each other and need consolidation so the documentation remains consistent.
- Attribution documents reference prior milestone behavior that must stay valid after Milestone 2 wording changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The project MUST identify all major repository directories that require supplementary README coverage for final submission using an explicit discovery inventory rooted at first-level repository directories relevant to source, runtime, persistence, or hand-up documentation.
- **FR-002**: Each identified major directory MUST provide a supplementary README that explains its local purpose, responsibilities, and relationship to the overall three-tier architecture.
- **FR-003**: The top-level project README MUST remain the primary hand-up entry point and MUST reference the existence and purpose of supplementary directory-level READMEs.
- **FR-004**: Custom business-logic modules MUST include module-level docstrings that explain their purpose in reviewer-facing language.
- **FR-005**: Custom business-logic functions and methods whose intent is not self-evident from their signature alone MUST include function-level docstrings describing their purpose and expected behavior; self-evident exceptions MUST be captured in a documented rationale inventory.
- **FR-006**: Standard framework boilerplate and generated scaffolding MUST NOT accumulate explanatory inline comments unless a project-specific deviation requires clarification, and each retained exception MUST include reviewer-approved justification.
- **FR-007**: Existing explanatory comments in custom business logic MUST be reviewed so that useful, non-redundant guidance is preserved while repetitive or boilerplate commentary is removed.
- **FR-008**: Milestone 2 updates MUST preserve the existing separation of concerns and MUST NOT introduce architectural changes solely to satisfy documentation requirements.
- **FR-009**: Existing external-source attribution records MUST be updated or cross-referenced where necessary so they remain consistent with the revised README structure.
- **FR-010**: Existing AI prompt traceability records MUST remain discoverable from the repository documentation after the milestone changes.
- **FR-011**: The final documentation set MUST present Section V compliance as a coherent submission package rather than as isolated file updates.
- **FR-012**: The project MUST define a reviewable way to confirm Section V compliance across both code and documentation before hand-up.
- **FR-013**: The implementation plan and task execution evidence MUST include meaningful Git commit traceability checkpoints so development progression is auditable during review.

### Key Entities *(include if feature involves data)*

- **Major Directory Guide**: A supplementary README that explains the purpose, boundaries, and reviewer-facing context of a major repository directory.
- **Business Logic Docstring**: Reviewer-facing module or function documentation attached to custom project logic.
- **Boilerplate Comment Exception**: A narrowly justified explanatory comment retained only where framework or generated code has project-specific meaning that would otherwise be unclear.
- **Attribution Record**: Project documentation that captures external sources, AI/tool usage, and prompt traceability relevant to academic review.
- **Section V Compliance Review**: The documented evidence set used to verify that Milestone 2 satisfies the constitution's delivery and traceability requirements.

### Constitutional Constraints *(mandatory when applicable)*

- This milestone affects documentation and code comments/docstrings across the database, MCP server, and Flask web layers, but it does not alter the Database -> MCP Server -> Flask Web Server boundary.
- No new MCP contracts are required for this milestone; JSON-RPC and SSE behavior remain unchanged.
- This milestone does not introduce persistence changes, so SQLAlchemy confinement and workflow-schema integrity remain governed by the existing implementation baseline.
- No new environment variables are required for Section V compliance work.
- External sources, AI prompts, and Spec Kit workflow usage referenced while producing Milestone 2 materials MUST continue to be recorded in the repository documentation.
- README expectations for this feature include the top-level hand-up README plus supplementary README coverage for each major repository directory included in the final submission scope.

## Assumptions

- Major directories in current scope include, at minimum, `database`, `docs`, `mcp_server`, and `flask_web`, and any additional first-level directory in submission scope must be explicitly marked as covered or out-of-scope with rationale.
- Existing generated or framework-owned files should remain minimally commented unless the project has added non-obvious behavior that requires explanation.
- Self-explanatory trivial functions do not need verbose docstrings if their intent is already obvious and the file-level documentation provides enough context.
- Existing attribution and prompt-log files remain the authoritative traceability records and should be extended rather than replaced.
- Milestone 2 is focused on compliance and documentation quality, not feature expansion or architectural redesign.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of major directories in submission scope include a supplementary README or are explicitly justified as out of scope.
- **SC-002**: 100% of custom business-logic modules in the declared inventory for Milestone 2 scope include module-level docstrings.
- **SC-003**: 100% of custom business-logic functions in the declared inventory include function-level docstrings or a documented rationale that their signatures are already self-explanatory.
- **SC-004**: 100% of reviewed framework boilerplate files in Milestone 2 scope are free of unnecessary explanatory inline comments.
- **SC-005**: Using a timed walkthrough protocol, a reviewer can locate top-level setup guidance, directory-level architecture guidance, prompt traceability, and external-source attribution within 5 minutes using only repository documentation.
- **SC-006**: Section V compliance review produces zero unresolved contradictions between README guidance, attribution records, and the actual repository structure.
