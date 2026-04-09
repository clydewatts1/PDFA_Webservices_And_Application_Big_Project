"""Authentication and workspace-selection forms for the Flask web tier."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """User login form for MCP-backed authentication."""

    username = StringField(
        "Username",
        validators=[DataRequired(message="Username is required"), Length(max=128)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Password is required"), Length(max=256)],
    )
    submit = SubmitField("Login")


class WorkspaceSelectForm(FlaskForm):
    """Workflow selection form used after authentication."""

    workflow_name = SelectField(
        "Workflow",
        choices=[],
        validators=[DataRequired(message="Workflow selection is required")],
    )
    submit = SubmitField("Continue")


class LogoutForm(FlaskForm):
    """Hidden CSRF-protected logout form."""

    submit = SubmitField("Logout")