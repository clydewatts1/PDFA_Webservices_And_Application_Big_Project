# MCP Transport Compatibility Contract

## Purpose
Define acceptance contracts ensuring MCP stdio and HTTP/SSE transports are both available, protocol-valid, and behaviorally equivalent for required milestone tools.

## Scope
- Canonical config: `WB-Workflow-Configuration.yaml`
- Required stdio launch: `python -m mcp_server.src.server`
- Required Inspector command: `npx @modelcontextprotocol/inspector`
- Required tools:
  - `get_system_health`
  - `user_logon`
  - `user_logoff`
  - `workflow.create|get|list|update|delete`
  - `role.create|get|list|update|delete`
  - `interaction.create|get|list|update|delete`
  - `guard.create|get|list|update|delete`
  - `interaction_component.create|get|list|update|delete`

## Contract Rules

### 1) Transport Availability Contract
- Stdio transport MUST start with python -m mcp_server.src.server and connect from Inspector.
- HTTP JSON-RPC MUST be exposed at POST /rpc.
- SSE MUST be exposed at GET /sse and return text/event-stream.

### 2) Tool Discovery Parity Contract
- Both transports MUST expose the same required tool set.
- Tool names MUST remain canonical dotted naming.

### 3) Behavioral Parity Contract
- JSON-RPC requests MUST follow envelope fields jsonrpc, id, method, optional params.
- JSON-RPC success responses MUST return result; errors MUST return error with code, message, optional data.
- SSE MUST emit ready, tool_result, error, and heartbeat events.
- SSE tool_result MUST include request_id, method, status, status_message.
- SSE ready MUST include transport (`sse`), status, status_message.
- SSE error MUST include request_id (or null), code, message, optional data.
- SSE heartbeat MUST include timestamp and status.
- For equivalent tool inputs, stdio, HTTP JSON-RPC, and SSE MUST return equivalent business-semantic outcomes (excluding transport metadata like timestamps/connection IDs).
- Deterministic transport-level failures MUST map as follows:
  - Invalid JSON-RPC envelope -> code `-32600`, message `Invalid Request`
  - Unknown method -> code `-32601`, message `Method not found`
  - Missing/invalid params object -> code `-32602`, message `Invalid params`
  - Project-specific diagnostics (for example, reason identifiers) MUST be carried in `error.data` and MUST NOT replace the transport-level standard code mapping.

### 4) Authentication Scope Contract
- Mock auth uses YAML plain-text user map for milestone testing only.
- Documentation MUST explicitly mark mock auth as non-production.

### 5) Validation Runbook Contract
Runbook MUST include:
- environment and config setup,
- stdio Inspector flow,
- HTTP/SSE verification flow,
- one complete CRUD lifecycle,
- direct SQLite verification steps,
- optional PostgreSQL equivalent steps,
- negative-path checks.

## Required Status Semantics

### Health
- `CONNECTED`, `DISCONNECTED`, `FAILED`, `INITIALIZING`, `DEAD`

### Auth
- `user_logon`: `SUCCESS`, `DENIED`, `ERROR`
- `user_logoff`: `SUCCESS`, `ERROR`

### Health/Auth parity examples
- `get_system_health` on both transports MUST expose equivalent `status`, `status_message`, and `health_status` semantics.
- `user_logon` with invalid credentials MUST produce `DENIED` on both transports.
- `user_logon` with malformed payload MUST produce `ERROR` semantics and deterministic validation error mapping.
- `user_logoff` with an active session from prior successful `user_logon` MUST produce `SUCCESS` semantics on both transports.
- `user_logoff` without an active session MUST produce `ERROR` semantics with deterministic reason details.

### CRUD
- `status`: `SUCCESS` or `ERROR`
- `status_message`: required

## Verification Output Schema

```json
{
  "check_date": "YYYY-MM-DD",
  "overall_result": "pass|fail",
  "transport_results": {
    "stdio": "pass|fail",
    "http_sse": "pass|fail",
    "parity": "pass|fail"
  },
  "required_tools_present": true,
  "evidence_paths": [],
  "open_issues": []
}
```

## Failure Conditions
- Inspector cannot connect to stdio command.
- HTTP/SSE endpoint unavailable.
- Required tool missing on either transport.
- Tool naming deviates from dotted canonical names.
- Status semantics differ between transports for equivalent requests.
- Runbook missing manual SQLite verification instructions.
