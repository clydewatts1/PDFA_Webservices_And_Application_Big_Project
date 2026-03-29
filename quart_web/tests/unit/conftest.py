"""Pytest configuration and shared fixtures for quart_web unit tests."""
import os

import pytest
from quart_web.src.app import create_app


@pytest.fixture()
def app():
    """Create a Quart test application instance."""
    os.environ.setdefault("SESSION_SECRET", "test-session-secret")
    os.environ.setdefault("MCP_SERVER_URL", "http://127.0.0.1:5001/sse")
    application = create_app()
    application.config["TESTING"] = True
    application.config["WTF_CSRF_ENABLED"] = False
    return application


@pytest.fixture()
def client(app):
    """Return a Quart async test client."""
    return app.test_client()
