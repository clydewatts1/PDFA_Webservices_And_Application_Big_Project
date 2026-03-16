# Data Model: MCP Server FastMCP Refactor

## Overview
This feature is a runtime/protocol refactor in the MCP tier. Persisted domain entities remain unchanged; this model captures runtime and validation entities needed for design, contracts, and tests.

## Entities

### 1) MCPRuntimeProfile
Represents how the FastMCP runtime is launched.

Fields:
- `Transport` (enum: `stdio` | `sse` | `streamable-http`, required)
- `Host` (string, optional; required for network transports)
- `Port` (integer, optional; required for network transports)
- `EnvironmentInputs` (map, required)
- `ToolScope` (set, required; in-scope family set only)

Validation rules:
- `Transport` MUST be one of the three required values.
- `Host` and `Port` required when transport is `sse` or `streamable-http`.

### 2) ToolRegistrationCatalog
Represents in-code FastMCP tool declarations for this feature.

Fields:
- `ToolName` (string, required; canonical dotted or system name)
- `Description` (string, optional)
- `Parameters` (structured map, required)
- `HandlerBinding` (reference to MCP service handler, required)

Validation rules:
- Must include all in-scope tools.
- Must exclude deferred `unit_of_work.*` and `instance.*` from required migration set.

### 3) TransportSmokeResult
Represents transport-level smoke validation on `sse` and `streamable-http`.

Fields:
- `Transport` (enum: `sse` | `streamable-http`, required)
- `StartupStatus` (enum: `pass` | `fail`, required)
- `DiscoveryStatus` (enum: `pass` | `fail`, required)
- `BasicCallStatus` (enum: `pass` | `fail`, required)
- `FailureReason` (string, optional)

### 4) StdioBehaviorValidation
Represents full behavioral validation using `stdio` transport.

Fields:
- `ToolName` (string, required)
- `InvocationStatus` (enum: `pass` | `fail`, required)
- `ResultSemanticParity` (enum: `pass` | `fail`, required)
- `TemporalAssertionStatus` (enum: `pass` | `fail`, optional by tool type)

### 5) TemporalPersistenceAssertion
Represents required temporal persistence checks after runtime refactor.

Fields:
- `EntityType` (enum: Workflow | Role | Interaction | Guard | InteractionComponent, required)
- `Operation` (enum: update | delete, required)
- `HistWriteObserved` (boolean, required)
- `SingleCurrentRowObserved` (boolean, required)
- `TransactionAtomicityObserved` (boolean, required)

Validation rules:
- All three booleans must be true for passing assertion.

## Relationships
- `MCPRuntimeProfile` determines which `ToolRegistrationCatalog` entries are exposed at runtime.
- `StdioBehaviorValidation` and `TransportSmokeResult` jointly provide coverage for required three-transport support.
- `TemporalPersistenceAssertion` links to tool invocations that mutate persisted entities.

## State Transitions
- Runtime transport state: `configured` -> `started` -> `discoverable` -> `callable`.
- Tool registration state: `declared` -> `bound` -> `discoverable` -> `validated`.