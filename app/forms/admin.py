# forms/admin.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Email, Length, Optional
from app.models.user import Role

class UserForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Parola', validators=[Optional(), Length(min=8)])
    roles = SelectMultipleField('Roller', coerce=int)
    submit = SubmitField('Kaydet')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.roles.choices = [(role.id, role.name) for role in Role.query.all()]

class RoleForm(FlaskForm):
    name = StringField('Rol Adı', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    submit = SubmitField('Kaydet')

class CourseForm(FlaskForm):
    name = StringField('Kurs Adı', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    submit = SubmitField('Kaydet')


class SettingForm(FlaskForm):
    site_name = StringField('Site Adı', validators=[DataRequired()])
    site_description = TextAreaField('Site Açıklaması')
    default_language = SelectField('Varsayılan Dil', choices=[('tr', 'Türkçe'), ('en', 'English')])
    allow_registration = SelectField('Kayıt İzni', choices=[('1', 'Açık'), ('0', 'Kapalı')])
    enable_user_activation = SelectField('Hesap Aktivasyonu', choices=[('1', 'Gerekli'), ('0', 'Gerekli Değil')])
    mail_server = StringField('Mail Sunucusu')
    mail_port = StringField('Mail Port')
    mail_username = StringField('Mail Kullanıcı Adı')
    mail_password = PasswordField('Mail Şifresi')
    mail_use_tls = SelectField('Mail TLS', choices=[('1', 'Evet'), ('0', 'Hayır')])

    # AI ile ilgili form alanları
    enable_ai_features = SelectField('AI Özellikleri', choices=[('1', 'Açık'), ('0', 'Kapalı')])
    api_provider = SelectField('API Sağlayıcı',
                               choices=[('gemini', 'Google Gemini')],
                               default='gemini')
    default_ai_model = SelectField('Varsayılan AI Modeli',
                                   choices=[
                                       ('gemini-1.5-pro-latest', 'Gemini 1.5 Pro'),
                                       ('gemini-1.5-flash-latest', 'Gemini 1.5 Flash')
                                   ],
                                   default='gemini-1.5-flash-latest')
    max_token_limit = StringField('Maksimum Token Limiti')
    api_key = PasswordField('API Anahtarı')
    submit = SubmitField('Ayarları Kaydet')