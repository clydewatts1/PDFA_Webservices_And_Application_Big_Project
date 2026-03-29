# Contracts: Refactor Database Driver from PostgreSQL to MySQL

**Feature**: 009-postgres-to-mysql-refactor  
**Date**: 2026-03-23

## MCP Tool Contracts

**No changes.** This feature performs a database driver swap at the infrastructure level.
No MCP tool signatures, JSON-RPC method names, input schemas, or output schemas are added,
removed, or modified.

All existing MCP tool contracts defined in prior features (001–008) remain in effect
without alteration. The backing MySQL engine is transparent to MCP callers.

## HTTP / SSE Contracts

**No changes.** The Quart web tier's HTTP routes and SSE event contracts are unchanged.
No new endpoints, no changed response shapes, no new streaming events.

## Environment Variable Contract

The `DB_URL` environment variable format changes. This is the only externally visible
contract change in this feature:

| Variable | Old Format | New Format |
|----------|-----------|------------|
| `DB_URL` | `postgresql+psycopg://user:password@host:5432/dbname` | `mysql+pymysql://user:password@host:3306/dbname?charset=utf8mb4` |

The `?charset=utf8mb4` suffix is **mandatory** for MySQL 8.x deployments. Omitting it
may cause silent multi-byte character corruption in SCD `String` audit columns.

The `DB_URL` variable continues to accept `sqlite:///path/to/db` for local test runs
without modification — the SQLite path is unchanged.

## No New Interfaces

This feature does not expose new APIs, command schemas, database schemas, or UI contracts.
It is purely an infrastructure change within the MCP server tier.
