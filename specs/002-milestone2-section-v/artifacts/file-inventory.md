# In-Scope File Inventory

## Code Files (Section V Docstring/Comment Review)

### MCP Server
- mcp_server/src/services/workflow_service.py
- mcp_server/src/services/dependent_service.py
- mcp_server/src/services/instance_service.py
- mcp_server/src/services/validation.py
- mcp_server/src/api/handlers/workflow_handlers.py
- mcp_server/src/api/handlers/dependent_handlers.py
- mcp_server/src/api/handlers/instance_handlers.py
- mcp_server/src/api/app.py
- mcp_server/src/db/session.py

### Flask Web
- flask_web/src/clients/mcp_client.py
- flask_web/src/routes/workflow.py
- flask_web/src/routes/dependent.py
- flask_web/src/routes/instance.py
- flask_web/src/app.py

### Framework Boilerplate
- database/migrations/env.py
- database/migrations/versions/0001_current_history_tables.py

## Documentation Files
- README.md
- docs/source_attribution.md
- docs/prompts/prompt_log.md
- database/README.md
- docs/README.md
- mcp_server/README.md
- flask_web/README.md

## Inventory Coverage Rule
All files listed above must be reviewed and marked complete in the corresponding audit artifacts before final compliance sign-off.
