"""Canary test — verifies pytest-asyncio auto mode is configured correctly.

This test has no business logic; it exists to prove Phase 1 SC-002:
  'Running pytest quart_web/tests/ with a trivial async test passes in under 5 seconds
  with no collection warnings about missing asyncio configuration.'
"""


async def test_async_mode_is_active():
    """Assert that async functions run without @pytest.mark.asyncio."""
    result = await _async_identity(42)
    assert result == 42


async def _async_identity(value):
    return value


async def test_app_factory_creates_quart_app(app):
    """Assert that create_app() returns a Quart application instance."""
    from quart import Quart

    assert isinstance(app, Quart)
