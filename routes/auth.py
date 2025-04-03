from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from models.base import db
from models.user import User
from forms.auth import LoginForm, RegisterForm

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
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
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

@auth_bp.route('/profile')
def profile():
    if not current_user.is_authenticated:
        flash('Lütfen önce giriş yapın.')
        return redirect(url_for('auth.login'))

    return render_template('profile.html', user=current_user)

@auth_bp.route('/settings')
def settings():
    if not current_user.is_authenticated:
        flash('Lütfen önce giriş yapın.')
        return redirect(url_for('auth.login'))

    return render_template('settings.html', user=current_user)