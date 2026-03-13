"""SQLAlchemy session factory — shared between MCP server and tests."""
from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def make_session_factory(db_url: str | None = None) -> sessionmaker[Session]:
    """Return a sessionmaker bound to *db_url* (falls back to DB_URL env var)."""
    url = db_url or os.environ["DB_URL"]
    engine = create_engine(url, connect_args={"check_same_thread": False} if "sqlite" in url else {})
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)
