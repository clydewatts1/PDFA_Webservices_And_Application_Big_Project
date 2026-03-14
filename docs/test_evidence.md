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
- `user_logoff` stdio and HTTP outcomes:
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
