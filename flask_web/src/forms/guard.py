"""Guard entity forms."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class GuardForm(FlaskForm):
    """Create/edit form for guard business fields."""

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