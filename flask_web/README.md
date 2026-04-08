# Flask Web Layer

This directory contains the presentation layer and HTTP routes for interacting with the MCP server.

Status: primary web-tier surface. The canonical runbook lives in root `README.md`.

## Responsibilities

- Render the canonical WSGI-compatible web pages and forms for workflow management.
- Call MCP JSON-RPC methods through the MCP client wrapper.
- Normalize MCP client errors into user-visible responses.

## Boundary Notes

- Flask does not access database objects directly.
- Flask does not import SQLAlchemy or persistence models.
- All business operations are delegated to MCP over HTTP.

## Subdirectories

- `src/routes/` view handlers and form endpoints
- `src/clients/` MCP transport client
- `src/app.py` Flask app entrypoint

## Startup (Supplementary)

```powershell
python -m flask_web.src.app
```

Required env vars for the canonical path:

- `SESSION_SECRET`
- `MCP_RPC_URL`
- `MCP_TIMEOUT_SECONDS`
- `FLASK_HOST`
- `FLASK_PORT`

Use this as the canonical web tier for local and deployment validation.
