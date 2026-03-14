# MCP Milestone Test Guide

## Purpose
This guide explains how to configure the MCP server and database, execute milestone tool verification, and manually validate table data directly.

## 1) Prerequisites
- Python virtual environment available and dependencies installed.
- Node.js installed for required inspector command.
- SQLite CLI (`sqlite3`) installed for primary manual verification.
- Optional: PostgreSQL + `psql` for equivalent query checks.

## 2) Environment Setup
1. Create `.env` from `.env.example`.
2. Set required values:

```env
DB_URL=sqlite:///./local.db
DEFAULT_ACTOR=local_dev
MCP_CONFIG_PATH=WB-Workflow-Configuration.yaml
MCP_HOST=127.0.0.1
MCP_PORT=5001
```

## 3) MCP Configuration
1. Ensure canonical config file exists at repository root:
   - `WB-Workflow-Configuration.yaml`
2. Confirm file includes:
   - server metadata,
   - required tools (`get_system_health`, `user_logon`, `user_logoff`, CRUD tools),
   - `mock_users` map for auth checks.

## 4) Start MCP Transport Profiles

### A) Required stdio profile (Inspector canonical)

```powershell
python -m mcp_server.src.server
```

### B) Required HTTP/SSE profile

```powershell
python -m mcp_server.src.api.app
```

Expected: runtime exposes JSON-RPC endpoint at `/rpc` and SSE endpoint at `/sse` on configured host/port.

## 5) Required Inspector Validation (`npx`)
Run inspector:

```powershell
npx @modelcontextprotocol/inspector
```

Use inspector to invoke and verify:
1. `get_system_health`
   - Status includes `health_status`, `health_status_description`, and error fields.
2. `user_logon`
   - Valid mock credentials -> `SUCCESS`
   - Invalid credentials -> `DENIED`
   - Missing fields -> JSON-RPC validation error
3. `user_logoff`
   - Valid username -> `SUCCESS`
4. CRUD lifecycle for in-scope tables:
   - `workflow.*`
   - `role.*`
   - `interaction.*`
   - `guard.*`
   - `interaction_component.*`

### Inspector command configuration
- Command: `python`
- Args: `-m mcp_server.src.server`

### Stdio startup troubleshooting
- If startup fails with SDK import errors, reinstall dependencies from `requirements.txt`.
- If startup fails with config errors, ensure `MCP_CONFIG_PATH=WB-Workflow-Configuration.yaml`.
- If tools are missing in Inspector, verify `tools` in `WB-Workflow-Configuration.yaml`.

## 5B) Health/Auth transport parity procedure
1. Invoke `get_system_health`, `user_logon`, and `user_logoff` over stdio.
2. Invoke equivalent requests over HTTP JSON-RPC (`POST /rpc`).
3. Confirm parity for `status` and `status_message` semantics.

## 6) End-to-end CRUD execution walkthrough
1. Create a workflow and one dependent entity (`role.create` or `interaction.create`).
2. Verify retrieval (`*.get`) and listing (`*.list`) for created records.
3. Execute update (`*.update`) and verify changed fields.
4. Execute delete (`*.delete`) and verify logical-delete semantics.

## 7) Manual Database Verification (Primary: SQLite)
After running tool operations, query data directly:

```powershell
sqlite3 local.db
.tables
SELECT WorkflowName, DeleteInd FROM Workflow LIMIT 10;
SELECT RoleName, WorkflowName, DeleteInd FROM Role LIMIT 10;
SELECT InteractionName, WorkflowName, DeleteInd FROM Interaction LIMIT 10;
SELECT GuardName, WorkflowName, DeleteInd FROM Guard LIMIT 10;
SELECT InteractionComponentName, WorkflowName, DeleteInd FROM InteractionComponent LIMIT 10;
```

Manual verification checks:
- Created records appear in expected table.
- Updated records show changed values and current-row behavior.
- Deleted rows are represented by logical-delete semantics where applicable.

## 8) Optional PostgreSQL Equivalent Commands

```sql
\dt
SELECT "WorkflowName", "DeleteInd" FROM "Workflow" LIMIT 10;
SELECT "RoleName", "WorkflowName", "DeleteInd" FROM "Role" LIMIT 10;
SELECT "InteractionName", "WorkflowName", "DeleteInd" FROM "Interaction" LIMIT 10;
SELECT "GuardName", "WorkflowName", "DeleteInd" FROM "Guard" LIMIT 10;
SELECT "InteractionComponentName", "WorkflowName", "DeleteInd" FROM "InteractionComponent" LIMIT 10;
```

## 9) Negative-Case Verification
- Missing/invalid `WB-Workflow-Configuration.yaml` path/content.
- Invalid DB URL or unavailable database.
- Missing auth fields (`username`, `password`) for `user_logon`.
- Invalid pagination values for list operations.
- Missing primary-key inputs for get/update/delete operations.

## 10) Constitution guard check
Confirm Flask remains HTTP-only:
- Flask must call MCP via HTTP contracts (`/rpc` and `/sse`) only.
- Flask must not invoke stdio transport or import MCP stdio runtime modules.

## 11) Evidence Capture
Record run details in `docs/test_evidence.md`:
- Date/time and environment,
- commands executed,
- key output snippets,
- manual SQL query results,
- open issues (if any).
