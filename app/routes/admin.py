from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.settings import Setting
from app.forms.admin import SettingForm
from app.models.base import db
from app.models.user import User, Role
from app.forms import UserForm

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

    # Admin rolünü önceden belirle
    admin_role = Role.query.filter_by(name='admin').first()

    if request.method == 'POST' and form.validate():
        # Rolleri geçici olarak sakla
        role_ids = form.roles.data

        # Form.roles alanını geçici olarak kaldır
        form_roles = form.roles
        del form.roles

        # Diğer alanları güncelle (roles hariç)
        form.populate_obj(user)

        # Form.roles'u geri koy
        form.roles = form_roles

        # Şifre güncellemesi
        if form.password.data:
            user.set_password(form.password.data)

        # Rolleri güncelle
        roles = Role.query.filter(Role.id.in_(role_ids)).all()
        user.roles = roles

        # Kullanıcı ID=1 ise ve admin rolü kaldırıldıysa, tekrar ekle
        if id == 1 and admin_role and admin_role.id not in role_ids:
            user.roles.append(admin_role)
            flash('Ana admin kullanıcısından admin rolü kaldırılamaz.', 'warning')

        db.session.commit()
        flash('Kullanıcı başarıyla güncellendi.')
        return redirect(url_for('admin.users'))

    # Mevcut rolleri seç
    form.roles.data = [role.id for role in user.roles]
    return render_template('admin/edit_user.html', form=form, user=user)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    form = SettingForm()

    # Formu doldur (GET isteğinde)
    if request.method == 'GET':
        form.site_name.data = Setting.get('site_name', 'Site Adı')
        form.site_description.data = Setting.get('site_description', '')
        form.default_language.data = Setting.get('default_language', 'tr')
        form.allow_registration.data = '1' if Setting.get('allow_registration', True) else '0'
        form.enable_user_activation.data = '1' if Setting.get('enable_user_activation', False) else '0'
        form.mail_server.data = Setting.get('mail_server', '')
        form.mail_port.data = Setting.get('mail_port', '587')
        form.mail_username.data = Setting.get('mail_username', '')
        form.mail_password.data = Setting.get('mail_password', '')
        form.mail_use_tls.data = '1' if Setting.get('mail_use_tls', True) else '0'

        # AI ayarlarını da doldur
        form.enable_ai_features.data = '1' if Setting.get('ai_enable_features', True) else '0'
        form.api_provider.data = Setting.get('ai_api_provider', 'openai')
        form.default_ai_model.data = Setting.get('ai_default_model', 'gpt-3.5-turbo')
        form.api_key.data = Setting.get('ai_api_key', '')

    # Formu kaydet (POST isteğinde)
    if form.validate_on_submit():
        Setting.set('site_name', form.site_name.data)
        Setting.set('site_description', form.site_description.data)
        Setting.set('default_language', form.default_language.data)
        Setting.set('allow_registration', form.allow_registration.data == '1')
        Setting.set('enable_user_activation', form.enable_user_activation.data == '1')
        Setting.set('mail_server', form.mail_server.data)
        Setting.set('mail_port', form.mail_port.data)
        Setting.set('mail_username', form.mail_username.data)
        Setting.set('mail_password', form.mail_password.data)
        Setting.set('mail_use_tls', form.mail_use_tls.data == '1')

        # AI ayarlarını kaydet
        Setting.set('ai_enable_features', form.enable_ai_features.data == '1')
        Setting.set('ai_api_provider', form.api_provider.data)
        Setting.set('ai_default_model', form.default_ai_model.data)
        Setting.set('ai_api_key', form.api_key.data)

        db.session.commit()
        flash('Ayarlar başarıyla kaydedildi.', 'success')
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', form=form)


@admin_bp.route('/programming-questions/<int:id>/submissions')
@admin_required
def question_submissions(id):
    from app.models.submission import Submission
    from app.models.programming_question import ProgrammingQuestion

    # Soruyu kontrol et
    question = ProgrammingQuestion.query.get_or_404(id)

    # Bu soru için tüm çözümleri al
    submissions = Submission.query.filter_by(question_id=id) \
        .order_by(Submission.created_at.desc()).all()

    return render_template('admin/question_submissions.html',
                           question=question,
                           submissions=submissions)


@admin_bp.route('/programming-questions')
@admin_required
def programming_questions():
    from app.models.programming_question import ProgrammingQuestion
    questions = ProgrammingQuestion.query.order_by(ProgrammingQuestion.created_at.desc()).all()
    return render_template('admin/programming_questions.html', questions=questions)


@admin_bp.route('/programming-questions/new', methods=['GET', 'POST'])
@admin_required
def new_programming_question():
    from app.forms.programming import ProgrammingQuestionForm
    from app.models.programming_question import ProgrammingQuestion

    form = ProgrammingQuestionForm()

    if form.validate_on_submit():
        question = ProgrammingQuestion(
            title=form.title.data,
            description=form.description.data,
            difficulty=form.difficulty.data,
            points=form.points.data,
            example_input=form.example_input.data,
            example_output=form.example_output.data,
            function_name=form.function_name.data,
            solution_code=form.solution_code.data,
            test_inputs=form.test_inputs.data
        )

        db.session.add(question)
        db.session.commit()

        flash('Programlama sorusu başarıyla oluşturuldu.', 'success')
        return redirect(url_for('admin.programming_questions'))

    return render_template('admin/new_programming_question.html', form=form)


@admin_bp.route('/programming-questions/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_programming_question(id):
    from app.forms.programming import ProgrammingQuestionForm
    from app.models.programming_question import ProgrammingQuestion

    question = ProgrammingQuestion.query.get_or_404(id)
    form = ProgrammingQuestionForm(obj=question)

    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()

        flash('Programlama sorusu başarıyla güncellendi.', 'success')
        return redirect(url_for('admin.programming_questions'))

    return render_template('admin/edit_programming_question.html', form=form, question=question)


@admin_bp.route('/programming-questions/<int:id>/delete', methods=['POST'])
@admin_required
def delete_programming_question(id):
    from app.models.programming_question import ProgrammingQuestion

    question = ProgrammingQuestion.query.get_or_404(id)

    # Önce soruyla ilişkili gönderileri temizle
    from app.models.submission import Submission
    Submission.query.filter_by(question_id=id).delete()

    # Sonra soruyu sil
    db.session.delete(question)
    db.session.commit()

    flash('Programlama sorusu başarıyla silindi.', 'success')
    return redirect(url_for('admin.programming_questions'))


@admin_bp.route('/programming-questions/<int:id>')
@admin_required
def view_programming_question(id):
    from app.models.programming_question import ProgrammingQuestion

    question = ProgrammingQuestion.query.get_or_404(id)
    return render_template('admin/view_programming_question.html', question=question)


@admin_bp.route('/programming-questions/<int:id>/test', methods=['GET', 'POST'])
@admin_required
def test_programming_question(id):
    from app.models.programming_question import ProgrammingQuestion
    import requests

    question = ProgrammingQuestion.query.get_or_404(id)

    if request.method == 'POST':
        test_code = request.form.get('test_code')

        # FastAPI servisine istek gönder
        try:
            evaluation_request = {
                "code": test_code,
                "function_name": question.function_name,
                "test_inputs": question.test_inputs,
                "solution_code": question.solution_code
            }

            response = requests.post(
                "http://127.0.0.1:8000/api/evaluate",
                json=evaluation_request,
                timeout=5
            )

            if response.status_code == 200:
                result = response.json()
            else:
                flash('Kod değerlendirme servisi geçici olarak kullanılamıyor.', 'error')
                return render_template('admin/test_programming_question.html',
                                       question=question,
                                       test_code=test_code,
                                       error="API Hatası")

        except requests.RequestException as e:
            flash('Kod değerlendirme servisi geçici olarak kullanılamıyor.', 'error')
            return render_template('admin/test_programming_question.html',
                                   question=question,
                                   test_code=test_code,
                                   error=str(e))

        return render_template('admin/test_programming_question.html',
                               question=question,
                               test_code=test_code,
                               result=result)

    return render_template('admin/test_programming_question.html',
                           question=question,
                           test_code=question.solution_code)