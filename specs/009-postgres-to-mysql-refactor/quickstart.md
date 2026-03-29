# Quickstart: Refactor Database Driver from PostgreSQL to MySQL

**Feature**: 009-postgres-to-mysql-refactor

This guide walks through setting up and verifying the MySQL-backed configuration
introduced in this feature. After following these steps the MCP server will be connected
to MySQL and all existing automated tests will continue to pass via SQLite in-process.

---

## 1) Prerequisites

- Python 3.11+ with virtual environment created and activated
- MySQL 8.x instance reachable from your development machine
- MySQL database created with `utf8mb4` charset:

```sql
CREATE DATABASE pdfa_workflow
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

- A MySQL user with `CREATE`, `ALTER`, `DROP`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`
  privileges on `pdfa_workflow`

---

## 2) Install Dependencies

```bash
pip install -r requirements.txt
```

This installs `PyMySQL>=1.1,<2.0` (new in this feature) alongside all existing
dependencies. No system packages or native compilation are required.

---

## 3) Environment Variables

Create or update `.env` in the repository root:

```env
DB_URL=mysql+pymysql://user:password@localhost:3306/pdfa_workflow?charset=utf8mb4
DEFAULT_ACTOR=local_dev
MCP_SERVER_URL=http://127.0.0.1:5001
```

> **Important**: The `?charset=utf8mb4` suffix is **mandatory**. Omitting it may cause
> silent character encoding corruption in SCD audit columns (`InsertUserName`,
> `UpdateUserName`, etc.).

Load the environment:

```bash
# Windows (PowerShell)
.\.env

# Linux / macOS
export $(cat .env | xargs)
```

---

## 4) Run Database Migrations

```bash
alembic upgrade head
```

Expected output:

```
INFO  [alembic.runtime.migration] Context impl MySQLImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_current_history_tables, create current and history tables
```

Verify the tables were created (using `mysql` CLI):

```sql
USE pdfa_workflow;
SHOW TABLES;
```

Expected: 14 tables — `Workflow`, `Workflow_Hist`, `Role`, `Role_Hist`, `Interaction`,
`Interaction_Hist`, `Guard`, `Guard_Hist`, `InteractionComponent`,
`InteractionComponent_Hist`, `UnitOfWork`, `UnitOfWork_Hist`, `Instance`, `Instance_Hist`.

---

## 5) Start the MCP Server

```bash
python -m mcp_server.src.server --transport http --host 127.0.0.1 --port 5001
```

Expected console output (no error lines):

```
INFO  Starting MCP server on http://127.0.0.1:5001
```

---

## 6) Verify MySQL Database Health

Call the `get_system_health` MCP tool. Using the MCP Inspector or the sandbox HTTP client:

```bash
python sandbox/connect_to_mcp.py
```

Expected response includes:

```json
{
  "health_status": "ok",
  "db_url_configured": true
}
```

If you see `"health_status_error": "db_url_missing"` verify the `DB_URL` environment
variable is set in the active shell.

---

## 7) Run the Automated Test Suite

The test suite uses SQLite in-process and is unaffected by the MySQL driver change:

```bash
pytest mcp_server/tests/ -v
```

All previously passing tests must pass without modification or test fixture changes.

---

## 8) Manual MySQL Verification Queries

Confirm SCD columns and charset are correct:

```sql
-- Verify utf8mb4 charset on a representative table
SHOW CREATE TABLE Workflow\G

-- Confirm control columns exist
DESCRIBE Workflow;

-- Confirm AUTO_INCREMENT is active on the id column
SELECT AUTO_INCREMENT FROM information_schema.tables
WHERE table_schema = 'pdfa_workflow' AND table_name = 'Workflow';
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `Access denied for user` | Insufficient MySQL privileges | Grant `CREATE, ALTER, DROP, INSERT, SELECT, UPDATE, DELETE` on `pdfa_workflow.*` |
| `Can't connect to MySQL server` | Wrong host/port or MySQL not running | Check `DB_URL` host and port; verify `mysql` service is running |
| `MySQL server has gone away` | Stale connection (should not happen with pool_pre_ping=True) | Confirm `mcp_server/src/db/session.py` includes `pool_pre_ping=True` |
| `Incorrect string value` | Missing `?charset=utf8mb4` in DB_URL | Add `?charset=utf8mb4` to end of `DB_URL` value |
| `Authentication plugin error` | MySQL 8 auth with older PyMySQL | Ensure `PyMySQL>=1.1` is installed (`pip show PyMySQL`) |
