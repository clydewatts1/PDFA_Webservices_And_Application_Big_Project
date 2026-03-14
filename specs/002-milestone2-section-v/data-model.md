# Data Model: Milestone 2 Section V Alignment

## Overview
This increment introduces a compliance-oriented data model for planning and review artifacts. It does not change runtime persistence schema.

## Entities

### 1) MajorDirectoryGuide
Represents required supplementary documentation for a major repository directory.

- Identifier: `DirectoryPath`
- Fields:
  - `DirectoryPath` (string, required, unique in compliance scope)
  - `ReadmePath` (string, required)
  - `PurposeSummary` (string, required)
  - `ArchitectureBoundaryNotes` (string, required)
  - `LastReviewedDate` (date, required)
- Validation rules:
  - `ReadmePath` must resolve inside the same directory or a documented local docs path.
  - `PurposeSummary` must describe local responsibility and relation to the three-tier architecture.

### 2) DocstringRemediationItem
Represents a custom business-logic code item requiring docstring verification or remediation.

- Identifier: `FilePath + SymbolName`
- Fields:
  - `FilePath` (string, required)
  - `SymbolName` (string, required)
  - `SymbolType` (enum: module/function/method, required)
  - `DocstringStatus` (enum: present/missing/not-required, required)
  - `ReviewRationale` (string, optional; required when `DocstringStatus=not-required`)
  - `LastReviewedBy` (string, required)
- Validation rules:
  - `missing` status requires planned remediation task.
  - `not-required` must include explicit rationale.

### 3) BoilerplateCommentReviewItem
Tracks policy compliance for framework-generated or framework-standard boilerplate files.

- Identifier: `FilePath`
- Fields:
  - `FilePath` (string, required, unique)
  - `BoilerplateType` (enum: alembic/framework_scaffold/other, required)
  - `UnnecessaryInlineCommentsFound` (boolean, required)
  - `ExceptionJustification` (string, optional; required if comments are retained)
  - `Disposition` (enum: remove_comments/retain_with_justification/no_action, required)
- Validation rules:
  - If `Disposition=retain_with_justification`, `ExceptionJustification` must be non-empty.

### 4) AttributionLink
Represents required traceability references from README artifacts to canonical attribution/prompt records.

- Identifier: `SourceReadmePath + TargetEvidencePath`
- Fields:
  - `SourceReadmePath` (string, required)
  - `TargetEvidencePath` (string, required)
  - `LinkPurpose` (enum: ai_assistance/external_sources/prompt_traceability, required)
  - `Verified` (boolean, required)
- Validation rules:
  - `TargetEvidencePath` must be one of the canonical evidence docs for this project.
  - All README layers in scope must provide discoverable links to attribution evidence.

### 5) SectionVComplianceCheckResult
Captures final milestone verification outcomes.

- Identifier: `CheckName + CheckDate`
- Fields:
  - `CheckName` (string, required)
  - `CheckDate` (date, required)
  - `Result` (enum: pass/fail, required)
  - `EvidencePaths` (list of strings, required)
  - `OpenIssues` (list of strings, optional)
- Validation rules:
  - `Result=pass` requires `OpenIssues` empty.
  - `EvidencePaths` must point to existing repository artifacts.

## Relationships
- `MajorDirectoryGuide` 1 -> N `AttributionLink`
- `SectionVComplianceCheckResult` references N `MajorDirectoryGuide` entries and N `DocstringRemediationItem` entries through evidence paths.
- `BoilerplateCommentReviewItem` and `DocstringRemediationItem` together compose code-level compliance evidence.

## State Transitions

### DocstringRemediationItem
`missing` -> `present` after code update and review.
`missing` -> `not-required` only with documented rationale and reviewer approval.

### BoilerplateCommentReviewItem
`UnnecessaryInlineCommentsFound=true` -> `Disposition=remove_comments` after cleanup.
`UnnecessaryInlineCommentsFound=true` -> `Disposition=retain_with_justification` when exception applies.

### SectionVComplianceCheckResult
`fail` -> `pass` once all open issues are resolved and evidence links validate.
