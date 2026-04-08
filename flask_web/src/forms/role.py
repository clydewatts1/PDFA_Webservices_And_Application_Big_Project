"""Role entity forms."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class RoleForm(FlaskForm):
    """Create/edit form for role business fields."""

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