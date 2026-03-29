"""Guard entity forms."""

from __future__ import annotations

from wtforms import Form, HiddenField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class GuardForm(Form):
	"""Create/edit form for Guard business fields."""

	csrf_token = HiddenField("csrf_token")
	GuardName = StringField(
		"GuardName",
		validators=[DataRequired(message="GuardName is required"), Length(max=128)],
	)
	WorkflowName = StringField("WorkflowName", validators=[DataRequired(message="WorkflowName is required")])
	GuardDescription = TextAreaField("GuardDescription", validators=[Length(max=2000)])
	GuardContextDescription = TextAreaField("GuardContextDescription", validators=[Length(max=4000)])
	GuardType = StringField("GuardType", validators=[Length(max=128)])
	GuardConfiguration = TextAreaField("GuardConfiguration")
	submit = SubmitField("Save")
