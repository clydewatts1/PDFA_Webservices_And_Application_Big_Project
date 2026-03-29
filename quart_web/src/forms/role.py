"""Role entity forms."""

from __future__ import annotations

from wtforms import Form, HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class RoleForm(Form):
	"""Create/edit form for Role business fields."""

	csrf_token = HiddenField("csrf_token")
	RoleName = StringField(
		"RoleName",
		validators=[DataRequired(message="RoleName is required"), Length(max=128)],
	)
	WorkflowName = StringField("WorkflowName", validators=[DataRequired(message="WorkflowName is required")])
	RoleDescription = TextAreaField("RoleDescription", validators=[Length(max=2000)])
	RoleContextDescription = TextAreaField("RoleContextDescription", validators=[Length(max=4000)])
	RoleConfiguration = TextAreaField("RoleConfiguration")
	RoleConfigurationDescription = TextAreaField("RoleConfigurationDescription")
	RoleConfigurationContextDescription = TextAreaField("RoleConfigurationContextDescription")
	submit = SubmitField("Save")
