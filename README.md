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

- Architecture is fixed to Database -> MCP Server -> Flask Web Server.
- Flask must talk to MCP exclusively over HTTP using JSON-RPC and/or SSE.
- SQLAlchemy is permitted only inside the MCP server layer.
- Delivery proceeds in small chunks, starting with workflow table maintenance.
- Development history must remain visible through meaningful Git commits.

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

All external sources used during development, including AI prompts, architectural research,
and Spec Kit usage, must be cited in project documentation so the development process is
auditable.

## Temporary App Setup / Run / Test

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
MCP_BASE_URL=http://127.0.0.1:5001
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### 4) Run migrations

```powershell
alembic upgrade head
```

### 5) Start MCP server (terminal 1)

```powershell
python -m mcp_server.src.api.app
```

### 6) Start Flask web app (terminal 2)

```powershell
python -m flask_web.src.app
```

### 7) Run tests

```powershell
pytest mcp_server/tests/ -v --tb=short
```

## Logging and Error Mapping (Phase 6)

- MCP JSON-RPC endpoint now emits structured log events (`mcp.request.*`) including method, request id, and duration.
- Flask MCP client emits structured completion events (`flask.mcp.call.completed`).
- MCP JSON-RPC errors are preserved by Flask client as `MCPClientError(code, message, data)`.
- Flask app includes a centralized `MCPClientError` handler returning normalized JSON error payloads.

## Hand-up Evidence

- Prompt traceability: `docs/prompts/prompt_log.md`
- External source attribution: `docs/source_attribution.md`
- Test execution evidence: `docs/test_evidence.md`
- Section V compliance artifacts: `specs/002-milestone2-section-v/artifacts/`
