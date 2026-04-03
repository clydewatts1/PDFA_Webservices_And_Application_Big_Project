"""SQLAlchemy session factory — shared between MCP server and tests."""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _build_engine_options(url: str) -> dict[str, object]:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}

    options: dict[str, object] = {"pool_pre_ping": True}
    if url.startswith("mysql"):
        options.update({"pool_recycle": 3600, "pool_reset_on_return": "rollback"})
    return options


def make_session_factory(db_url: str | None = None) -> sessionmaker[Session]:
    """Return a sessionmaker bound to *db_url* (falls back to DB_URL env var)."""

    url = db_url or os.environ["DB_URL"]
    engine = create_engine(url, **_build_engine_options(url))
    return sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)
