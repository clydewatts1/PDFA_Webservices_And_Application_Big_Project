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
- Inspector checks completed:
	- get_system_health:
	- user_logon (success/denied/error):
	- user_logoff:
	- CRUD checks (workflow/role/interaction/guard/interaction_component):
- Manual SQLite query outputs:
- Optional PostgreSQL query outputs:
- Open issues:
