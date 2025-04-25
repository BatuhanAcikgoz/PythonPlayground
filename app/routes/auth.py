from flask import Blueprint, render_template, redirect, url_for, flash, request
from urllib.parse import urlparse
from flask_login import login_user, logout_user, current_user, login_required

from app.forms.auth import UpdateAccountForm
from app.models.base import db
from app.models.user import User
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next', '')
            from urllib.parse import urlparse
            next_page = next_page.replace('\\', '')
            if next_page and not urlparse(next_page).netloc and not urlparse(next_page).scheme:
                return redirect(next_page)
            return redirect(url_for('main.index'))
        flash('Geçersiz kullanıcı adı veya şifre')

    return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
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
    if not current_user.is_authenticated:
        flash('Lütfen önce giriş yapın.')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=username).first()
    return render_template('profile.html', user=current_user)

@auth_bp.route('/settings/account', methods=['POST'])
@login_required
def update_account():
    # Hesap bilgileri güncelleme mantığı
    flash('Hesap bilgileriniz güncellendi.', 'success')
    return redirect(url_for('auth.settings'))

@auth_bp.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    # Profil bilgileri güncelleme mantığı
    flash('Profil bilgileriniz güncellendi.', 'success')
    return redirect(url_for('auth.settings'))

@auth_bp.route('/settings/notifications', methods=['POST'])
@login_required
def update_notifications():
    # Bildirim tercihleri güncelleme mantığı
    flash('Bildirim tercihleriniz güncellendi.', 'success')
    return redirect(url_for('auth.settings'))

@auth_bp.route('/settings/privacy', methods=['POST'])
@login_required
def update_privacy():
    # Gizlilik ayarları güncelleme mantığı
    flash('Gizlilik ayarlarınız güncellendi.', 'success')
    return redirect(url_for('auth.settings'))

@auth_bp.route('/settings')
@login_required
def settings():
    form = UpdateAccountForm()  # app/forms/auth.py'deki mevcut formunuz
    return render_template('settings.html', form=form)