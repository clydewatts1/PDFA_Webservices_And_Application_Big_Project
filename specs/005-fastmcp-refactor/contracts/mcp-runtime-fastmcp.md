# Contract: FastMCP Runtime Migration (MCP Tier)

## Scope
Defines required runtime and protocol contracts for migrating MCP-tier runtime implementation from custom Flask/JSON-RPC/SSE handling to official FastMCP behavior.

## Required Transports
- `stdio` (full tool-behavior validation transport)
- `sse` (transport smoke validation transport)
- `streamable-http` (transport smoke validation transport)

All three transports are mandatory.

## In-Scope Tool Contract
Required migrated tools:
- `get_system_health`
- `user_logon`
- `user_logoff`
- `workflow.*`
- `role.*`
- `interaction.*`
- `guard.*`
- `interaction_component.*`

Deferred from required migration scope:
- `unit_of_work.*`
- `instance.*`

## Runtime Behavior Contract
1. MCP-tier runtime is FastMCP-based.
2. MCP-tier runtime does not depend on custom Flask/Quart request routing or queue-based stream relays.
3. Tool metadata and registration are defined in Python code for in-scope tools.
4. Transport selection is parameterized and deterministic.

## Protocol Contract
1. `sse` and `streamable-http` behavior follows FastMCP-native transport semantics.
2. Legacy custom MCP-tier `/rpc` and custom SSE envelope behavior are out of required compatibility scope.
3. Business semantics for in-scope tools remain equivalent across required transports.

## Testing Contract
1. `stdio` receives full in-scope tool-behavior validation.
2. `sse` receives startup + discovery + basic-call smoke validation.
3. `streamable-http` receives startup + discovery + basic-call smoke validation.
4. MCP-tier temporal update/delete tests continue asserting:
   - write to matching `_Hist`
   - single current row per business key
   - transaction-level atomicity

## Boundary Contract
1. Feature scope is MCP-tier only.
2. Flask-side integration changes are not required for this increment.
3. SQLAlchemy and persistence orchestration remain MCP-tier only.