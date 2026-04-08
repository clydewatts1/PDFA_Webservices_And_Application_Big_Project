# quart_web — Legacy Async Quart Web Tier

The `quart_web/` package is a legacy presentation-tier experiment retained for reference.
It is not the canonical deployment target after the constitution's return to Flask for WSGI-compatible hosting.

This README is supplementary to the root canonical runbook in `README.md`.

---

## Architecture Position

```
Database  →  MCP Server  →  Flask Web Tier (canonical)
```

No direct database access. All persistence is delegated to the MCP server. For active setup and runtime guidance, use `flask_web/README.md` and the root `README.md`.

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

## Legacy Runtime Notes

### Prerequisites

Install dependencies from the project root:

```powershell
pip install -r requirements.txt
```

### Legacy start command

```powershell
python -m quart_web.src.app
```

Or using the Quart CLI (set `QUART_APP` first):

```powershell
$env:QUART_APP = "quart_web.src.app:create_app"
$env:QUART_ENV = "development"
quart run --port 5002
```

This surface is non-canonical, depends on legacy async transport assumptions, and may drift from the constitution over time.

---

## Running Tests

```powershell
pytest quart_web/tests/ -v --tb=short
```

Run these only as explicit legacy checks. They are not part of the default repository test path.

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
