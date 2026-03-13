# Quickstart: Temporary Three-Tier Application

## 1) Prerequisites
- Python 3.11+
- A reachable PostgreSQL instance (or SQLite for local temporary runs)
- Virtual environment created and activated

## 2) Environment Variables
Create `.env` in repository root:

```env
DB_URL=postgresql+psycopg://user:password@localhost:5432/pdfa_workflow
DEFAULT_ACTOR=local_dev
```

Current phase scope:
- Required now: database variables needed to create/migrate tables (`DB_URL`, plus actor/default metadata if used by migration scripts).
- Deferred to later phases: MCP/Flask host/port/base URL variables for runtime service integration.

## 3) Install Dependencies
```bash
pip install -r requirements.txt
```

## 4) Run Database Migrations
```bash
alembic upgrade head
```

## 5) Start MCP Server
```bash
python -m mcp_server.src.api.app
```

## 6) Start Flask Web App
```bash
python -m flask_web.src.app
```

## 7) Run Tests
```bash
pytest mcp_server/tests/unit -q
pytest mcp_server/tests/contract -q
pytest mcp_server/tests/integration -q
```

## 8) Smoke Test Flow
1. Create a workflow via Flask UI/API.
2. Update workflow and verify history snapshot behavior.
3. Create Role/Interaction/Guard/InteractionComponent records.
4. Create Instance and verify instance-scoped replication in fixed tables.

## Notes
- JSON-RPC is mandatory in this increment; SSE can be added later.
- SQLAlchemy usage must remain confined to the MCP tier.
- For schema-only phase execution, only steps 1-4 are mandatory.
