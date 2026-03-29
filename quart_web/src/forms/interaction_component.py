"""InteractionComponent entity forms."""

from __future__ import annotations

from wtforms import Form, HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class InteractionComponentForm(Form):
	"""Create/edit form for InteractionComponent business fields."""

	csrf_token = HiddenField("csrf_token")
	InteractionComponentName = StringField(
		"InteractionComponentName",
		validators=[
			DataRequired(message="InteractionComponentName is required"),
			Length(max=128),
		],
	)
	WorkflowName = StringField("WorkflowName", validators=[DataRequired(message="WorkflowName is required")])
	InteractionComponentRelationShip = StringField("InteractionComponentRelationShip", validators=[Length(max=128)])
	InteractionComponentDescription = TextAreaField("InteractionComponentDescription", validators=[Length(max=2000)])
	InteractionComponentContextDescription = TextAreaField(
		"InteractionComponentContextDescription", validators=[Length(max=4000)]
	)
	SourceName = StringField("SourceName", validators=[Length(max=128)])
	TargetName = StringField("TargetName", validators=[Length(max=128)])
	submit = SubmitField("Save")
