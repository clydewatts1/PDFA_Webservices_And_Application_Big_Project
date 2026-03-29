# MCP Server Layer

This directory contains the MCP JSON-RPC service, SQLAlchemy-backed persistence access, and domain business logic.

## Responsibilities

- Own business logic and persistence orchestration.
- Enforce current/history lifecycle semantics for workflow entities and instances.
- Expose capabilities through JSON-RPC handlers consumed by Flask.

## Boundary Notes

- SQLAlchemy usage is confined to this layer.
- Flask communicates only over HTTP JSON-RPC and does not import MCP persistence internals.
- Database remains a state store and does not host service logic.

## Startup Commands

- Canonical network mode (for Quart/web-tier integration):
	- `python -m mcp_server.src.server --transport http --host 127.0.0.1 --port 5001`
- Optional inspector/local mode:
	- `python -m mcp_server.src.server --transport stdio`

Root canonical runbook remains in `README.md`.

## Subdirectories

- `src/api/` JSON-RPC app and handlers
- `src/services/` domain logic
- `src/models/` ORM models
- `src/db/` session factory and connectivity
- `tests/` unit, contract, and integration tests
