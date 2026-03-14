# Quickstart: MCP Milestone Configuration and Verification

## 1) Prepare Environment
1. Ensure Python environment is available and dependencies are installed.
2. Ensure Node.js is installed (required for `npx @modelcontextprotocol/inspector`).
3. Configure `.env` values using `env.example` as baseline.

## 2) Configure MCP Server
1. Create/update `WB-Workflow-Configuration.yaml` with:
   - MCP server name,
   - tool/resource definitions,
   - mock user map for `user_logon`.
2. Confirm server startup points to this canonical configuration file.

Set `.env` values:

```env
DB_URL=sqlite:///./local.db
MCP_CONFIG_PATH=WB-Workflow-Configuration.yaml
MCP_HOST=127.0.0.1
MCP_PORT=5001
```

## 3) Start Services
1. Start database service (SQLite local file path or PostgreSQL environment, as configured).
2. Start MCP server:

```powershell
python -m mcp_server.src.api.app
```

3. Optionally start Flask web layer if testing complete chain behavior.

## 4) Verify Tools via MCP Inspector (Required)
Run:

```powershell
npx @modelcontextprotocol/inspector
```

Use inspector to execute and verify:
1. `get_system_health` (check status fields + error behavior).
2. `user_logon` with valid and invalid credentials from YAML user map.
3. `user_logoff` for a known username.
4. One full CRUD lifecycle for each in-scope table or representative minimum per review scope.

## 5) Manual Database Verification (Required Primary Path)
Use SQLite CLI (`sqlite3`) to validate persisted outcomes directly.

Example flow:

```powershell
sqlite3 <path-to-db-file>
.tables
SELECT * FROM Workflow LIMIT 5;
SELECT * FROM Role LIMIT 5;
SELECT * FROM Interaction LIMIT 5;
SELECT * FROM Guard LIMIT 5;
SELECT * FROM InteractionComponent LIMIT 5;
```

Validate rows created/updated/deleted by tool calls match expected outcomes.

## 6) Optional PostgreSQL Equivalent Checks
For PostgreSQL environments, optionally run equivalent checks in `psql`:

```sql
\dt
SELECT * FROM "Workflow" LIMIT 5;
SELECT * FROM "Role" LIMIT 5;
SELECT * FROM "Interaction" LIMIT 5;
SELECT * FROM "Guard" LIMIT 5;
SELECT * FROM "InteractionComponent" LIMIT 5;
```

## 7) Negative-Path Verification
- Missing/malformed YAML config.
- Invalid DB connectivity.
- Invalid/missing auth payload fields.
- CRUD calls with missing primary key or invalid pagination.

## 8) Completion Criteria
Mark the feature validation complete when:
- Required MCP tool contracts are verified.
- Required inspector path was executed.
- Manual SQLite table verification was completed.
- Evidence is recorded in `docs/test_evidence.md`.
- Any open issues are documented with repro steps.
