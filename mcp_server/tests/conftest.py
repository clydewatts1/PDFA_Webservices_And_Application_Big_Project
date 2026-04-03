"""Shared FastMCP runtime test harness helpers."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from typing import Any

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from mcp_server.src.api.app import create_app, create_runtime_app
from mcp_server.src.models.base import Base


MYSQL_TEST_DB_ENV_VARS = ("MCP_TEST_DB_URL", "TEST_DB_URL", "DB_URL")


def _resolve_mysql_test_db_url() -> str:
    for env_var in MYSQL_TEST_DB_ENV_VARS:
        candidate = (os.getenv(env_var) or "").strip()
        if candidate:
            if candidate.startswith("mysql"):
                return candidate
            pytest.skip(
                f"{env_var} must point to a MySQL database for contract/integration validation; got: {candidate.split(':', 1)[0]}"
            )

    pytest.skip("Set MCP_TEST_DB_URL to a MySQL database URL before running MCP contract/integration suites")


def _reset_schema(engine: Engine) -> None:
    Base.metadata.drop_all(engine, checkfirst=True)
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    Base.metadata.create_all(engine, checkfirst=True)


def build_test_client(
    session_factory: sessionmaker[Session],
    *handler_groups: dict[str, Callable[[dict[str, Any]], dict[str, Any]]],
):
    app = create_app()
    for handlers in handler_groups:
        for method, handler in handlers.items():
            app.register_jsonrpc_handler(method, handler)  # type: ignore[attr-defined]

    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def runtime_server():
    """Build the shared FastMCP runtime used by transport-aware tests."""

    return create_runtime_app()


@pytest.fixture
def mysql_test_db_url() -> str:
    """Return the MySQL URL used for MCP contract and integration validation."""

    return _resolve_mysql_test_db_url()


@pytest.fixture
def mysql_test_engine(mysql_test_db_url: str) -> Iterator[Engine]:
    """Provide a reusable MySQL engine for validation tests."""

    engine = create_engine(mysql_test_db_url, pool_pre_ping=True, pool_recycle=3600)
    yield engine
    engine.dispose()


@pytest.fixture
def mysql_session_factory(mysql_test_engine: Engine) -> Iterator[sessionmaker[Session]]:
    """Reset the schema and return a session factory bound to the MySQL validation database."""

    _reset_schema(mysql_test_engine)
    yield sessionmaker(bind=mysql_test_engine, autocommit=False, autoflush=False, expire_on_commit=False)
    Base.metadata.drop_all(mysql_test_engine, checkfirst=True)
    with mysql_test_engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))


@pytest.fixture
def runtime_tool_names(runtime_server) -> list[str]:
    """Return the registered canonical tool names for discovery assertions."""

    return sorted(tool.name for tool in runtime_server.list_tools())


@pytest.fixture
def network_runtime_settings(runtime_server) -> Iterator[tuple[str, int]]:
    """Expose the network runtime bind settings for SSE/HTTP smoke tests."""

    yield runtime_server.settings.host, runtime_server.settings.port


def normalize_tool_result(payload: dict) -> dict:
    """Strip transport metadata and keep only business result contract fields."""

    return {
        "status": payload.get("status"),
        "status_message": payload.get("status_message"),
        "data": payload.get("data"),
    }
