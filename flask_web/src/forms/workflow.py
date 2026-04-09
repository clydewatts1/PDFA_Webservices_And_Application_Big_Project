"""Workflow entity forms."""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class WorkflowForm(FlaskForm):
    """Create/edit form for workflow business fields."""

    WorkflowName = StringField(
        "WorkflowName",
        validators=[DataRequired(message="WorkflowName is required"), Length(max=128)],
    )
    WorkflowDescription = TextAreaField("WorkflowDescription", validators=[Length(max=2000)])
    WorkflowContextDescription = TextAreaField(
        "WorkflowContextDescription",
        validators=[Length(max=4000)],
    )
    WorkflowStateInd = StringField("WorkflowStateInd", validators=[Length(max=64)])
    submit = SubmitField("Save")