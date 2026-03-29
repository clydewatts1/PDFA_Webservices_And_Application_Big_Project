"""Authentication and workspace-selection forms for the Quart web tier."""

from __future__ import annotations

from wtforms import Form, HiddenField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(Form):
	"""User login form for MCP-backed authentication."""

	csrf_token = HiddenField("csrf_token")
	username = StringField(
		"Username",
		validators=[DataRequired(message="Username is required"), Length(max=128)],
	)
	password = PasswordField(
		"Password",
		validators=[DataRequired(message="Password is required"), Length(max=256)],
	)
	submit = SubmitField("Login")


class WorkspaceSelectForm(Form):
	"""Workflow selection form used after authentication."""

	csrf_token = HiddenField("csrf_token")
	workflow_name = SelectField(
		"Workflow",
		choices=[],
		validators=[DataRequired(message="Workflow selection is required")],
	)
	submit = SubmitField("Continue")
