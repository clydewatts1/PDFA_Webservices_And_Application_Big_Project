# quart_web — Async Quart Web Tier

The `quart_web/` package is the **presentation tier** of the PDFA three-tier application.
It uses [Quart](https://quart.palletsprojects.com/) (Flask-compatible async framework) and communicates exclusively with the MCP server via HTTP/SSE.

This README is supplementary to the root canonical runbook in `README.md`.

---

## Architecture Position

```
Database  →  MCP Server (port 5001/SSE)  →  Quart Web Tier (port 5002)
```

No direct database access. All persistence is delegated to the MCP server via
`MCP_SERVER_URL`.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `MCP_SERVER_URL` | Yes | `http://127.0.0.1:5001/sse` | Full SSE URL of the MCP backend |
| `SESSION_SECRET` | Yes | *(none)* | Secret key for Quart session cookie signing |

Create a `.env` file at the repository root (or export variables directly):

```env
MCP_SERVER_URL=http://127.0.0.1:5001/sse
SESSION_SECRET=replace-with-a-random-secret-value
```

---

## Running the Quart Tier

### Prerequisites

Install dependencies from the project root:

```powershell
pip install -r requirements.txt
```

### Start the server

```powershell
python -m quart_web.src.app
```

Or using the Quart CLI (set `QUART_APP` first):

```powershell
$env:QUART_APP = "quart_web.src.app:create_app"
$env:QUART_ENV = "development"
quart run --port 5002
```

The server listens on `http://127.0.0.1:5002` by default.

---

## Running Tests

```powershell
pytest quart_web/tests/ -v --tb=short
```

## Route Runbook

### Authentication and Session

- `GET /` — health landing page (`get_system_health`)
- `GET /login` / `POST /login` — authenticate via `user_logon`
- `POST /logout` — terminate session via `user_logoff`

### Workflow Context and Navigation

- `GET /dashboard` / `POST /dashboard` — list/select active workflow (`workflow.list`)
- `GET /entities` — contextual entity dashboard (requires `active_workflow_name`)

### Entity Management

- Workflows: `/workflows`, `/workflows/new`, `/workflows/<name>/edit`, `/workflows/<name>/delete`
- Roles: `/roles`, `/roles/new`, `/roles/<name>/edit`, `/roles/<name>/delete`
- Interactions: `/interactions`, `/interactions/new`, `/interactions/<name>/edit`, `/interactions/<name>/delete`
- Guards: `/guards`, `/guards/new`, `/guards/<name>/edit`, `/guards/<name>/delete`
- Interaction Components: `/interaction-components`, `/interaction-components/new`, `/interaction-components/<name>/edit`, `/interaction-components/<name>/delete`

All POST handlers are server-side rendered form submissions with MCP-backed validation/error re-render behavior.

---

## Directory Structure

```
quart_web/
├── __init__.py
├── README.md
├── src/
│   ├── __init__.py
│   ├── app.py              # Application factory (create_app)
│   ├── config.py           # Environment configuration (Phase 2)
│   ├── clients/
│   │   ├── mcp_client.py   # MCPClientWrapper SSE singleton (Phase 2)
│   │   └── errors.py       # Web-tier MCP exception classes (Phase 2)
│   ├── routes/             # Blueprint route handlers (Phases 2–4)
│   ├── forms/              # WTForms form classes (Phases 3–4)
│   └── templates/          # Jinja2 HTML templates (Phases 3–4)
└── tests/
    └── unit/               # Async route unit tests (Phases 3–4)
```

---

## Related Documentation

- [Parent spec: 006-web-tier-integration](../specs/006-web-tier-integration/spec.md)
- [Implementation plan](../specs/006-web-tier-integration/plan.md)
- [MCP server README](../mcp_server/README.md)
