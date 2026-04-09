"""Canonical Flask web application entrypoint and app factory."""

from __future__ import annotations

import json
import logging
import os
from datetime import timedelta

from flask import Flask, render_template, session
from flask_wtf import CSRFProtect

from flask_web.src.clients.mcp_client import MCPClientError
from flask_web.src.clients.mcp_client import MCPClient
from flask_web.src.config import FlaskWebConfig
from flask_web.src.routes.auth import auth_bp
from flask_web.src.routes.guard import guard_bp
from flask_web.src.routes.health import health_bp
from flask_web.src.routes.interaction import interaction_bp
from flask_web.src.routes.interaction_component import interaction_component_bp
from flask_web.src.routes.role import role_bp
from flask_web.src.routes.workflow import workflow_bp
from flask_web.src.routes.workspace import workspace_bp


logger = logging.getLogger("pdfa.flask")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

csrf = CSRFProtect()


def create_app() -> Flask:
    """Create and configure the Flask web application instance."""

    settings = FlaskWebConfig.from_env()
    app = Flask(__name__, template_folder="templates")
    app.config.update(settings.as_flask_config())
    app.permanent_session_lifetime = timedelta(hours=8)
    csrf.init_app(app)
    app.mcp_client = MCPClient(
        rpc_url=settings.mcp_rpc_url,
        timeout_seconds=settings.mcp_timeout,
    )

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(workflow_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(guard_bp)
    app.register_blueprint(interaction_bp)
    app.register_blueprint(interaction_component_bp)

    @app.before_request
    def maintain_session_context() -> None:
        user_id = session.get("user_id")
        if user_id:
            session.permanent = True
            return
        session.permanent = False
        session.pop("active_workflow_name", None)

    @app.errorhandler(MCPClientError)
    def handle_mcp_client_error(error: MCPClientError):
        """Render MCP client exceptions through the canonical error page."""

        logger.warning(
            json.dumps(
                {
                    "event": "flask.mcp.error",
                    "code": error.code,
                    "message": error.message,
                    "data": error.data,
                }
            )
        )
        return (
            render_template(
                "error.html",
                error_title="MCP Service Error",
                error_message=error.message,
                status_code=error.status_code,
            ),
            error.status_code,
        )

    @app.errorhandler(404)
    def handle_not_found(_error):
        return (
            render_template(
                "error.html",
                error_title="Not Found",
                error_message="The requested page could not be found.",
                status_code=404,
            ),
            404,
        )

    @app.errorhandler(500)
    def handle_server_error(_error):
        return (
            render_template(
                "error.html",
                error_title="Server Error",
                error_message="An unexpected error occurred.",
                status_code=500,
            ),
            500,
        )

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=False)
