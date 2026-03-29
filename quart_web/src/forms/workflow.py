"""Workflow entity forms."""

from __future__ import annotations

from wtforms import Form, HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class WorkflowForm(Form):
	"""Create/edit form for Workflow business fields."""

	csrf_token = HiddenField("csrf_token")
	WorkflowName = StringField(
		"WorkflowName",
		validators=[DataRequired(message="WorkflowName is required"), Length(max=128)],
	)
	WorkflowDescription = TextAreaField("WorkflowDescription", validators=[Length(max=2000)])
	WorkflowContextDescription = TextAreaField(
		"WorkflowContextDescription", validators=[Length(max=4000)]
	)
	WorkflowStateInd = StringField("WorkflowStateInd", validators=[Length(max=64)])
	submit = SubmitField("Save")
