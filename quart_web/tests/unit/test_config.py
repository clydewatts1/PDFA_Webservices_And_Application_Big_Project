"""Unit tests for Quart environment-backed configuration."""

from __future__ import annotations

from quart_web.src.config import QuartWebConfig


def test_from_env_uses_explicit_mcp_server_url(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "secret")
    monkeypatch.setenv("MCP_SERVER_URL", "http://127.0.0.1:5001/sse")
    monkeypatch.setenv("MCP_BASE_URL", "http://127.0.0.1:5001")

    config = QuartWebConfig.from_env()

    assert config.mcp_server_url == "http://127.0.0.1:5001/sse"


def test_from_env_derives_sse_url_from_base_url(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "secret")
    monkeypatch.delenv("MCP_SERVER_URL", raising=False)
    monkeypatch.setenv("MCP_BASE_URL", "http://127.0.0.1:5001")
    monkeypatch.setenv("MCP_TRANSPORT", "sse")

    config = QuartWebConfig.from_env()

    assert config.mcp_server_url == "http://127.0.0.1:5001/sse"


def test_from_env_derives_streamable_http_url_from_host_port(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "secret")
    monkeypatch.delenv("MCP_SERVER_URL", raising=False)
    monkeypatch.delenv("MCP_BASE_URL", raising=False)
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    monkeypatch.setenv("MCP_HOST", "127.0.0.1")
    monkeypatch.setenv("MCP_PORT", "5001")

    config = QuartWebConfig.from_env()

    assert config.mcp_server_url == "http://127.0.0.1:5001/mcp"