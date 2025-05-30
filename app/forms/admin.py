# forms/admin.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Email, Length, Optional
from app.models.user import Role

class UserForm(FlaskForm):
    """
    Kullanıcı formunu temsil eden bir sınıf.

    Bu sınıf, FlaskForm sınıfından türetilmiştir ve bir kullanıcı formunun doğrulama ve
    form elemanlarını tanımlamak için kullanılır. Kullanıcı adı, e-posta adresi, parola
    ve roller gibi alanları içerir. Form alanlarına yönelik doğrulama kuralları
    belirtilmiştir ve roller için dinamik seçim seçenekleri yüklenmektedir.
    """
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Parola', validators=[Optional(), Length(min=8)])
    roles = SelectMultipleField('Roller', coerce=int)
    submit = SubmitField('Kaydet')

    def __init__(self, *args, **kwargs):
        """
        Initializes an instance of the UserForm class, setting up role choices for form usage.

        Parameters
        ----------
        *args :
            Variable length argument list.
        **kwargs :
            Arbitrary keyword arguments.

        """
        super(UserForm, self).__init__(*args, **kwargs)
        self.roles.choices = [(role.id, role.name) for role in Role.query.all()]

class RoleForm(FlaskForm):
    """
    Rol formunu temsil eden sınıf.

    Kullanıcı rollerini tanımlamak ve düzenlemek için kullanılacak bir form sağlar.
    FlaskForm sınıfından türemiştir ve kullanıcıların rol adı ve açıklama gibi
    ilgili bilgileri girmesine olanak tanır.
    """
    name = StringField('Rol Adı', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Açıklama', validators=[DataRequired()])
    submit = SubmitField('Kaydet')

class SettingForm(FlaskForm):
    """
    Kullanıcı arayüzü üzerinden sistem ayarlarını yapılandırmak için kullanılan form sınıfıdır.

    Bu sınıf, Flask web uygulamalarında sistem ayarlarının kullanıcı tarafından
    düzenlenmesi için bir form sağlar. Form, sistem genelinde belirli sabit
    ayarları değiştirmek amacıyla kullanılabilir. Alanlar, sistemin çeşitli
    özelliklerini ve kullanıcı yönetimi ile ilgili ayarlarını yapılandırmayı
    amaçlamaktadır. Ayrıca, yapay zeka ile ilgili özelliklerin yönetimi için de
    seçenekler içerir.

    Attributes:
        site_name (StringField): Sitenin adı. Kullanıcı tarafından zorunlu olarak doldurulmalıdır.
        site_description (TextAreaField): Sitenin açıklaması. Zorunlu değildir.
        default_language (SelectField): Sitenin varsayılan dili. Seçenekler arasında "Türkçe" ve "English" bulunur.
        allow_registration (SelectField): Kullanıcı kaydına izin verme ayarı. Seçenekler: Açık (1) veya Kapalı (0).
        enable_user_activation (SelectField): Hesap aktivasyon gerekliliği ayarı. Seçenekler: Gerekli (1) veya Gerekli Değil (0).
        mail_server (StringField): Mail sunucusunun adı.
        mail_port (StringField): Mail sunucusu bağlantı portu.
        mail_username (StringField): Mail hesap adı.
        mail_password (PasswordField): Mail hesap şifresi.
        mail_use_tls (SelectField): Mail bağlantısı için TLS kullanım ayarı. Seçenekler: Evet (1) veya Hayır (0).
        enable_ai_features (SelectField): Yapay zeka özelliklerini etkinleştirme ayarı. Seçenekler: Açık (1) veya Kapalı (0).
        api_provider (SelectField): Kullanılacak API sağlayıcı. Varsayılan değer: "Google Gemini".
        default_ai_model (SelectField): Varsayılan yapay zeka modeli. Seçenekler arasında çeşitli "Gemini" modelleri bulunur.
        api_key (PasswordField): API erişim anahtarı.
        submit (SubmitField): Formu gönderme düğmesi.
    """
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
    enable_ai_features = SelectField('AI Özellikleri', choices=[('1', 'Açık'), ('0', 'Kapalı')])
    api_provider = SelectField('API Sağlayıcı',
                               choices=[('gemini', 'Google Gemini')],
                               default='gemini')
    default_ai_model = SelectField('Varsayılan AI Modeli',
                                   choices=[
                                       ('gemini-1.5-pro-latest', 'Gemini 1.5 Pro'),
                                       ('gemini-1.5-flash-latest', 'Gemini 1.5 Flash'),
                                       ('gemini-2.0-pro', 'Gemini 2.0 Pro'),
                                       ('gemini-2.0-flash', 'Gemini 2.0 Flash'),
                                       ('gemini-2.0-flash-lite', 'Gemini 2.0 Flash Lite'),
                                   ],
                                   default='gemini-2.0-flash-lite')
    api_key = PasswordField('API Anahtarı')
    submit = SubmitField('Ayarları Kaydet')