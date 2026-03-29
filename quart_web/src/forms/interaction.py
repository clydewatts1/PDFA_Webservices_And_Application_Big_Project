"""Interaction entity forms."""

from __future__ import annotations

from wtforms import Form, HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class InteractionForm(Form):
	"""Create/edit form for Interaction business fields."""

	csrf_token = HiddenField("csrf_token")
	InteractionName = StringField(
		"InteractionName",
		validators=[DataRequired(message="InteractionName is required"), Length(max=128)],
	)
	WorkflowName = StringField("WorkflowName", validators=[DataRequired(message="WorkflowName is required")])
	InteractionDescription = TextAreaField("InteractionDescription", validators=[Length(max=2000)])
	InteractionContextDescription = TextAreaField("InteractionContextDescription", validators=[Length(max=4000)])
	InteractionType = StringField("InteractionType", validators=[Length(max=128)])
	submit = SubmitField("Save")
