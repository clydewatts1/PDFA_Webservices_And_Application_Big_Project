# Database Layer

This directory contains migration and schema-management assets for the PDFA temporary application.

## Responsibilities

- Own database migration configuration and migration scripts.
- Persist current/history table structures required by workflow and instance lifecycle handling.
- Remain framework-managed through Alembic; runtime business logic is not implemented here.

## Boundary Notes

- The database layer stores state only.
- MCP server owns SQLAlchemy models and transaction orchestration.
- Flask web layer never accesses database objects directly.

## Related Evidence

- Section V artifacts: `specs/002-milestone2-section-v/artifacts/`
- Source attribution: `docs/source_attribution.md`
