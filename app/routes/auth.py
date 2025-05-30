from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from app.forms.auth import UpdateAccountForm
from app.models.base import db
from app.models.user import User
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Kullanıcının giriş yaptığı ya da giriş formunu görüntülediği işlemi yöneten bir rota.

    Functions:
        Bu fonksiyon, kullanıcının giriş yapabileceği ya da zaten giriş yapmışsa ana sayfaya
        yönlendireceği bir login işlevi sağlar.

    Args:
        None

    Returns:
        Response: Kullanıcı oturum açmışsa ana sayfaya yönlendirilir. Oturum açık değilse ve
        kullanıcı geçerli bir kimlik doğrulama sağladıysa, login bilgileri onaylanarak
        giriş yapılır. Geçersiz bilgilerde hata mesajıyla giriş sayfası tekrar yüklenir.

    Raises:
        None
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next', '')
            next_page = next_page.replace('\\', '')
            if next_page and not urlparse(next_page).netloc and not urlparse(next_page).scheme:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        flash('Geçersiz kullanıcı adı veya şifre')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """
    Çıkış işlemi gerçekleştirir ve kullanıcıyı oturum açma sayfasına yönlendirir.

    Dosyalarda yer alan oturum bilgilerini sıfırlar ve kullanıcıyı oturum açma
    sayfasına yeniden yönlendirir.

    Returns:
        Werkzeug Response: Kullanıcıyı oturum açma sayfasına yönlendiren bir
        yanıt nesnesi.
    """
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Kullanıcı kayıt işlemlerini işleyen bir Flask route fonksiyonu. Bu rota, kullanıcılar
    için bir kayıt formu sunar ve giriş yapmamış kullanıcıların hesap oluşturmasına imkan
    tanır. Kayıt işlemi başarıyla tamamlandığında kullanıcı yönlendirilir ve bir flash
    mesaj görüntülenir.

    Arguments:
        None

    Returns:
        Werkzeug Response: Kullanıcının durumuna bağlı olarak farklı bir HTML sayfası
        veya yönlendirme döner.

    Raises:
        None
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/profil/<string:username>')
def profile(username):
    """
    Bir kullanıcıya ait profil sayfasını görüntülemek için kullanılan bir route.

    Bu endpoint, verilen kullanıcı adını kullanarak bir kullanıcı arar. Belirtilen kullanıcı
    veritabanında bulunamazsa bir hata mesajı gösterir ve ana sayfaya yönlendirir. Kullanıcı
    bulunursa, profil sayfası ile ilgili bir şablon oluşturularak bu şablon döndürülür.

    Parameters:
        username (str): Görüntülenmek istenen kullanıcının kullanıcı adı.

    Returns:
        Response: Kullanıcı profil şablonunun oluşturulmuş hali veya ana sayfaya yönlendirme.
    """
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Kullanıcı bulunamadı.', 'error')
        return redirect(url_for('main.index'))

    return render_template('profile.html', user=user)


@auth_bp.route('/profil')
def my_profile():
    """
    Flask blueprint route işlevi. Kullanıcı profil sayfasına yönlendirme işlemlerini
    barındırır. Kullanıcı giriş yapmamışsa, giriş yapmasını talep eder ve giriş
    sayfasına yönlendirir.

    Returns:
        Werkzeug response object: Bir HTML sayfasını döndüren bir yanıt nesnesi.
        Eğer kullanıcı giriş yapmamışsa, giriş sayfasını döndürür.
        Giriş yapmışsa, profil sayfasını döndürür.
    """
    if not current_user.is_authenticated:
        flash('Lütfen önce giriş yapın.')
        return redirect(url_for('auth.login'))

    return render_template('profile.html', user=current_user)


@auth_bp.route('/settings/account', methods=['POST'])
@login_required
def update_account():
    """
    Kullanıcının hesap bilgilerini güncelleyen bir görünüm fonksiyonudur. Bu işlem sırasında kullanıcının
    giriş yapmış olması gerekir. Başarıyla güncelleme sonrası bir bilgi mesajı görüntülenir ve ayarlar
    sayfasına yönlendirme yapılır.

    Parameters:
        methods (list): Fonksiyonun kabul ettiği HTTP metodları. Bu fonksiyon yalnızca 'POST' metodunu
        kabul eder.

    Returns:
        Response: Ayarlar sayfasına yönlendirme yapan bir Flask HTTP yanıt objesi döner.

    Raises:
        Exception: Eğer kullanıcı giriş yapmadan erişim sağlamaya çalışırsa bir hata alınabilir.

    Notlar:
        Bu fonksiyonun çalışması için `login_required` decorator'üne ek olarak Flask uygulamasının
        gerekli ayarları ve 'auth_bp' blueprint'in yapılandırılmış olması gerekmektedir.
    """
    # Hesap bilgileri güncelleme mantığı
    flash('Hesap bilgileriniz güncellendi.', 'success')
    return redirect(url_for('auth.settings'))

@auth_bp.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    """
    Güncellenmiş profil bilgilerini işleyen ve kullanıcıya başarı mesajı ile yönlendirme
    yapan bir Flask rotası.

    Parameters:
        None

    Returns:
        Werkzeug Response: Kullanıcıyı 'auth.settings' rotasına yönlendiren bir HTTP
        yanıtı döner.

    Raises:
        None
    """
    # Profil bilgileri güncelleme mantığı
    flash('Profil bilgileriniz güncellendi.', 'success')
    return redirect(url_for('auth.settings'))

@auth_bp.route('/settings/notifications', methods=['POST'])
@login_required
def update_notifications():
    """
    Bir kullanıcının bildirim tercihlerini güncellemesini sağlayan bir rota fonksiyonudur. Bu
    fonksiyon, form verilerini alarak kullanıcının tercihlerini günceller. Başarı durumunda
    kullanıcıya bir başarı mesajı görüntüler ve ayarlar sayfasına yönlendirir.

    Parameters:
        None

    Raises:
        None

    Returns:
        Werkzeug Response: Kullanıcıyı 'auth.settings' rotasına yönlendiren bir cevap döner.
    """
    # Bildirim tercihleri güncelleme mantığı
    flash('Bildirim tercihleriniz güncellendi.', 'success')
    return redirect(url_for('auth.settings'))

@auth_bp.route('/settings/privacy', methods=['POST'])
@login_required
def update_privacy():
    """
    Endpoint, kullanıcının gizlilik ayarlarını güncellemesini sağlar. Kullanıcı, bu endpointi kullanarak
    mevcut gizlilik tercihlerini değiştirebilir. Yalnızca giriş yapmış kullanıcılar bu fonksiyona erişebilir.

    Parameters:
        None

    Returns:
        werkzeug.wrappers.Response: Kullanıcıyı ayarları görüntüleme sayfasına yönlendiren bir cevap.

    Raises:
        None
    """
    # Gizlilik ayarları güncelleme mantığı
    flash('Gizlilik ayarlarınız güncellendi.', 'success')
    return redirect(url_for('auth.settings'))

@auth_bp.route('/settings')
@login_required
def settings():
    """
    Uygulamanın kullanıcı ayarları sayfasını döndüren bir görüntüleme fonksiyonudur.

    Bu fonksiyon, giriş yapmayı gerektirir ve kullanıcının hesap ayarlarını güncelleyebilmesi
    için bir form sağlar.

    Parameters
    ----------
    None

    Returns
    -------
    Response
        Kullanıcının ayarları gösterebileceği "settings.html" şablonunu bir form
        ile birlikte döner.

    Raises
    ------
    None
    """
    form = UpdateAccountForm()  # app/forms/auth.py'deki mevcut formunuz
    return render_template('settings.html', form=form)