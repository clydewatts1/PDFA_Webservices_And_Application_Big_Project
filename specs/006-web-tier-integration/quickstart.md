# Quickstart: Web Tier Integration

**Feature**: `006-web-tier-integration`  
**Stack**: Quart + MCP Python SDK (SSE) | Python 3.13 | Bootstrap 5 | flask-wtf

---

## Prerequisites

- Python 3.13 (in `.venv/`)
- MCP server running and reachable at `MCP_SERVER_URL`
- Database applied (Alembic migrations up to date)
- `.env` file at project root (see env vars below)

---

## Directory Structure

After implementation, `quart_web/` will look like:

```
quart_web/
├── __init__.py
└── src/
    ├── __init__.py
    ├── app.py                  # create_app() factory
    ├── clients/
    │   ├── __init__.py
    │   └── mcp_client.py       # MCPClientWrapper
    ├── routes/
    │   ├── __init__.py
    │   ├── auth.py             # GET/POST /login, POST /logout
    │   ├── workspace.py        # GET/POST /dashboard, GET /entities
    │   ├── workflow.py         # /workflows CRUD
    │   ├── role.py             # /roles CRUD
    │   ├── interaction.py      # /interactions CRUD
    │   ├── guard.py            # /guards CRUD
    │   └── interaction_component.py  # /interaction-components CRUD
    ├── forms/
    │   ├── __init__.py
    │   ├── auth.py             # LoginForm, WorkspaceSelectForm
    │   ├── workflow.py         # WorkflowForm
    │   ├── role.py             # RoleForm
    │   ├── interaction.py      # InteractionForm
    │   ├── guard.py            # GuardForm
    │   └── interaction_component.py  # InteractionComponentForm
    └── templates/
        ├── base.html           # Bootstrap 5 layout, nav, flash messages
        ├── auth/
        │   ├── login.html
        │   └── logout.html
        ├── workspace/
        │   ├── dashboard.html  # Workflow selection
        │   └── entities.html   # Entity navigation
        └── entities/
            ├── list.html       # Shared list template (entity_type variable)
            ├── form.html       # Shared create/edit form template
            └── delete_confirm.html
```

---

## Environment Variables

Create `.env` at project root (or set in shell):

```bash
# Required
SESSION_SECRET=<32+ bytes random string, e.g. output of: python -c "import secrets; print(secrets.token_hex(32))">
MCP_SERVER_URL=http://127.0.0.1:5001/sse

# Optional
MCP_TIMEOUT=10
QUART_ENV=development
QUART_DEBUG=1
```

Default mock credentials are configured in `WB-Workflow-Configuration.yaml`:

- `admin` / `password123`
- `reviewer` / `reviewer_pass`
- `test_user` / `test_pass`

---

## Installation

```bash
# Install project dependencies (adds quart, flask-wtf to existing requirements.txt)
.venv/Scripts/pip install quart flask-wtf

# Or if requirements.txt is updated:
.venv/Scripts/pip install -r requirements.txt
```

---

## Running the Application

### 1. Start the MCP Server (in a separate terminal)

```bash
.venv/Scripts/python -m mcp_server.src.server --transport sse
# Server listens at http://127.0.0.1:5001/sse by default
```

### 2. Start the Quart Web App

```bash
Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
    $name, $value = $_ -split '=', 2
    Set-Item -Path "Env:$name" -Value $value
}
echo $env:SESSION_SECRET
echo $env:MCP_SERVER_URL
python -m quart_web.src.app
.venv/Scripts/python -m quart_web.src.app
# App listens at http://127.0.0.1:5002 by default
```

Or with the Quart CLI:

```bash
QUART_APP=quart_web.src.app:create_app .venv/Scripts/quart run --port 5002
```

---

## Smoke Test Checklist (Manual)

After starting both servers:

1. **Landing health (healthy)**: Open `http://localhost:5002/` — page shows `MCP Healthy` badge and enabled login button
2. **Landing health (unavailable fallback)**: Stop MCP server, refresh `/` — page shows `MCP Unavailable` and disabled login button
3. **Login**: Navigate to `/login`, enter `admin` / `password123` → redirected to `/dashboard`
4. **Workspace selection**: `/dashboard` shows workflow dropdown → select one → redirected to `/entities`
5. **Role list**: Navigate to `/roles` → list of roles filtered by selected workflow
6. **Create role**: `/roles/new` → fill form → submit → see new record in list
7. **Edit role**: `/roles/<name>/edit` → change a field → submit → updated record
8. **Delete role**: POST to `/roles/<name>/delete` → record removed from list
9. **Logout**: POST to `/logout` → redirected to landing page, session cleared

---

## Running Tests

```bash
# All unit + integration tests for the web tier
.venv/Scripts/pytest quart_web/tests/ -v

# With coverage
.venv/Scripts/pytest quart_web/tests/ --cov=quart_web --cov-report=term-missing

# Fast: unit tests only (no MCP server needed)
.venv/Scripts/pytest quart_web/tests/unit/ -v
```

### Test Fixtures Pattern

```python
# quart_web/tests/conftest.py
import pytest
from unittest.mock import AsyncMock
from quart_web.src.app import create_app

@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
        "MCP_SERVER_URL": "http://mock-mcp/sse",
    })
    return app

@pytest.fixture
def mock_mcp_client(app):
    mock = AsyncMock()
    app.mcp_client = mock
    return mock
```

---

## Configuration Reference

| Config Key | Source | Development | Production |
|------------|--------|-------------|------------|
| `SECRET_KEY` | `SESSION_SECRET` env | Any string | Random 32+ bytes |
| `MCP_SERVER_URL` | Env var | `http://127.0.0.1:5001/sse` | Full SSE URL |
| `MCP_TIMEOUT` | Env var (float) | `10` | `10` |
| `WTF_CSRF_ENABLED` | Config | `True` | `True` |
| `SESSION_COOKIE_SECURE` | Config | `False` | `True` |
| `SESSION_COOKIE_SAMESITE` | Config | `"Strict"` | `"Strict"` |
| `QUART_ENV` | Env var | `development` | `production` |

---

## Key Implementation Notes

1. **MCP Client initialization**: Created in `create_app()`, stored as `app.mcp_client`. Connects lazily on first `call_tool()` call.
2. **CSRF protection**: `CSRFProtect(app)` initialized in `create_app()`. Every POST form must include `{{ form.csrf_token }}`.
3. **WorkflowName in entity routes**: Always read from `session["active_workflow_name"]`, never from form POST data.
4. **actor parameter**: Always pass `session["user_id"]` as the `actor` argument to mutating MCP tools.
5. **Double-submit prevention**: All submit buttons include `onclick="this.disabled=true; this.form.submit()"`.
6. **Temporal columns**: Never render `EffFromDateTime`, `EffToDateTime`, `DeleteInd`, `InsertUserName`, `UpdateUserName` in forms or list views.
7. **Error handling**: `MCPTimeoutError` → 504 page; `MCPConnectionError` → 503 page; entity tool errors → re-render form with error message.

---

## Validated Command Flow (Phase 10)

1. Install dependencies:
    - `.venv/Scripts/pip install -r requirements.txt`
2. Run focused unit tests:
    - `.venv/Scripts/python.exe -m pytest quart_web/tests/unit/ -q`
    - Expected output pattern: `... [100%]` and all tests pass
3. Run integration happy path:
    - `.venv/Scripts/python.exe -m pytest quart_web/tests/integration/test_role_crud_e2e.py -q`
    - Expected output pattern: `. [100%]`
4. Run full web-tier test matrix:
    - `.venv/Scripts/python.exe -m pytest quart_web/tests/ -q`
    - Expected output pattern: all tests pass with no failures
