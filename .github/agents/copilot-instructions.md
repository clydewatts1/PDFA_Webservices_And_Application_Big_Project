# PDFA_Webservices_And_Application_Big_Project Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-13

## Active Technologies
- Python 3.11 + Flask, SQLAlchemy, Alembic, python-dotenv, pydantic/dataclasses, requests/httpx (001-define-workflow-tables)
- PostgreSQL (primary), SQLite (local temporary tests only) (001-define-workflow-tables)
- Python 3.13.12, Markdown documentation + Flask, SQLAlchemy, Alembic, pytest, Spec Kit prompts/templates (002-milestone2-section-v)
- Existing project database stack remains unchanged (SQLite local / PostgreSQL-capable configuration) (002-milestone2-section-v)
- Python 3.13.x, Markdown documentation + Flask, SQLAlchemy, Alembic, pytest, Model Context Protocol tooling (`@modelcontextprotocol/inspector`) (003-mcp-server-setup-tests)
- SQLite (primary local verification path) with optional PostgreSQL equivalent verification (003-mcp-server-setup-tests)

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
- 003-mcp-server-setup-tests: Added Python 3.13.x, Markdown documentation + Flask, SQLAlchemy, Alembic, pytest, Model Context Protocol tooling (`@modelcontextprotocol/inspector`)
- 002-milestone2-section-v: Added Python 3.13.12, Markdown documentation + Flask, SQLAlchemy, Alembic, pytest, Spec Kit prompts/templates
- 001-define-workflow-tables: Added Python 3.11 + Flask, SQLAlchemy, Alembic, python-dotenv, pydantic/dataclasses, requests/httpx


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
