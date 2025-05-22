from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class BadgeForm(FlaskForm):
    """
    Form for creating and updating badges.
    """
    name = StringField('Badge Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    icon = HiddenField('Icon', validators=[DataRequired()])
    color = HiddenField('Color', validators=[DataRequired()])
    criteria_type = StringField('Criteria Type', validators=[DataRequired()])
    criteria_value = StringField('Criteria Value', validators=[DataRequired()])
    submit = SubmitField('Save Badge')