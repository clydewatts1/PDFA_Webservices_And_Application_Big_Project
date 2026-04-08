# PDFA_Webservices_And_Application_Big_Project Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-13

## Active Technologies
- Python 3.11 + Flask, SQLAlchemy, Alembic, python-dotenv, pydantic/dataclasses, requests/httpx (001-define-workflow-tables)
- PostgreSQL (primary), SQLite (local temporary tests only) (001-define-workflow-tables)
- Python 3.13.12, Markdown documentation + Flask, SQLAlchemy, Alembic, pytest, Spec Kit prompts/templates (002-milestone2-section-v)
- Existing project database stack remains unchanged (SQLite local / PostgreSQL-capable configuration) (002-milestone2-section-v)
- Python 3.13.x, Markdown documentation + Flask, SQLAlchemy, Alembic, pytest, Model Context Protocol tooling (`@modelcontextprotocol/inspector`) (003-mcp-server-setup-tests)
- SQLite (primary local verification path) with optional PostgreSQL equivalent verification (003-mcp-server-setup-tests)
- Python 3.13.x, Markdown documentation + Flask, SQLAlchemy, Alembic, pytest, python-dotenv, PyYAML, MCP Python SDK, Model Context Protocol Inspector (`@modelcontextprotocol/inspector`) (004-mcp-stdio-compat)
- SQLite (primary local verification) with PostgreSQL-capable equivalents (004-mcp-stdio-compat)
- Python 3.13.x + `mcp` Python SDK (`FastMCP`), SQLAlchemy, Alembic, pytest, python-dotenv, PyYAML (non-tool config), Flask (web tier only) (005-fastmcp-refactor)
- SQLite/PostgreSQL through SQLAlchemy in MCP tier (005-fastmcp-refactor)
- Python 3.13 (from `.venv/Scripts/python.exe`) + Flask, official Python MCP SDK (`mcp` package), Jinja2, Bootstrap 5 CSS (006-web-tier-integration)
- N/A (all persistence delegated to MCP server tier via synchronous HTTP POST JSON-RPC) (006-web-tier-integration)
- Markdown + PowerShell command examples, Python 3.13 runtime references for reproducibility checks + Spec Kit workflow artifacts, repository README set, constitution, pytest command surface, MCP/Flask documented runtime commands (008-constitution-docs)
- Filesystem markdown artifacts in repository (`docs/`, root `README.md`, `specs/008-constitution-docs/`, `docs/constitution/`) (008-constitution-docs)
- Python 3.11+ + SQLAlchemy 2.0+, Alembic 1.13+, PyMySQL 1.1+ (new), FastMCP 1.x (009-postgres-to-mysql-refactor)
- MySQL 8.x (production/integration), SQLite (automated tests — unchanged) (009-postgres-to-mysql-refactor)
- Python 3.11+ + SQLAlchemy 2.x, Alembic 1.13+, FastMCP 1.x, PyMySQL 1.1+ (010-postgres-mysql-refactor)
- MySQL 8.x (runtime + contract/integration validation), PostgreSQL (legacy pre-cutover retention only), SQLite (unit-only where already applicable) (010-postgres-mysql-refactor)
- Python 3.13.12 + Flask 3.x, Flask-WTF, WTForms, requests, SQLAlchemy 2.x, Alembic 1.13+, python-dotenv, PyYAML, pytest, existing `mcp` package for non-canonical MCP metadata/runtime code (011-flask-wsgi-migration)
- MySQL 8.x via SQLAlchemy in the MCP tier; no new persistence schema for this feature (011-flask-wsgi-migration)

- [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION] + [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION] (001-define-workflow-tables)

## Project Structure

```text
backend/
frontend/
tests/
```

## Commands

cd src; pytest; ruff check .

## Code Style

[e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]: Follow standard conventions

## Recent Changes
- 011-flask-wsgi-migration: Added Python 3.13.12 + Flask 3.x, Flask-WTF, WTForms, requests, SQLAlchemy 2.x, Alembic 1.13+, python-dotenv, PyYAML, pytest, existing `mcp` package for non-canonical MCP metadata/runtime code
- 010-postgres-mysql-refactor: Added Python 3.11+ + SQLAlchemy 2.x, Alembic 1.13+, FastMCP 1.x, PyMySQL 1.1+
- 009-postgres-to-mysql-refactor: Added Python 3.11+ + SQLAlchemy 2.0+, Alembic 1.13+, PyMySQL 1.1+ (new), FastMCP 1.x


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
