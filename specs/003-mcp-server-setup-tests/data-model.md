# Data Model: MCP Server Configuration and Test Guide

## Overview
This feature introduces planning-level entities for MCP configuration, tool response consistency, and reviewer verification workflows. It does not require new persistence schema entities.

## Entities

### 1) MCPConfigurationDocument
Represents canonical YAML configuration for MCP server setup.

- Identifier: `ConfigPath`
- Fields:
  - `ConfigPath` (string, required; expected `WB-Workflow-Configuration.yaml`)
  - `ServerName` (string, required)
  - `ToolDefinitions` (list, required)
  - `MockUserMap` (map, required for `user_logon`)
  - `ResourceDefinitions` (list, optional)
- Validation rules:
  - File name must match canonical naming requirement.
  - Tool definitions must include health/auth/table CRUD tool entries.

### 2) HealthToolResult
Represents output contract for `get_system_health`.

- Identifier: `RequestId + Timestamp`
- Fields:
  - `health_status` (enum: CONNECTED|DISCONNECTED|FAILED|INITIALIZING|DEAD, required)
  - `health_status_description` (string, required)
  - `health_status_error` (string, optional)
  - `health_status_error_detail` (string, optional)
- Validation rules:
  - Error fields required when status is `FAILED` or `DEAD`.

### 3) AuthToolResult
Represents output contract for `user_logon` and `user_logoff`.

- Identifier: `ToolName + Username + Timestamp`
- Fields:
  - `status` (enum: SUCCESS|DENIED|ERROR for logon; SUCCESS|ERROR for logoff)
  - `error_message` (string, optional)
  - `username` (string, required)
- Validation rules:
  - Missing/invalid input must produce `ERROR`.
  - Credential mismatch must produce `DENIED` for logon.

### 4) TableCrudResult
Represents normalized output contract for CRUD tool operations.

- Identifier: `ToolName + TableName + RequestId`
- Fields:
  - `table_name` (enum: Workflow|Role|Interaction|Guard|InteractionComponent)
  - `operation` (enum: create|get|list|update|delete)
  - `status` (enum: SUCCESS|ERROR)
  - `status_message` (string, required)
  - `payload` (object or list, optional)
- Validation rules:
  - `get`, `update`, and `delete` require primary key input.
  - `list` accepts optional `limit` and `offset`.

### 5) VerificationRunbookStep
Represents ordered steps in the testing document.

- Identifier: `StepNumber`
- Fields:
  - `StepNumber` (integer, required)
  - `Category` (enum: setup|tool-test|npx-verification|sql-verification|negative-test)
  - `Command` (string, required)
  - `ExpectedOutcome` (string, required)
  - `EvidenceType` (enum: response-output|inspector-output|sql-row-check)
- Validation rules:
  - Must include mandatory inspector command step.
  - Must include manual SQLite query verification step.

## Relationships
- `MCPConfigurationDocument` defines `ToolDefinitions` that produce `HealthToolResult`, `AuthToolResult`, and `TableCrudResult`.
- `VerificationRunbookStep` references all result entities via expected outcomes/evidence links.

## State Transitions

### AuthToolResult
- `ERROR` for malformed input.
- `DENIED` for valid format + credential mismatch (logon only).
- `SUCCESS` for credential match (logon) or valid logoff execution.

### HealthToolResult
- `INITIALIZING` -> `CONNECTED` when DB connectivity is confirmed.
- `CONNECTED` -> `DISCONNECTED`/`FAILED`/`DEAD` under connection failures.

### TableCrudResult
- `SUCCESS` for valid operation/inputs.
- `ERROR` for unknown table, missing primary key, or invalid pagination.
