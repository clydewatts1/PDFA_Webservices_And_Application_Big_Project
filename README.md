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

_Github Co _Pilot_

Using speckit and Specification Driven Development methodology the big project will be developed.

_Google Gemini_

Google gemini is used as a brainstorm tool and high level architect. 

_SpecKit_

SpecKit is a utility consisting of a number of prompts which drives the specification life cycle.

Constitution -> Project Specification -> Technical Specification -> Implementation Plan

https://github.com/github/spec-kit

__Installation__

specify init .

## Constitutional Baseline

The project is governed by the constitution in .specify/memory/constitution.md.

- Architecture is fixed to Database -> MCP Server -> Quart Web Server.
- Quart must talk to MCP exclusively over HTTP using JSON-RPC and/or SSE.
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
- `quart_web/README.md`

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
DB_URL=sqlite:///./local.db
DEFAULT_ACTOR=local_dev
MCP_SERVER_URL=http://127.0.0.1:5001/sse
SESSION_SECRET=replace-with-a-random-secret-value
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

MCP workflow configuration file:

- `WB-Workflow-Configuration.yaml`

### 4) Run migrations

```powershell
python -m alembic -c database/alembic.ini upgrade head
```

### 5) Start MCP runtime (network mode)

Use `http` transport for network/web-tier communication (JSON-RPC + SSE endpoints):

```powershell
python -m mcp_server.src.server --transport http --host 127.0.0.1 --port 5001
```

### 6) Optional: start MCP in `stdio` mode (inspector/local tool use)

```powershell
python -m mcp_server.src.server --transport stdio
```

### 7) Start Quart web tier (primary web tier)

```powershell
python -m quart_web.src.app
```

Quart default URL: `http://127.0.0.1:5002`

### 8) Optional: start Flask web tier (legacy/supplementary)

```powershell
python -m flask_web.src.app
```

### 9) Run tests

MCP server tests:

```powershell
pytest mcp_server/tests/ -v --tb=short
```

Quart tests:

```powershell
pytest quart_web/tests/ -v --tb=short
```

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

### Testing SSE

__0. Run Server__

```
$env:DB_URL="sqlite:///./local.db"
$env:MCP_CONFIG_PATH="WB-Workflow-Configuration.yaml"
$env:MCP_HOST="127.0.0.1"
$env:MCP_PORT="5001"
python -m mcp_server.src.api.app
```

__1. Open SSE stream__

```
curl.exe -N http://127.0.0.1:5001/sse
```
]__2. Trigger RPC__

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




