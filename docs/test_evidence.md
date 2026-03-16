# Test Execution Evidence

## Run Metadata

- Date (UTC): 2026-03-13
- Command: `.venv\Scripts\python.exe -m pytest mcp_server/tests/ -v --tb=short`
- Working directory: `C:\Users\cw171001\Projects\PDFA_Webservices_And_Application_Big_Project`

## Result Summary

- Collected tests: 122
- Passed: 122
- Failed: 0
- Errors: 0
- Warnings: 240 (deprecation warnings, mostly `datetime.utcnow()`)
- Duration: 8.63s

## Phase Coverage

This run includes test suites for:
- Workflow (Phase 3)
- Dependent entities (Phase 4)
- Instance creation/replication (Phase 5)

## Raw Tail Output

```text
====================== 122 passed, 240 warnings in 8.63s ======================
```

## MCP Milestone 003 Verification Evidence

- Configuration file used: `WB-Workflow-Configuration.yaml`
- Required inspector command: `npx @modelcontextprotocol/inspector`
- Manual database verification path: SQLite CLI (`sqlite3`) with optional PostgreSQL (`psql`) equivalents.

### Evidence Capture Template

- Date/time:
- Environment (`DB_URL`, `MCP_CONFIG_PATH`):
- Evidence Files:
    - setup_start, inspector_connected_at, full_flow_completed_at, elapsed_setup_minutes, elapsed_total_minutes.

- Inspector checks completed:
	- get_system_health:
	- user_logon (success/denied/error):
	- user_logoff:
	- CRUD checks (workflow/role/interaction/guard/interaction_component):
- Manual SQLite query outputs:
- Optional PostgreSQL query outputs:
- Open issues:

## MCP Milestone 004 Verification Evidence

- Canonical stdio launch command: `python -m mcp_server.src.server`
- HTTP JSON-RPC endpoint: `POST /rpc`
- SSE endpoint: `GET /sse` (`text/event-stream`)
- Required Inspector command: `npx @modelcontextprotocol/inspector`

### US1 Connectivity Evidence Template

- Date/time:
- Environment (`DB_URL`, `MCP_CONFIG_PATH`, `MCP_HOST`, `MCP_PORT`):
- Inspector launch config (`python -m mcp_server.src.server`):
- Tool discovery result (required tool families present):
- Stdio startup troubleshooting notes (if any):

### US2 Health/Auth Parity Evidence Template

- `get_system_health` stdio status + message:
- `get_system_health` HTTP status + message:
- `user_logon` stdio and HTTP outcomes (success/denied/error):
- `user_logoff` stdio and HTTP outcomes (with active session):
- `user_logoff` stdio and HTTP outcomes (without active session):
- JSON-RPC transport error-code mapping checks (`-32600`, `-32601`, `-32602`):
- `error.data` diagnostics parity checks:
- Parity verification result (`status`, `status_message`):

### US3 CRUD + Data Verification Evidence Template

- CRUD sequence executed (`workflow/role/interaction/guard/interaction_component`):
- SQLite verification command outputs:
- Optional PostgreSQL verification outputs:
- Transport parity result for CRUD calls:

### Timed Reviewer Dry-Run (SC-001 / SC-005)

- setup_start: `2026-03-14T16:41:58.3481939+00:00`
- inspector_connected_at: `2026-03-14T16:42:22.9454964+00:00`
- full_flow_completed_at: `2026-03-14T16:42:26.7916799+00:00`
- elapsed_setup_minutes: `0.41`
- elapsed_total_minutes: `0.474`
- SC-001 pass/fail (`<= 5 minutes`): `PASS`
- SC-005 pass/fail (`<= 15 minutes`): `PASS`

### Transport parity smoke evidence (2026-03-14)

- Inspector tool discovery command:
	- `npx @modelcontextprotocol/inspector --config specs/004-mcp-stdio-compat/inspector.local.json --server local-stdio --cli --method tools/list`
- Inspector stdio health command:
	- `npx @modelcontextprotocol/inspector --config specs/004-mcp-stdio-compat/inspector.local.json --server local-stdio --cli --method tools/call --tool-name get_system_health --tool-arg 'kwargs={}'`
- HTTP JSON-RPC health smoke command:
	- `python -c "... create_runtime_app(); client.post('/rpc', method=get_system_health) ..."`

Observed parity result:
- stdio status: `SUCCESS`
- http status: `SUCCESS`
- stdio status_message: `Health check completed`
- http status_message: `Health check completed`
- parity outcome: pass

### Additional regression verification (2026-03-15)

- Command: `pytest mcp_server/tests/ -q`
- Exit code: `0`
- Result: full MCP server suite passed

### Phase 6 Closeout Evidence (Feature 004)

- Task `T047` (Inspector-based parity smoke run): `PASS`
	- Evidence source: transport parity smoke block above (Inspector stdio + HTTP JSON-RPC health parity)
	- Outcome: equivalent `status`/`status_message` observed for stdio and HTTP
- Task `T048` (Timed first-time reviewer dry-run): `PASS`
	- Evidence source: timed dry-run block above
	- Outcome: setup time `0.41` minutes and total flow `0.474` minutes, both within required thresholds
- Protocol/error-session alignment checkpoints for closeout:
	- JSON-RPC transport standard codes (`-32600`, `-32601`, `-32602`) validated in current contract behavior and regression tests
	- Active-session-dependent `user_logoff` semantics verified by updated parity/test flow

## Feature 005 Manual Transport Validation Evidence

- Date: 2026-03-16
- Branch: `005-fastmcp-refactor`
- Environment: `DB_URL=sqlite:///./local.db`, `DEFAULT_ACTOR=local_dev`, `MCP_HOST=127.0.0.1`, `MCP_PORT=5001`

### Transport Startup Verification

| Transport | Command | Startup result |
|---|---|---|
| `stdio` | `python -m mcp_server.src.server --transport stdio` | PASS |
| `sse` | `python -m mcp_server.src.server --transport sse --host 127.0.0.1 --port 5001` | PASS |
| `streamable-http` | `python -m mcp_server.src.server --transport http --host 127.0.0.1 --port 5001` | PASS |

### MCP Inspector Connection Verification

| Transport | Inspector URL | Connection result |
|---|---|---|
| `sse` | `http://127.0.0.1:5001/sse` | PASS |
| `streamable-http` | `http://127.0.0.1:5001/mcp` | PASS |

Note: `GET /` and `OPTIONS /` return `404 Not Found` for both network transports — this is expected FastMCP behaviour; the root path is not a valid MCP endpoint.

### Tool Discovery and Basic Call

- `get_system_health` discoverable and callable on all three transports: PASS
- In-scope tool families present (`workflow.*`, `role.*`, `interaction.*`, `guard.*`, `interaction_component.*`): PASS
- Deferred families absent (`unit_of_work.*`, `instance.*`): PASS

### Overall Feature 005 Manual Validation Result: PASS
