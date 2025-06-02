# forms/auth.py
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models.user import User


class LoginForm(FlaskForm):
    """
    Kullanıcı giriş formunu temsil eden bir sınıf.

    Giriş yaparken kullanıcı adı ve parola bilgilerini alır, ayrıca isteğe bağlı olarak
    kullanıcıdan "beni hatırla" seçeneğini işaretleyip işaretlemeyeceğini belirten bir
    değer alır. Bu form genellikle kimlik doğrulama işlemlerinde kullanılır.

    Attributes:
        username: Kullanıcı adı bilgisini temsil eden StringField. Form üzerinde
        "Kullanıcı Adı" başlığı ile görüntülenir.
        password: Kullanıcı parolasını temsil eden PasswordField. Form üzerinde
        "Parola" başlığı ile gösterilir.
        remember_me: Kullanıcının "beni hatırla" tercihini belirten BooleanField.
        submit: Formu gönderme işlemini gerçekleştiren SubmitField.
    """
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Parola', validators=[DataRequired()])
    remember_me = BooleanField('Beni Hatırla')
    submit = SubmitField('Giriş Yap')


class UpdateAccountForm(FlaskForm):
    """
    Kullanıcı hesabını güncellemek için bir form sınıfı.

    Bu sınıf, mevcut bir kullanıcı hesabını güncellemek için tasarlanmıştır. Kullanıcıdan, kullanıcı adı,
    e-posta adresi ve isteğe bağlı olarak şifre gibi bilgiler istenir. Form alanlarının doğrulama kuralları
    eklenmiştir ve kullanıcı adı ile e-posta adresindeki benzersizlik kontrol edilir.

    Attributes:
        username (flask_wtf.form.StringField): Kullanıcının yeni kullanıcı adını belirttiği alan, 3 ila 64 karakter uzunluğunda olmalı.
        email (flask_wtf.form.StringField): Kullanıcının yeni e-posta adresi bilgilerinin girildiği alan, geçerli bir e-posta adresi olmalı.
        current_password (flask_wtf.form.PasswordField): Kullanıcının mevcut şifresini girdiği alan.
        new_password (flask_wtf.form.PasswordField): Kullanıcının yeni bir şifre belirttiği alan, en az 8 karakter uzunluğunda olabilir.
        confirm_password (flask_wtf.form.PasswordField): Yeni şifrenin doğruluğunu kontrol etmek için doğrulama alanı.
        submit (flask_wtf.form.SubmitField): Formun gönderilmesini sağlayan göndermek düğmesi.

    Methods:
        validate_username(username): Kullanıcı adının mevcut kullanıcı adıyla aynı olup olmadığını kontrol eder. Eğer farklı ve başka bir kullanıcı
        tarafından kullanılıyorsa doğrulama hatası yükseltir.

        validate_email(email): E-posta adresinin mevcut e-posta adresiyle aynı olup olmadığını kontrol eder. Eğer farklı ve başka bir kullanıcı
        tarafından kullanılıyorsa doğrulama hatası yükseltir.
    """
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    current_password = PasswordField('Mevcut Şifre')
    new_password = PasswordField('Yeni Şifre', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Şifre Doğrulama', validators=[EqualTo('new_password')])
    submit = SubmitField('Güncelle')

    def validate_username(self, username):
        """
        Kontrolcü tarafından sağlanan kullanıcı adını doğrular. Kullanıcı adı, mevcut kullanıcı adı ile
        aynı değilse veritabanında mevcut olup olmadığını kontrol eder. Eğer kullanıcı adı mevcutsa
        bir doğrulama hatası fırlatır.

        Parameters
        ----------
        username : WTForms Field
            Doğrulama işlemi için girilen kullanıcı adı.

        Raises
        ------
        ValidationError
            Eğer kullanıcı adı zaten kullanımda ise doğrulama hatası fırlatılır.
        """
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Bu kullanıcı adı zaten alınmış.')

    def validate_email(self, email):
        """
        Bir kullanıcının e-posta adresinin geçerliliğini kontrol eden bir fonksiyon.

        Fonksiyon, kullanıcının girdiği e-posta adresinin mevcut kullanıcıya ait olup olmadığını
        kontrol eder. Eğer girdi mevcut kullanıcıya ait değilse, aynı e-posta adresiyle bir başka
        kullanıcının kayıtlı olup olmadığını doğrular. Eğer başka bir kullanıcı bulunuyorsa, bir
        ValidationError hatası yükseltilir.

        Arguments:
            email: Hedef E-posta adresini kontrol etmek için kullanılan parametre.

        Raises:
            ValidationError: E-posta adresi zaten bir başka kullanıcıya aitse yükseltilen hata.
        """
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Bu e-posta adresi zaten kayıtlı.')

class RegisterForm(FlaskForm):
    """
    Kullanıcı kayıt formunu temsil eder.

    Bu sınıf, bir kullanıcının kayıt işlemi sırasında doldurması gereken
    veri alanlarını içerir. Kullanıcı adını, e-posta adresini, şifreyi ve
    şifre doğrulamasını kontrol eder. Ayrıca belirli validasyon işlemleriyle
    girdi verisinin doğruluğunu sağlar.

    Attributes:
        username: Kullanıcı adını temsil eden metin alanı.
        email: E-posta adresini temsil eden metin alanı.
        password: Şifreyi temsil eden parola alanı.
        confirm_password: Şifre doğrulaması için kullanılan parola alanı.
        submit: Kayıt işlemini gönderme butonunu temsil eder.

    Methods:
        validate_username(username):
            Kullanıcı adının benzersiz olup olmadığını kontrol eder.
        validate_email(email):
            E-posta adresinin benzersiz olup olmadığını kontrol eder.
    """
    username = StringField('Kullanıcı Adı', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    password = PasswordField('Parola', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Parola Tekrar',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Kayıt Ol')

    def validate_username(self, username):
        """
        Kullanıcı adı doğrulama fonksiyonu.

        Bu fonksiyon, verilen kullanıcı adının veri tabanında mevcut olup olmadığını
        kontrol eder. Eğer kullanıcı adı zaten kullanılmışsa bir ValidationError
        fırlatır.

        Args:
            username: Doğrulanmak istenen kullanıcı adı alanı (önceden sağlanan
            verilerle dolmuş bir form nesnesinin alanı olarak gelir).

        Raises:
            ValidationError: Eğer kullanıcı adı veri tabanında zaten mevcutsa oluşur.
        """
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu kullanıcı adı zaten alınmış.')

    def validate_email(self, email):
        """
        Bu fonksiyon, verilen e-posta adresinin veri tabanında zaten kayıtlı olup olmadığını kontrol eder. Eğer e-posta adresi
        kayıtlıysa, bir doğrulama hatası (ValidationError) fırlatır. Bu sayede aynı e-posta adresine sahip birden fazla kullanıcı
        oluşturulması engellenir.

        Args:
            self: Doğrulama işlemini gerçekleştiren sınıfın örneği.
            email: Doğrulanacak e-posta adresini içeren veri.

        Raises:
            ValidationError: Eğer e-posta adresi veri tabanında zaten mevcutsa bu hata fırlatılır.
        """
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu e-posta adresi zaten kayıtlı.')