import threading
import logging
import time
from flask import Flask, session, render_template
from flask_babel import Babel
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect
from app.models.base import db
from app.models.user import User
from app.routes import register_routes
from config import Config
from colorlog import StreamHandler, ColoredFormatter
from app.tasks.instagram_tasks import instagram_task_manager
from app.utils.misc import get_git_info


def setup_logger():
    """Renkli loglamayı yapılandırır"""
    handler = StreamHandler()
    handler.setFormatter(ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        },
        datefmt='%Y-%m-%d %H:%M:%S'
    ))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []
    root_logger.addHandler(handler)


def create_app():
    """
    Flask web uygulamasını başlatmak ve yapılandırmak için kullanılan bir fonksiyon. Bu
     fonksiyon, gerekli uzantıları başlatır, kullanıcı oturumu yönetimi sağlar, çeviri için
    Babel'i yapılandırır, hata sayfalarını ayarlar ve gerekli rotaları yükler.

    Returns:
        tuple: Flask uygulama nesnesi ve SocketIO nesnesi
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # CSRF korumasını başlat
    csrf = CSRFProtect(app)

    setup_logger()

    # Uzantılar başlat
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'auth.login'

    # SocketIO başlat
    socketio = SocketIO(app, async_mode='threading')

    @app.context_processor
    def inject_globals():
        """
        create_app, bir Flask uygulaması başlatma ve yapılandırma işlemlerini gerçekleştiren
        ana işlevdir. Uygulamanın tüm bağlam işlemleri burada tanımlanır ve yürütülür.
        Bir Flask uygulamasını başlatmadan önce kullanılacak herhangi bir global değişken
        veya objeyi bu yapılandırmada tanımlayabilirsiniz.

        Returns:
            Flask: Başlatılmış ve yapılandırılmış bir Flask uygulama örneği.
        """
        from datetime import datetime
        return {
            'datetime': datetime,
            # Diğer global değişkenler
        }

    # Babel için locale seçici
    def get_locale():
        """
        create_app fonksiyonu, Flask uygulamasını başlatmak için genel yapılandırmaları
        ve bağımlılıkları ayarlayan bir fonksiyon sağlar. Bu fonksiyon, uygulamaya özgü
        dil eklentilerinin de yapılandırılmasını içerir.

        Functions:
            get_locale: Kullanıcının dil ayarlarını belirler.

        Returns:
            Flask uygulama nesnesi döner.
        """
        if 'language' in session:
            return session['language']
        return app.config['BABEL_DEFAULT_LOCALE']

    babel = Babel(app, locale_selector=get_locale)

    # UserLoader tanımı
    @login_manager.user_loader
    def load_user(id):
        """
        create_app fonksiyonu, Flask uygulaması oluşturur ve kullanıcı kimlik doğrulama işlemleri için gerekli yapılandırmaları
        gerçekleştirir.

        Returns:
            Flask: Oluşturulan Flask uygulama nesnesi.
        """
        return User.query.get(int(id))

    # Rotaları kaydet
    register_routes(app, socketio)

    # Hata sayfaları
    @app.errorhandler(403)
    def forbidden(error):
        """
        Flask uygulaması oluşturan bir fonksiyon.

        Bu fonksiyon, bir Flask uygulaması oluşturur ve bir hata işleyiciye sahiptir.

        Returns:
            Flask: Oluşturulan Flask uygulamasını döndürür.
        """
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        """
        Flask uygulaması oluşturur ve temel hata yönetimi ile birlikte yapılandırır.

        Functions:
            create_app: Flask uygulamasını oluşturur ve yapılandırır. Uygulamayı
            temel hata yönetimi ile donatır. 404 hata durumunda belirlenmiş bir
            şablon dosyasını kullanarak hata sayfası döner.

        Raises:
            HTTPException: Eğer bir HTTP hatası oluşursa yönetim sağlar.

        Returns:
            Flask: Oluşturulan Flask uygulama nesnesini döner.
        """
        return render_template('404.html'), 404

    return app, socketio


def init_db(app):
    """
    init_db(app)

    Uygulama veritabanını başlatır ve gerekli tabloları oluşturur. Müfredat için gerekli
    olan kullanıcı rolleri, kullanıcı hesabı ve varsayılan ayarlar bu işlev tarafından
    tanımlanır ve veritabanına eklenir. Yapılandırılmış bir uygulama bağlamında çalıştırılmalıdır.

    Arguments:
        app: Flask uygulaması örneği.

    Parameters:
        app (Flask): Flask uygulaması örneği. Aşağıdaki işlemlerin yapılması için gerekli
        olan uygulamanın bağlamını sağlar.

    Raises:
        Bu fonksiyon, herhangi bir hata yönetimi (exception handling) mekanizması
        içermediği için çalışma sırasında oluşabilecek hataları dışarıya aktarır.
    """
    with app.app_context():
        from app.models.notebook_summary import NotebookSummary
        from app.models.programming_question import ProgrammingQuestion
        from app.models.submission import Submission
        from app.models.badges import Badges
        from app.models.badge_criteria import BadgeCriteria
        from app.models.user_badges import UserBadge
        from app.models.user import User, Role
        from app.models.settings import Setting
        from app.models.cache import Cache

        # Tabloları oluştur
        db.create_all()

        # Rolleri başlat
        roles = {
            'student': 'Basic access to view notebooks',
            'teacher': 'Can manage notebooks and view student progress',
            'admin': 'Full administrative access'
        }

        # AI ayarlarını ekle
        from app.models.settings import add_ai_settings
        add_ai_settings()

        for role_name, description in roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=description)
                db.session.add(role)

        # Admin kullanıcı oluştur
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com')
            admin.set_password('admin123')
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                admin.roles.append(admin_role)
            db.session.add(admin)

        default_settings = [
            {'key': 'site_name', 'value': 'Python Playground', 'type': 'str', 'category': 'general'},
            {'key': 'site_description', 'value': 'Eğitim ve kodlama platformu', 'type': 'str', 'category': 'general'},
            {'key': 'default_language', 'value': 'tr', 'type': 'str', 'category': 'general'},
            {'key': 'allow_registration', 'value': 'True', 'type': 'bool', 'category': 'users'},
            {'key': 'enable_user_activation', 'value': 'False', 'type': 'bool', 'category': 'users'},
            {'key': 'tracked_instagram_users', 'value': 'bseu_istatistikvebilgisayar', 'type': 'str', 'category': 'social'},        ]

        for setting_data in default_settings:
            setting = Setting.query.filter_by(key=setting_data['key']).first()
            if not setting:
                setting = Setting(**setting_data)
                db.session.add(setting)

        db.session.commit()

# Fonksiyon çalışma kontrolü için global değişken
_summaries_loaded = False


def run_web_server_and_background_tasks(app, socketio):
    """
    Web sunucusu ve arka plan görevleri başlatıcı.

    Bu fonksiyon:
    1. Web sunucusunu başlatır
    2. Background görevleri başlatır (Instagram, vb.)
    """
    import logging
    logger = logging.getLogger('app')

    # Git commit numarasını ve tarihini oku ve göster
    commit_hash, commit_date = get_git_info()
    logger.info(f"Uygulama başlatılıyor - Commit: {commit_hash} ({commit_date})")

    # Instagram task manager'ı başlat
    try:
        instagram_task_manager.start()
        logger.info("✅ Instagram task manager başlatıldı")
    except Exception as e:
        logger.error(f"❌ Instagram task manager başlatılamadı: {str(e)}")

    logger.info("=" * 70)
    logger.info(f"🌐 Flask Web Server başlatılıyor: http://0.0.0.0:{Config.WEB_PORT}")
    logger.info("=" * 70)

    # Web sunucusunu başlat
    socketio.run(
        app,
        host="0.0.0.0",
        debug=True,
        port=Config.WEB_PORT,
        allow_unsafe_werkzeug=True,
        use_reloader=False,
        log_output=True
    )

if __name__ == '__main__':
    import time
    import logging
    import os

    logger = logging.getLogger('app')

    # 1. App'i oluştur
    logger.info("Flask uygulaması oluşturuluyor...")
    app, socketio = create_app()

    # 2. DB'yi başlat
    logger.info("Veritabanı başlatılıyor...")
    init_db(app)

    # 3. Docker initialization bekleme
    logger.info("Docker container initialization bekleniyor...")
    time.sleep(5)

    # 4. Web sunucusu ve background görevleri başlat
    logger.info("Web sunucusu ve background görevler başlatılıyor...")
    run_web_server_and_background_tasks(app, socketio)