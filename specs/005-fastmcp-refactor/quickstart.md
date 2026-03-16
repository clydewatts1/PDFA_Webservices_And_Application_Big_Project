# Quickstart: FastMCP Runtime Refactor Validation

## 1) Prerequisites
1. Python virtual environment activated.
2. Dependencies installed from `requirements-dev.txt`.
3. Database migrated and reachable via `DB_URL`.

## 2) Environment Setup
Set required runtime variables:

```powershell
$env:DB_URL="sqlite:///./local.db"
$env:DEFAULT_ACTOR="local_dev"
$env:MCP_HOST="127.0.0.1"
$env:MCP_PORT="5001"
```

## 3) Start FastMCP Runtime by Transport

### A) `stdio`

```powershell
python -m mcp_server.src.server --transport stdio
```

### B) `sse`

```powershell
python -m mcp_server.src.server --transport sse --host 127.0.0.1 --port 5001
```

For MCP Inspector, connect to `http://127.0.0.1:5001/sse`.
Do not point Inspector at `http://127.0.0.1:5001/`; FastMCP does not expose a root route for SSE, so `GET /` and `OPTIONS /` return `404 Not Found` even when the runtime is healthy.

### C) `streamable-http`

```powershell
python -m mcp_server.src.server --transport http --host 127.0.0.1 --port 5001
```

For MCP Inspector, connect to `http://127.0.0.1:5001/mcp`.
Do not point Inspector at `http://127.0.0.1:5001/`; FastMCP mounts streamable HTTP at `/mcp`, not at the root path.

## 4) Validate Tool Scope
Confirm discoverable in-scope tools include:
- `get_system_health`
- `user_logon`
- `user_logoff`
- `workflow.*`, `role.*`, `interaction.*`, `guard.*`, `interaction_component.*`

Confirm deferred families are not required in this feature:
- `unit_of_work.*`
- `instance.*`

## 5) Transport Validation Strategy

### A) Full behavior validation (`stdio`)
Run the in-scope tool behavior suite on `stdio`.

### B) Smoke validation (`sse`, `streamable-http`)
For each transport, validate:
1. runtime startup
2. tool discovery
3. one basic in-scope tool call (`get_system_health`)

## 6) Temporal Assertions (MCP Tests)
Run MCP-tier tests ensuring updates/deletes still:
1. write prior state to `_Hist`
2. preserve one current primary row
3. commit atomically

## 7) Expected Refactor Outcomes
1. MCP-tier runtime is FastMCP-based across all three required transports.
2. Legacy custom MCP-tier Flask routing/envelope logic is removed.
3. In-scope tool names and business semantics are preserved.