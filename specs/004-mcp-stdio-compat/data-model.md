# Data Model: MCP Stdio Inspector Compatibility

## Overview
This feature defines planning-level entities needed to validate MCP protocol transport compatibility, tool contract parity, and reviewer verification evidence. No new persistence schema entities are required.

## Entities

### 1) MCPServerRuntimeProfile
Describes transport/runtime launch configuration used for validation.

- Identifier: `ProfileName`
- Fields:
  - `ProfileName` (string, required)
  - `Transport` (enum: stdio|http_sse, required)
  - `LaunchCommand` (string, required)
  - `ConfigPath` (string, required; expected `WB-Workflow-Configuration.yaml`)
  - `EnvRequirements` (map, required)
- Validation rules:
  - Stdio profile launch command must be `python -m mcp_server.src.server`.
  - Runtime config path must resolve to canonical filename.

### 2) InspectorVerificationSession
Captures one reviewer validation session through Inspector.

- Identifier: `SessionId`
- Fields:
  - `SessionId` (string, required)
  - `TransportUsed` (enum: stdio|http_sse, required)
  - `ConnectionStatus` (enum: connected|failed, required)
  - `DiscoveredTools` (list[string], required)
  - `ExecutedCalls` (list[object], required)
  - `OpenIssues` (list[string], optional)
- Validation rules:
  - Required tool set must be present for successful session.
  - Failed connection must record reason and evidence.

### 3) HealthAuthToolResult
Represents normalized result for health/auth tool operations.

- Identifier: `ToolName + RequestId + Timestamp`
- Fields:
  - `ToolName` (enum: get_system_health|user_logon|user_logoff)
  - `status` (string, required)
  - `status_message` (string, required)
  - `payload` (object, optional)
  - `error_detail` (object, optional)
- Validation rules:
  - `get_system_health` must support CONNECTED/DISCONNECTED/FAILED/INITIALIZING/DEAD semantics.
  - `user_logon` must support SUCCESS/DENIED/ERROR semantics.
  - `user_logoff` must support SUCCESS/ERROR semantics.

### 4) CrudToolResult
Represents normalized result for dotted-name CRUD tools.

- Identifier: `ToolName + RequestId`
- Fields:
  - `ToolName` (string, required; dotted form e.g. `workflow.create`)
  - `TableScope` (enum: Workflow|Role|Interaction|Guard|InteractionComponent)
  - `Operation` (enum: create|get|list|update|delete)
  - `status` (enum: SUCCESS|ERROR, required)
  - `status_message` (string, required)
  - `payload` (object|list, optional)
- Validation rules:
  - `get/update/delete` require business/primary key inputs.
  - `list` supports optional `limit/offset` with invalid values rejected.

### 5) ManualDatabaseVerificationStep
Represents a documented manual SQL evidence step.

- Identifier: `StepNumber`
- Fields:
  - `StepNumber` (integer, required)
  - `TransportContext` (enum: stdio|http_sse|both)
  - `QueryDialect` (enum: sqlite3|psql)
  - `QueryText` (string, required)
  - `ExpectedOutcome` (string, required)
  - `EvidenceRef` (string, optional)
- Validation rules:
  - SQLite verification is mandatory primary path.
  - PostgreSQL verification remains optional equivalent path.

## Relationships
- `MCPServerRuntimeProfile` is referenced by `InspectorVerificationSession` to define expected launch/transport behavior.
- `InspectorVerificationSession` produces `HealthAuthToolResult` and `CrudToolResult` evidence.
- `ManualDatabaseVerificationStep` validates data outcomes corresponding to executed CRUD tool results.

## State Transitions

### InspectorVerificationSession
- `failed` when connection cannot be established or required tools are missing.
- `connected` when transport handshake succeeds and required tool set is discoverable.

### HealthAuthToolResult
- Health status transitions according to runtime DB state (`INITIALIZING` -> `CONNECTED` or failure states).
- Auth transitions from `ERROR` (invalid input) / `DENIED` (credential mismatch) to `SUCCESS` (valid login/logoff scenario).

### CrudToolResult
- `SUCCESS` for valid in-scope operation and payload handling.
- `ERROR` for missing required identifiers, invalid pagination, or invalid operation context.
