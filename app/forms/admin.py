# forms/admin.py
from wtforms import Form, StringField, PasswordField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional
from app.models.user import Role

class UserForm(Form):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Parola', validators=[Optional(), Length(min=8)])
    roles = SelectMultipleField('Roller', coerce=int)
    submit = SubmitField('Kaydet')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.roles.choices = [(role.id, role.name) for role in Role.query.all()]

class RoleForm(Form):
    name = StringField('Rol Adı', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    submit = SubmitField('Kaydet')

class CourseForm(Form):
    name = StringField('Kurs Adı', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    submit = SubmitField('Kaydet')