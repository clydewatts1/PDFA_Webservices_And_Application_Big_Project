"""Authentication routes for the canonical Flask web tier."""

from __future__ import annotations

import json
import logging
import time

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for

from flask_web.src.clients.mcp_client import MCPClientError
from flask_web.src.forms.auth import LoginForm, LogoutForm


auth_bp = Blueprint("auth", __name__)
logger = logging.getLogger("pdfa.flask.auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate the user via the MCP wrapper and establish session state."""

    if session.get("user_id"):
        return redirect(url_for("workspace.dashboard"))

    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("auth/login.html", form=form)

    started = time.perf_counter()
    username = str(form.username.data or "").strip()
    try:
        result = current_app.mcp_client.call(
            "user_logon",
            {"username": username, "password": str(form.password.data or "")},
        )
    except MCPClientError as exc:
        logger.warning(
            json.dumps(
                {
                    "event": "flask.auth.login.mcp_error",
                    "tool_name": "user_logon",
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "workflow_name": session.get("active_workflow_name"),
                    "username": username,
                    "error": exc.message,
                    "status_code": exc.status_code,
                }
            )
        )
        flash("Authentication service is unavailable. Please try again.", "danger")
        return render_template("auth/login.html", form=form), 200

    status = str(result.get("status", "")).upper()
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    if status == "SUCCESS":
        actor = str(result.get("username", username))
        session["user_id"] = actor
        session.pop("active_workflow_name", None)
        logger.info(
            json.dumps(
                {
                    "event": "flask.auth.login.success",
                    "username": actor,
                    "duration_ms": duration_ms,
                    "tool_name": "user_logon",
                }
            )
        )
        return redirect(url_for("workspace.dashboard"))

    message = str(result.get("status_message") or result.get("ErrorMessage") or "Login denied")
    logger.info(
        json.dumps(
            {
                "event": "flask.auth.login.denied",
                "username": username,
                "duration_ms": duration_ms,
                "tool_name": "user_logon",
                "reason": message,
            }
        )
    )
    flash(message, "danger")
    return render_template("auth/login.html", form=form), 200


@auth_bp.post("/logout")
def logout():
    """Log the user out via MCP and clear session state."""

    form = LogoutForm()
    if not form.validate_on_submit():
        return "Bad Request", 400

    username = session.get("user_id")
    if not username:
        return redirect(url_for("health.landing"))

    started = time.perf_counter()
    try:
        current_app.mcp_client.call("user_logoff", {"username": username})
    except MCPClientError as exc:
        logger.warning(
            json.dumps(
                {
                    "event": "flask.auth.logout.mcp_error",
                    "tool_name": "user_logoff",
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                    "workflow_name": session.get("active_workflow_name"),
                    "username": username,
                    "error": exc.message,
                }
            )
        )
    finally:
        session.clear()

    logger.info(
        json.dumps(
            {
                "event": "flask.auth.logout.completed",
                "username": username,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                "tool_name": "user_logoff",
            }
        )
    )
    return redirect(url_for("health.landing"))