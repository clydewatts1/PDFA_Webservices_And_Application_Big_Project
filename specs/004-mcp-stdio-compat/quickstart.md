# Quickstart: MCP Stdio + HTTP/SSE Compatibility Verification

## 1) Prerequisites
1. Python virtual environment active and dependencies installed.
2. Node.js available for `npx @modelcontextprotocol/inspector`.
3. SQLite CLI (`sqlite3`) installed for primary manual verification.
4. Optional: PostgreSQL + `psql` for equivalent query checks.

## 2) Environment and Config Setup
1. Create `.env` from `.env.example`.
2. Ensure canonical config file exists: `WB-Workflow-Configuration.yaml`.
3. Set required environment values:

```env
DB_URL=sqlite:///./local.db
DEFAULT_ACTOR=local_dev
MCP_CONFIG_PATH=WB-Workflow-Configuration.yaml
MCP_HOST=127.0.0.1
MCP_PORT=5001
```

## 3) Start MCP Transport Profiles

### A) Required stdio profile (Inspector canonical)

```powershell
python -m mcp_server.src.server
```

### B) Required HTTP/SSE profile

```powershell
python -m mcp_server.src.api.app
```

## 4) Inspector Validation Flow (Required)

```powershell
npx @modelcontextprotocol/inspector
```

Configure server command to:
- Command: `python`
- Args: `-m mcp_server.src.server`

Validate tool discovery includes:
- `get_system_health`
- `user_logon`
- `user_logoff`
- `workflow.*`, `role.*`, `interaction.*`, `guard.*`, `interaction_component.*`

## 5) Transport Parity Checks (Required)
1. Execute identical health/auth/CRUD requests through stdio profile.
2. Execute equivalent requests through HTTP/SSE profile (`POST /rpc`, `GET /sse`).
3. Confirm equivalent status and status-message semantics across both transports.

## 6) Manual Database Verification (Required Primary Path)
After CRUD operations, verify persisted outcomes directly:

```powershell
sqlite3 local.db
.tables
SELECT WorkflowName, DeleteInd FROM Workflow LIMIT 10;
SELECT RoleName, WorkflowName, DeleteInd FROM Role LIMIT 10;
SELECT InteractionName, WorkflowName, DeleteInd FROM Interaction LIMIT 10;
SELECT GuardName, WorkflowName, DeleteInd FROM Guard LIMIT 10;
SELECT InteractionComponentName, WorkflowName, DeleteInd FROM InteractionComponent LIMIT 10;
```

## 7) Optional PostgreSQL Equivalent Checks

```sql
\dt
SELECT "WorkflowName", "DeleteInd" FROM "Workflow" LIMIT 10;
SELECT "RoleName", "WorkflowName", "DeleteInd" FROM "Role" LIMIT 10;
SELECT "InteractionName", "WorkflowName", "DeleteInd" FROM "Interaction" LIMIT 10;
SELECT "GuardName", "WorkflowName", "DeleteInd" FROM "Guard" LIMIT 10;
SELECT "InteractionComponentName", "WorkflowName", "DeleteInd" FROM "InteractionComponent" LIMIT 10;
```

## 8) Negative-Path Verification
- Missing/malformed `WB-Workflow-Configuration.yaml`.
- Invalid DB URL or unavailable database.
- Invalid/missing `user_logon` payload fields.
- Missing key values for get/update/delete.
- Invalid `limit`/`offset` values for list operations.
- Inspector stdio startup failures or transport mismatch.

## 9) Completion Criteria
Validation is complete when:
- stdio transport is Inspector-connectable,
- HTTP/SSE transport is reachable,
- required tool set is present on both transports,
- status semantics are equivalent across transports,
- manual SQLite verification confirms expected data outcomes,
- evidence is recorded in project test-evidence documentation.
