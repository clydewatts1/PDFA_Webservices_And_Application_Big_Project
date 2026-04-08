"""Configuration helpers for the canonical Flask web tier."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from flask_web.src.clients.mcp_client import normalize_rpc_url


@dataclass(frozen=True)
class FlaskWebConfig:
    """Environment-backed settings for the Flask web application."""

    session_secret: str
    mcp_rpc_url: str
    mcp_timeout: int
    host: str
    port: int

    @classmethod
    def from_env(cls) -> "FlaskWebConfig":
        """Build configuration from environment variables and .env."""

        load_dotenv()
        return cls(
            session_secret=os.getenv("SESSION_SECRET", "development-session-secret"),
            mcp_rpc_url=cls._resolve_mcp_rpc_url(),
            mcp_timeout=int(os.getenv("MCP_TIMEOUT_SECONDS", "30")),
            host=os.getenv("FLASK_HOST", "127.0.0.1"),
            port=int(os.getenv("FLASK_PORT", "5000")),
        )

    @staticmethod
    def _resolve_mcp_rpc_url() -> str:
        explicit = os.getenv("MCP_RPC_URL") or os.getenv("MCP_BASE_URL")
        if explicit:
            return normalize_rpc_url(explicit)

        host = os.getenv("MCP_WRAPPER_HOST") or os.getenv("MCP_HOST", "127.0.0.1")
        port = os.getenv("MCP_WRAPPER_PORT") or os.getenv("MCP_PORT", "5001")
        return normalize_rpc_url(f"http://{host}:{port}")

    def as_flask_config(self) -> dict[str, object]:
        return {
            "SECRET_KEY": self.session_secret,
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SAMESITE": "Lax",
            "WTF_CSRF_TIME_LIMIT": None,
            "MCP_RPC_URL": self.mcp_rpc_url,
            "MCP_TIMEOUT_SECONDS": self.mcp_timeout,
        }