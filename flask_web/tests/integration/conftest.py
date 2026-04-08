from __future__ import annotations

import pytest

from flask_web.src.app import create_app
from flask_web.tests.support import FakeMCPClient


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.setenv("SESSION_SECRET", "integration-session-secret")
    monkeypatch.setenv("MCP_RPC_URL", "http://127.0.0.1:5001/rpc")
    application = create_app()
    application.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    application.mcp_client = FakeMCPClient()
    return application


@pytest.fixture()
def client(app):
    return app.test_client()