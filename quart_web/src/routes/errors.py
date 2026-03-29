"""Global error handlers for Quart web tier."""

from __future__ import annotations

from flask_wtf.csrf import CSRFError
from quart import Quart, render_template

from quart_web.src.clients.errors import MCPClientError, MCPConnectionError, MCPTimeoutError


def register_error_handlers(app: Quart) -> None:
    """Register global HTTP and MCP-specific error handlers."""

    @app.errorhandler(400)
    async def handle_bad_request(error):
        message = "Bad request."
        if isinstance(error, CSRFError):
            message = str(error.description or "Invalid CSRF token.")
        return (
            await render_template(
                "error.html",
                status_code=400,
                error_title="Bad Request",
                error_message=message,
            ),
            400,
        )

    @app.errorhandler(403)
    async def handle_forbidden(_error):
        return (
            await render_template(
                "error.html",
                status_code=403,
                error_title="Forbidden",
                error_message="You do not have permission to access this page.",
            ),
            403,
        )

    @app.errorhandler(500)
    async def handle_internal_error(_error):
        return (
            await render_template(
                "error.html",
                status_code=500,
                error_title="Internal Server Error",
                error_message="An unexpected error occurred.",
            ),
            500,
        )

    @app.errorhandler(503)
    async def handle_service_unavailable(_error):
        return (
            await render_template(
                "error.html",
                status_code=503,
                error_title="Service Unavailable",
                error_message="The MCP backend is currently unavailable.",
            ),
            503,
        )

    @app.errorhandler(504)
    async def handle_gateway_timeout(_error):
        return (
            await render_template(
                "error.html",
                status_code=504,
                error_title="Gateway Timeout",
                error_message="The MCP backend did not respond in time.",
            ),
            504,
        )

    @app.errorhandler(MCPTimeoutError)
    async def handle_mcp_timeout(error: MCPTimeoutError):
        return (
            await render_template(
                "error.html",
                status_code=504,
                error_title="Gateway Timeout",
                error_message=error.message,
            ),
            504,
        )

    @app.errorhandler(MCPConnectionError)
    async def handle_mcp_connection(error: MCPConnectionError):
        return (
            await render_template(
                "error.html",
                status_code=503,
                error_title="Service Unavailable",
                error_message=error.message,
            ),
            503,
        )

    @app.errorhandler(MCPClientError)
    async def handle_generic_mcp(error: MCPClientError):
        status_code = getattr(error, "status_code", 502)
        return (
            await render_template(
                "error.html",
                status_code=status_code,
                error_title="MCP Error",
                error_message=error.message,
            ),
            status_code,
        )
