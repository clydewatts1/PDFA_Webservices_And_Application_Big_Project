# PDFA_Webservices_And_Application_Big_Project
25-26: 8640 -- WEB SERVICES AND APPLICATIONS - BIG PROJECT



## Introduction

### Development Environment


### IDE
- Microsoft Visual Code 
- Google Antigravity

### LLM

- Development - Github Co pilot
- Design / Architect - Google Gemini Pro
- speckit

_Google Gemini_

Google gemini is used as a brainstorm tool and high level architect.  Gemini is used to generate the high level design and architecture of the system.  It is also used to generate the constitution which governs the project. The constitution is the source of truth for the project and all development must adhere to it. The constituion is a living document and can be updated as the project evolves, but all changes must be made through the Spec Kit workflow and must be approved by the project stakeholders(/speckit/constitution)

[Constitution](.specify/memory/constitution.md)

_Spec Kit_

Spec Kit is used to manage the development process and ensure that all development is done in a structured and organized manner.  Spec Kit is used to create and manage the specifications for each feature and to track the progress of each feature through the development process.  Spec Kit is also used to ensure that all development is done in accordance with the constitution and to provide traceability for all development activities.

_Github Co _Pilot_

Github Co Pilot is used as a development assistant to help with code generation and to provide suggestions for code improvements.  Co Pilot is used to generate code snippets and to provide suggestions for code structure and organization.  Co Pilot is also used to help with debugging and to provide suggestions for code optimization.

Prompts saving in `docs/prompts/prompt_log.md` for traceability.



__Installation__

specify init .

## Constitutional Baseline

The project is governed by the constitution in .specify/memory/constitution.md.

- Architecture is fixed to Database -> MCP Server -> Flask Web Server.
- Flask must talk to MCP exclusively over synchronous HTTP POST using JSON-RPC.
- SQLAlchemy is permitted only inside the MCP server layer.
- Persisted domain tables must maintain symmetric current and `_Hist` schemas, with only
	the current version in the primary table and prior versions tracked in `_Hist` by the MCP server.
- Delivery proceeds in small chunks, starting with workflow table maintenance.
- Development history must remain visible through meaningful Git commits.
- Every feature must start via Spec Kit workflow, and `spec.md` must be partitioned into
  MCP (Logic), Web-Tier (Routes), and Page (UI) sections before coding begins.

## Documentation and Source Attribution

The final hand-up must include a comprehensive README that explains setup, architecture,
environment variables, and the staged delivery process.

Major directories must also include supplementary README files that explain their local
architecture and responsibilities in the overall three-tier design.

Current supplementary README coverage:
- `database/README.md`
- `docs/README.md`
- `mcp_server/README.md`
- `flask_web/README.md`
- `quart_web/README.md` (legacy historical tier notes only)

All external sources used during development, including AI prompts, architectural research,
and Spec Kit usage, must be cited in project documentation so the development process is
auditable.

## Canonical Windows Setup / Run / Test Flow

This section is the canonical runbook for local reviewer execution.
Tier READMEs are supplementary and must remain aligned with this section.

### 1) Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
pip install -r requirements-dev.txt
```

### 3) Configure environment

Create `.env` at repository root:

```env
DB_URL=mysql+pymysql://user:password@127.0.0.1:3306/pdfa_workflow?charset=utf8mb4
DEFAULT_ACTOR=local_dev
MCP_CONFIG_PATH=WB-Workflow-Configuration.yaml
MCP_BASE_URL=http://127.0.0.1:5001
MCP_SERVER_URL=http://127.0.0.1:5001/rpc
SESSION_SECRET=replace-with-a-random-secret-value
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
CUTOVER_WINDOW_START_UTC=2026-04-03T12:00:00Z
ROLLBACK_WINDOW_HOURS=24
CUTOVER_DECISION_OWNER=on-call-reviewer
```

MCP workflow configuration file:

- `WB-Workflow-Configuration.yaml`

### 4) Run migrations

```powershell
python -m alembic -c database/alembic.ini upgrade head
```

### 5) Start MCP wrapper (canonical WSGI path)

Use the dedicated Flask WSGI wrapper for synchronous web-tier JSON-RPC POST communication:

```powershell
python -m mcp_server.src.wsgi_app
```

### 6) Optional: start MCP in `stdio` mode (inspector/local tool use)

```powershell
python -m mcp_server.src.server --transport stdio
```

### 7) Start Flask web tier (primary web tier)

```powershell
python -m flask_web.src.app
```

Flask default URL: `http://127.0.0.1:5000`

### 8) Optional: start Quart web tier (legacy/manual only)

```powershell
python -m quart_web.src.app
```

### 9) Run tests

MCP contract and integration sign-off on MySQL:

```powershell
pytest mcp_server/tests/contract mcp_server/tests/integration -v --tb=short
```

Flask tests:

```powershell
pytest flask_web/tests/ -v --tb=short
```

Quart legacy tests (manual/non-canonical):

```powershell
pytest quart_web/tests/ -v --tb=short
```

SQLite remains acceptable only for existing unit-only coverage. Contract and integration sign-off must use a MySQL `DB_URL`.

Full suite:

```powershell
pytest -v --tb=short
```

## Traceability Pointers

- Canonical coverage matrix: `docs/constitution/coverage-matrix.md`
- Source attribution: `docs/source_attribution.md`
- Test and validation evidence: `docs/test_evidence.md`
- Prompt/process trace log: `docs/prompts/prompt_log.md`
- Feature artifacts: `specs/008-constitution-docs/`

## Logging and Error Mapping (Phase 6)

- MCP JSON-RPC endpoint now emits structured log events (`mcp.request.*`) including method, request id, and duration.
- Flask MCP client emits structured completion events (`flask.mcp.call.completed`).
- MCP JSON-RPC errors are preserved by Flask client as `MCPClientError(code, message, data)`.
- Canonical Flask env vars: `SESSION_SECRET`, `MCP_RPC_URL`, `MCP_TIMEOUT_SECONDS`, `FLASK_HOST`, `FLASK_PORT`.
- Flask app includes a centralized `MCPClientError` handler returning normalized JSON error payloads.

## Hand-up Evidence

- Prompt traceability: `docs/prompts/prompt_log.md`
- External source attribution: `docs/source_attribution.md`
- Test execution evidence: `docs/test_evidence.md`
- Constitution coverage matrix: `docs/constitution/coverage-matrix.md`
- MCP milestone test runbook: `docs/mcp_milestone_test_guide.md`
- MCP transport compatibility quickstart: `specs/004-mcp-stdio-compat/quickstart.md`
- Section V compliance artifacts: `specs/002-milestone2-section-v/artifacts/`


## Appdendix

### Testing MCP HTTP JSON-RPC

__0. Run Server__

```
$env:DB_URL="mysql+pymysql://user:password@127.0.0.1:3306/pdfa_workflow?charset=utf8mb4"
$env:MCP_CONFIG_PATH="WB-Workflow-Configuration.yaml"
$env:MCP_HOST="127.0.0.1"
$env:MCP_PORT="5001"
python -m mcp_server.src.server --transport http --host 127.0.0.1 --port 5001
```

__1. Trigger RPC__

```
$body = @{
  jsonrpc = "2.0"
  id = 1
  method = "get_system_health"
  params = @{}
} | ConvertTo-Json -Depth 5

Invoke-RestMethod `
  -Uri "http://127.0.0.1:5001/rpc" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 10
```

## Speckit Milestones

The project was done using speckit and Specification Driven Development methodology.  The following milestones were completed in order:

The driver behind breaking the project down into a number of milestones is to decompose the project into smaller, reviewable logical increments. That keeps the LLM focused on a bounded slice of work and allows continuous review and course correction. The initial requirement was DB -> MCP -> Flask. A later shift to Quart improved async experimentation, but the architecture has now been returned to Flask so the web tier remains fully compatible with PythonAnywhere's WSGI hosting constraints. Another issue was that the project is supposed to be database agnostic via SQLAlchemy; early stages used SQLite to simplify local table and MCP logic development before the project converged on the required MySQL runtime.



The following milestones were completed in order:
- [Milestone 1: Workflow Table Maintenance](specs/001-milestone1-workflow-table-maintenance/)
- [Milestone 2: Section V Compliance](specs/002-milestone2-section-v/)
- [Milestone 3: MCP Server Setup Tests](specs/003-milestone3-mcp-server-setup-tests/)
- [Milestone 4: MCP stdio Transport Compatibility](specs/004-mcp-stdio-compat/)
- [Milestone 5: Fast MCP Refactor](specs/005-milestone5-fast-mcp-refactor/)
- [Milestone 6: Web Tier Integration](specs/006-milestone6-web-tier-integration/)
- [Milestone 7: Quart Web Tier Setup (legacy)](specs/007-milestone7-quart-web-tier-setup/)
- [Milestone 8: Constitution Docs](specs/008-constitution-docs/)
- [Milestone 9: Postgres to mySQL Migration](specs/09-milestone9-postgres-to-mysql-migration/)
  
## References

[Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)  

[MCP Documentation](https://mcp.palletsprojects.com/en/latest/) 

[Pytest Documentation](https://docs.pytest.org/en/stable/) 

[Pymysql Documentation](https://pymysql.readthedocs.io/en/latest/) 

[SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/) 

[Flask Documentation](https://flask.palletsprojects.com/en/latest/)

[Spec Kit Documentation](https://github.com/github/spec-kit)

[Google Gemini Pro](https://ai.google.dev/gemini)