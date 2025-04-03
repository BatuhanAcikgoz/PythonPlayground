from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.base import db
from models.user import User, Role
from models.course import Course  # Course modeliniz varsa
from forms.admin import UserForm, RoleForm, CourseForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Admin erişim kontrolü için decorator
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.has_role('admin'):
            flash('Bu sayfaya erişim izniniz yok.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route('/')
@admin_required
def index():
    users_list = User.query.all()
    users_data = []

    # User nesnelerini serileştirilebilir sözlüklere dönüştür
    for user in users_list:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [{'id': role.id, 'name': role.name} for role in user.roles]
        }
        users_data.append(user_data)

    return render_template('admin/index.html', users=users_data)


@admin_bp.route('/users')
@admin_required
def users():
    users_list = User.query.all()
    users_data = []

    # User nesnelerini serileştirilebilir sözlüklere dönüştür
    for user in users_list:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'roles': [{'id': role.id, 'name': role.name} for role in user.roles]
        }
        users_data.append(user_data)

    return render_template('admin/users.html', users=users_data)


@admin_bp.route('/users/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)

    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        if form.password.data:
            user.set_password(form.password.data)

        # Rolleri güncelle
        user.roles = []
        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)

        db.session.commit()
        flash('Kullanıcı başarıyla güncellendi.')
        return redirect(url_for('admin.users'))

    # Mevcut rolleri seç
    form.roles.data = [role.id for role in user.roles]
    return render_template('admin/edit_user.html', form=form, user=user)


@admin_bp.route('/courses')
@admin_required
def courses():
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)


@admin_bp.route('/courses/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    form = CourseForm(obj=course)

    if request.method == 'POST' and form.validate():
        form.populate_obj(course)
        db.session.commit()
        flash('Kurs başarıyla güncellendi.')
        return redirect(url_for('admin.courses'))

    return render_template('admin/edit_course.html', form=form, course=course)