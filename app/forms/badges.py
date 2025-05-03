from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class BadgeForm(FlaskForm):
    """
    Form for creating and updating badges.
    """
    name = StringField('Badge Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    icon = StringField('Icon')
    submit = SubmitField('Save Badge')