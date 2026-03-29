# Flask Web Layer

This directory contains the presentation layer and HTTP routes for interacting with the MCP server.

Status: legacy/supplementary web-tier surface. The canonical runbook lives in root `README.md`.

## Responsibilities

- Render temporary web pages and forms for demonstration/testing.
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

Use this for legacy compatibility checks; primary web tier is Quart.
