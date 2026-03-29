"""Quart web tier application entrypoint and app factory."""

from __future__ import annotations

import os
from datetime import timedelta

from quart import Quart, session

from quart_web.src.clients.mcp_client import MCPClientWrapper
from quart_web.src.config import QuartWebConfig
from quart_web.src.routes.auth import auth_bp
from quart_web.src.routes.errors import register_error_handlers
from quart_web.src.routes.guard import guard_bp
from quart_web.src.routes.health import health_bp
from quart_web.src.routes.interaction import interaction_bp
from quart_web.src.routes.interaction_component import interaction_component_bp
from quart_web.src.routes.role import role_bp
from quart_web.src.routes.workflow import workflow_bp
from quart_web.src.routes.workspace import workspace_bp


def create_app() -> Quart:
    """Create and configure the Quart application instance."""
    settings = QuartWebConfig.from_env()
    app = Quart(__name__, template_folder="templates")
    app.config.update(settings.as_quart_config())
    app.permanent_session_lifetime = timedelta(hours=8)
    app.mcp_client = MCPClientWrapper(
        url=settings.mcp_server_url,
        timeout_seconds=settings.mcp_timeout,
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(workflow_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(interaction_bp)
    app.register_blueprint(guard_bp)
    app.register_blueprint(interaction_component_bp)

    register_error_handlers(app)

    @app.before_request
    async def maintain_session_context() -> None:
        user_id = session.get("user_id")
        if user_id:
            session.permanent = True
        else:
            session.permanent = False
            session.pop("active_workflow_name", None)

    @app.after_serving
    async def close_mcp_client() -> None:
        await app.mcp_client.close()

    return app


if __name__ == "__main__":
    host = os.getenv("QUART_HOST", "127.0.0.1")
    port = int(os.getenv("QUART_PORT", "5002"))
    app = create_app()
    app.run(host=host, port=port, debug=False)
