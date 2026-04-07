"""Environment-backed configuration for the Quart web tier."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from dotenv import load_dotenv

from quart_web.src.clients.errors import MCPConfigurationError


def _read_bool(env_name: str, default: bool) -> bool:
    raw = os.getenv(env_name)
    if raw is None:
        return default
    value = raw.strip().lower()
    return value in {"1", "true", "yes", "on"}


def _resolve_mcp_server_url() -> str:
    transport = (os.getenv("MCP_TRANSPORT") or "sse").strip().lower()
    endpoint = "/mcp" if transport in {"http", "streamable-http"} else "/sse"

    explicit_url = (os.getenv("MCP_SERVER_URL") or "").strip()
    if explicit_url:
        parsed = urlparse(explicit_url)
        if parsed.path.strip("/"):
            return explicit_url
        return f"{explicit_url.rstrip('/')}{endpoint}"

    base_url = (os.getenv("MCP_BASE_URL") or "").strip().rstrip("/")
    if base_url:
        return f"{base_url}{endpoint}"

    host = (os.getenv("MCP_HOST") or "127.0.0.1").strip() or "127.0.0.1"
    port = (os.getenv("MCP_PORT") or "5001").strip() or "5001"
    return f"http://{host}:{port}{endpoint}"


@dataclass(frozen=True)
class QuartWebConfig:
    """Typed config values loaded from environment variables."""

    mcp_server_url: str
    session_secret: str
    mcp_timeout: float
    session_cookie_secure: bool
    session_cookie_httponly: bool
    session_cookie_samesite: str
    session_cookie_name: str

    @classmethod
    def from_env(cls) -> "QuartWebConfig":
        load_dotenv()

        mcp_server_url = _resolve_mcp_server_url()
        session_secret = os.getenv("SESSION_SECRET", "").strip()
        if not session_secret:
            raise MCPConfigurationError("SESSION_SECRET must be set for Quart session cookies")

        mcp_timeout = float(os.getenv("MCP_TIMEOUT", "10"))
        if mcp_timeout <= 0:
            raise MCPConfigurationError("MCP_TIMEOUT must be greater than 0")

        session_cookie_samesite = os.getenv("SESSION_COOKIE_SAMESITE", "Lax").strip() or "Lax"
        session_cookie_name = os.getenv("SESSION_COOKIE_NAME", "pdfa_session").strip() or "pdfa_session"

        return cls(
            mcp_server_url=mcp_server_url,
            session_secret=session_secret,
            mcp_timeout=mcp_timeout,
            session_cookie_secure=_read_bool("SESSION_COOKIE_SECURE", False),
            session_cookie_httponly=_read_bool("SESSION_COOKIE_HTTPONLY", True),
            session_cookie_samesite=session_cookie_samesite,
            session_cookie_name=session_cookie_name,
        )

    def as_quart_config(self) -> dict[str, Any]:
        """Return a dict suitable for Quart app.config.update(...)."""
        return {
            "SECRET_KEY": self.session_secret,
            "MCP_SERVER_URL": self.mcp_server_url,
            "MCP_TIMEOUT": self.mcp_timeout,
            "SESSION_COOKIE_NAME": self.session_cookie_name,
            "SESSION_COOKIE_SECURE": self.session_cookie_secure,
            "SESSION_COOKIE_HTTPONLY": self.session_cookie_httponly,
            "SESSION_COOKIE_SAMESITE": self.session_cookie_samesite,
            "WTF_CSRF_ENABLED": True,
        }
