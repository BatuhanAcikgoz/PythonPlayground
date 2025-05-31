from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.forms.badges import BadgeForm
from app.models.badge_criteria import BadgeCriteria
from app.models.badges import Badges
from app.models.settings import Setting
from app.forms.admin import SettingForm
from app.models.base import db
from app.models.user import User, Role
from app.forms import UserForm
from flask_wtf import FlaskForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Admin erişim kontrolü için decorator
def admin_required(f):
    """
    Bir kullanıcının admin rolüne sahip olup olmadığını kontrol eden ve buna göre erişim
    yetkisi sağlayan bir dekoratör fonksiyonu. Bu dekoratör, yalnızca admin yetkisine sahip
    kullanıcıların belirli bir işlevi çalıştırabilmesine olanak tanır.

    Arguments:
        f (Callable): Birincil işlev. Erişim sınırlaması uygulanacak ana fonksiyondur.

    Returns:
        Callable: Yeni işlev, erişim kontrolleri uygulanmış şekilde döndürülür.

    Raises:
        RedirectException: Eğer kullanıcı admin rolüne sahip değilse kullanıcı ana sayfaya
        yönlendirilir ve bir hata mesajı gösterilir.

    """
    @login_required
    def decorated_function(*args, **kwargs):
        """
        This function is a decorator used to enforce that a user has the 'admin'
        role to access a specific view or endpoint in a Flask application. It
        ensures that only users with the 'admin' role can proceed to the decorated
        view while others are redirected to the main index page.

        Parameters:
            f (Callable): The Flask route handler function to be decorated.

        Returns:
            Callable: A decorated function that checks the user's privileges
            before executing the original function.

        Raises:
            Redirects the user to the main index page with an error flash message
            if the user is not logged in or does not have the 'admin' role.
        """
        if not current_user.has_role('admin'):
            flash('Bu sayfaya erişim izniniz yok.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)

    decorated_function.__name__ = f.__name__
    return decorated_function


@admin_bp.route('/')
@admin_required
def index():
    """
    Bu view fonksiyonu, yönetici kontrol panelinin ana sayfasını oluşturur. Yönetici yetkisine sahip kullanıcılar
    tarafından çağrılabilir. Kullanıcı listesini veritabanından alır, her kullanıcı için gerekli bilgileri
    ve rollerini içerecek şekilde bir sözlük oluşturur ve ardından bu bilgileri şablon aracılığıyla
    görüntüler.

    Parameters:
        None

    Returns:
        Werkzeug Response: HTTP yanıtı. Admin paneli ana sayfasını içeren bir HTML yanıt döner.

    Raises:
        None
    """
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
    """
    admin_bp modülü için /users rotasını işleten fonksiyondur.

    Bu fonksiyon, tüm kullanıcıları sorgular ve admin tarafından erişilebilecek
    şekilde kullanıcı verilerini serileştirir. Her kullanıcıya ilişkin bilgiler
    id, username, email ve rollerini içerir. Serileştirilen kullanıcı
    verilerini HTML şablonuna aktarır ve döndürür.

    Arguments:
        None

    Returns:
        werkzeug.wrappers.response.Response: Admin kullanıcılar için hazırlanmış
        bir HTML sayfası döner. Bu sayfa, kullanıcıların serileştirilmiş verilerini içerir.

    Raises:
        Flask düğümündeki potansiyel hatalar sırasında HTTP hataları yaratılabilir.

    """
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
    """
    Bir kullanıcının bilgilerini düzenleme yeteneği sağlayan bir Flask rota işlevi.

    Bu işlev, belirtilen kullanıcının bilgilerini güncellemek için kullanılan bir formu işler ve
    gönderilen form verilerini kontrol ederek kullanıcı detaylarını günceller. Eğer ilgili kullanıcı
    ana bir admin kullanıcı ise, admin rolünü kaldırmak gibi belirli eylemleri kısıtlar. Güncelleme
    işlemi sırasında roller, şifre ve diğer bilgiler doğrulanarak veri tabanında güvenli bir şekilde
    değişiklikler yapılır.

    Parameters:
        id (int): Düzenlenecek kullanıcının benzersiz kimlik numarası.

    Raises:
        404: Eğer belirtilen kullanıcı ID ile bir kullanıcı bulunamazsa.

    Returns:
        flask.Response: İşlem sonucunda, güncellenmiş bir kullanıcı bilgisiyle ilgili bir HTML sayfası
                        döndürülür veya güncelleme başarılı olursa kullanıcılar sayfasına yönlendirilir.
    """
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
    """
    Bu fonksiyon, yönetici panelinde ayarlar sayfasını görüntülemek ve kullanıcıların
    sistemin temel ayarlarını değiştirmesine olanak sağlamak için bir HTTP GET ve POST
    işleyicisi olarak kullanılır. GET isteğiyle, mevcut ayarlar form alanlarında doldurulur.
    POST isteğiyle, form doğrulandıktan sonra ayarlar güncellenir ve veri tabanına kaydedilir.

    Args:
        form (SettingForm): Kullanıcı tarafından doldurulan ayar formu.

    Returns:
        Response: Aynı sayfaya geçerli form objesiyle dönüş yapılır veya başarılı güncelleme durumunda
        ayarlar sayfası yeniden yüklenir.

    Raises:
     Hint- follow error ranges mappingute"""
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
    """
    Fonksiyon, belirtilen bir programlama sorusuna ait tüm çözümleri (submission) alarak bir şablon dosyasına yönlendiren bir Flask rota işlemcisidir.

    Args:
        id (int): Programlama sorusunun benzersiz kimlik numarası.

    Returns:
        str: Yönetici görünümü için gerekli olan verileri içeren bir HTML şablonu.

    Raises:
        werkzeug.exceptions.NotFound: Eğer verilen `id` ile eşleşen bir programlama sorusu bulunamazsa.
    """
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
    """
    Yönetici panelinde programlama sorularını listeleyen bir Flask görünümdür.

    Bu görünüm, programlama sorularını tarih sırasına göre azalan bir biçimde
    sıralar ve admin/programming_questions.html şablonunda görüntüler.

    Parameters:
        Yok

    Returns:
        Werkzeug Response: render_template tarafından döndürülen bir Flask
        HTTP cevabı.
    """
    from app.models.programming_question import ProgrammingQuestion
    questions = ProgrammingQuestion.query.order_by(ProgrammingQuestion.created_at.desc()).all()
    return render_template('admin/programming_questions.html', questions=questions)


@admin_bp.route('/programming-questions/new', methods=['GET', 'POST'])
@admin_required
def new_programming_question():
    """
    Hedef adres '/programming-questions/new' olan bir route'un görevini gerçekleştiren
    fonksiyon. Yeni bir programlama sorusu oluşturmak amacıyla kullanılır. Kullanıcıdan
    gelen form verilerini alır, doğrular ve geçerli ise yeni bir programlama sorusunu
    veritabanına ekler. Ayrıca işlem sonucuna göre kullanıcıya bildirimde bulunur.

    Arguments:
        None

    Returns:
        Flask Response: Kullanıcıya, form doldurma ve gönderme işlemi durumuna göre
        ilgili sayfa döndürülür.
    """
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

@admin_bp.route('/programming-questions/new_ai', methods=['GET', 'POST'])
@admin_required
def new_ai_programming_question():
    """
    Bu fonksiyon, yapay zeka tabanlı yeni bir programlama sorusu oluşturmak için kullanılan bir
    route tanımını içerir. Gelen GET ve POST isteklerini işleyerek, gerekli form doğrulamaları
    yapılır ve doğrulama başarılı olduğunda kullanıcıdan alınan verilerle veritabanına bir
    soru kaydedilir. Ayrıca, işlem sonucunda bir başarı mesajı görüntülenir.

    Arguments:
        None

    Returns:
        Flask HTTP yanıtı: Eğer POST isteğinde form gönderimi ve doğrulama başarılıysa,
        kullanıcıyı programlama sorularının listesini içeren sayfaya yönlendirir. Aksi
        durumda, kullanıcıya formu tekrar sunar.
    """
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

        flash('AI programlama sorusu başarıyla oluşturuldu.', 'success')
        return redirect(url_for('admin.programming_questions'))

    return render_template('admin/generate_ai_question.html', form=form)


@admin_bp.route('/programming-questions/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_programming_question(id):
    """
    Bir programlama sorusunu düzenlemek için kullanılan Flask görünüm fonksiyonu.

    Bu fonksiyon belirli bir `id`'ye sahip programlama sorusunu veritabanından alır
    ve kullanıcıdan gelen form bilgileriyle düzenlenmesini sağlar. Form,
    ilk oluşturulurken mevcut sorunun bilgileri ile doldurulur.
    Formun doğrulaması başarılı olduğunda, düzenlenen soru veritabanında güncellenir
    ve kullanıcı bir onay mesajıyla başka bir sayfaya yönlendirilir.
    Eğer form doğrulaması başarısızsa, aynı sayfada hata mesajları görüntülenir.

    Parameters:
        id (int): Düzenlenecek programlama sorusunun benzersiz kimliği.

    Raises:
        werkzeug.exceptions.NotFound: Belirtilen `id`'ye sahip bir programlama
        sorusu bulunamazsa tetiklenir.

    Returns:
        flask.wrappers.Response: HTTP yanıtı olarak düzenleme formu içeren HTML sayfası
        veya düzenleme başarılı ise yönlendirilen URL.
    """
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
    """
    Route bir programlama sorusunu silmek için kullanılır. Yönetici yetkisi gerektirir.
    İlk olarak soruyla ilişkili tüm gönderiler temizlenir, ardından sorunun kendisi silinir.
    İşlem başarıyla tamamlanırsa, kullanıcıya bir başarı mesajı gösterilir ve
    programlama soruları görünümüne yönlendirilir.

    Parameters:
        id (int): Silinecek olan programlama sorusunun benzersiz tanımlayıcısı.

    Returns:
        Response: İşlem başarılıysa kullanıcıyı programlama soruları sayfasına yönlendiren bir HTTP yanıtı.
    """
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
    """
    Bu rota, belirli bir programlama sorusunu görüntüleme işlemini gerçekleştirir.
    Yönetici erişimi gerektirir. Bir ID parametresi alır ve bu ID'ye ait programlama
    sorusunu veri tabanından sorgular. Sorgu sonuçsuz kalırsa 404 hata kodu döndürülür.
    Başarılı bir sorgu halinde, ilgili programlama sorusuyla birlikte bu soruya ait
    detaylar bir şablon ile kullanıcıya sunulur.

    Parameters:
        id (int): Görüntülenmek istenen programlama sorusunun benzersiz kimlik
        numarası.

    Raises:
        NotFound: Eğer belirtilen ID'ye sahip bir programlama sorusu bulunamazsa
        404 hatası döner.

    Returns:
        Response: programlama sorusunun detaylarını barındıran HTML yanıtı.
    """
    from app.models.programming_question import ProgrammingQuestion

    question = ProgrammingQuestion.query.get_or_404(id)
    return render_template('admin/view_programming_question.html', question=question)


@admin_bp.route('/programming-questions/<int:id>/test', methods=['GET', 'POST'])
@admin_required
def test_programming_question(id):
    """
    admin_bp altındaki bir route işlevidir. Bu işlev, programlama sorusu testi yapılmasına olanak sağlar.
    Bir GET isteği alındığında, form sayfası döndürülür ve POST isteği ile test kodu FastAPI servisine
    gönderilerek değerlendirilir.

    Args:
        id (int): Testi yapılacak programlama sorusunun veritabanındaki ID'si.

    Raises:
        requests.RequestException: FastAPI değerlendirme servisi ile yapılan istek sırasında hata oluşursa yükseltilir.

    Returns:
        str: HTTP Yanıtı ve şablon render edilerek döndürülen HTML çıktısı.
    """
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
                Config.FASTAPI_DOMAIN+":"+Config.FASTAPI_PORT+"/api/evaluate",
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


@admin_bp.route('/badges')
@admin_required
def badges():
    """
    Badges işlevi, sistemdeki mevcut tüm rozetleri sorgulayıp serileştirerek
    ön uçta kullanıma hazır bir formatta döndürür. Bu işlev, rozetlerin
    isim, açıklama, simge, renk ve oluşturulma/güncellenme zaman bilgilerini
    içerir.

    Parameters:
        None

    Returns:
        Response: Admin panelinin rozetlere ayrılmış HTML şablonuyla yapılan
        HTTP yanıtı. Veriler, formatlanmış rozet bilgilerini içeren bir
        liste olarak döndürülür.
    """
    from app.models.badges import Badges
    badges_list = Badges.query.all()

    # Badges nesnelerini serileştirilebilir sözlüklere dönüştür
    badges_data = []
    for badge in badges_list:
        badges_data.append({
            'id': badge.id,
            'name': badge.name,
            'description': badge.description,
            'icon': badge.icon,
            'color': badge.color,
            'created_at': badge.created_at.isoformat() if hasattr(badge, 'created_at') and badge.created_at else None,
            'updated_at': badge.updated_at.isoformat() if hasattr(badge, 'updated_at') and badge.updated_at else None
        })

    return render_template('admin/badges.html', badge=badges_data)


@login_required
@admin_required
@admin_bp.route('/badges/new', methods=['GET', 'POST'])
def new_badge():
    """
    Yeni rozet oluşturma ve gerekli kriterleri kaydetme işlemlerini yöneten bir Flask rotasıdır. Bu rota, kullanıcıdan rozet
    bilgilerini ve kriterlerini alır, doğrulama yapar ve veritabanına kayıt işlemini gerçekleştirir. Yalnızca giriş yapmış
    ve yönetici izni olan kullanıcılar için erişime açıktır. GET ve POST HTTP metodlarını destekler.

    Parameters:
        None

    Returns:
        str: Yeni rozet sayfasının HTML içeriği (GET isteği) veya işlem sonucuna göre yönlendirme veya mesaj (POST isteği).

    Raises:
        Exception: Veritabanı işlemleri sırasında bir hata meydana gelirse fırlatılır ve işlem geri alınır.
    """
    form = FlaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            name = request.form['name'].strip()
            description = request.form['description'].strip()
            icon = request.form['icon'].strip()
            color = request.form['color'].strip()
            criteria_type = request.form['criteria_type']
            criteria_value = request.form.get('criteria_value', '')

            # Basit doğrulama
            if not name or not description or not icon:
                flash('Tüm alanları doldurun', 'error')
                return render_template('admin/new_badge.html', form=form)

            # Rozet nesnesini oluştur
            badge = Badges(
                name=name,
                description=description,
                icon=icon,
                color=color
            )
            db.session.add(badge)
            db.session.flush()  # badge.id değerini almak için

            # Rozet kriteri oluştur
            criteria = BadgeCriteria(
                badge_id=badge.id,
                criteria_type=criteria_type,
                criteria_value=criteria_value if criteria_value else None
            )
            db.session.add(criteria)

            db.session.commit()
            flash('Rozet başarıyla eklendi', 'success')
            return redirect(url_for('admin.badges'))
        except Exception as e:
            db.session.rollback()
            flash(f'Rozet eklenirken hata oluştu: {str(e)}', 'error')

    return render_template('admin/new_badge.html', form=form)


@admin_bp.route('/badges/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_badge(id):
    """
    edit_badge fonksiyonu, belirtilen ID'ye sahip bir Rozet'in (Badge) bilgilerini düzenlemek
    için bir form sunan ve güncellenen bilgileri veritabanında işleyen bir Flask görünümdür.
    Bu işlemi yalnızca yetkili ve giriş yapmış kullanıcılar gerçekleştirebilir.

    Parameters:
        id (int): Düzenlenecek rozetin eşsiz kimlik numarası.

    Raises:
        abort: Belirtilen ID'ye ait bir rozet bulunamadığında HTTP 404 hatası döndürülür.

    Returns:
        Response: Eğer POST talebi geçerli bir form ile gönderilmişse, güncellenen rozet
        ile yönetim rozet sayfasına yönlendirme yapılır. Aksi halde düzenleme formunu içeren
        bir HTML şablonu döndürülür.
    """
    badge = Badges.query.get_or_404(id)
    criteria = BadgeCriteria.query.filter_by(id=id).first()
    form = BadgeForm()

    if form.validate_on_submit():
        # Rozet bilgilerini güncelle
        badge.name = form.name.data
        badge.description = form.description.data
        badge.icon = form.icon.data
        badge.color = form.color.data

        # Kriter bilgilerini güncelle
        if not criteria:
            criteria = BadgeCriteria(badge_id=badge.id)
            db.session.add(criteria)

        criteria.criteria_type = request.form.get('criteria_type', 'registration')
        criteria.criteria_value = request.form.get(
            'criteria_value') if criteria.criteria_type != 'registration' else None

        db.session.commit()
        flash('Rozet başarıyla güncellendi!', 'success')
        return redirect(url_for('admin.badges'))

    # Şablona gönderilecek veriyi hazırla
    badge_data = {
        'id': badge.id,
        'name': badge.name,
        'description': badge.description,
        'icon': badge.icon,
        'color': badge.color,
        'criteria_type': criteria.criteria_type if criteria else 'registration',
        'criteria_value': criteria.criteria_value if criteria and criteria.criteria_value else ''
    }

    return render_template('admin/edit_badge.html', badge=badge_data, form=form)

@admin_bp.route('/badges/<int:id>/delete', methods=['POST'])
@admin_required
def delete_badge(id):
    """
    Belirtilen ID'ye sahip bir rozet (badge) kaydını siler. Rozet ile ilişkili olan kullanıcıların
    rozet bilgilerini de temizler ve ardından silme işlemine devam eder. İşlem sonucunda, başarıyla
    silme geri bildirimi kullanıcıya gösterilir.

    Arguments:
        id (int): Silinmesi gereken rozetin ID'si.

    Returns:
        Werkzeug Response: Silme işleminin ardından yönetici rozetler sayfasına yönlendiren
        bir cevap döndürülür.

    Raises:
        404: Belirtilen ID'ye sahip bir rozet bulunamadıysa bir hata yükseltilir.
    """
    from app.models.badges import Badges

    badge = Badges.query.get_or_404(id)

    # Badge ile ilişkili kullanıcıları güncelle
    from app.models.user import User
    users = User.query.filter(User.badge_id == id).all()
    for user in users:
        user.badge_id = None

    # Sonra badge'i sil
    db.session.delete(badge)
    db.session.commit()

    flash('Badge başarıyla silindi.', 'success')
    return redirect(url_for('admin.badges'))