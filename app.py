import threading
import uvicorn
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
import logging


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
        # NotebookSummary modelini açıkça import et
        from app.models.notebook_summary import NotebookSummary
        from app.models.programming_question import ProgrammingQuestion
        from app.models.submission import Submission
        from app.models.badges import Badges
        from app.models.badge_criteria import BadgeCriteria
        from app.models.user_badges import UserBadge
        from app.models.user import User, Role
        from app.models.settings import Setting

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
        ]

        for setting_data in default_settings:
            setting = Setting.query.filter_by(key=setting_data['key']).first()
            if not setting:
                setting = Setting(**setting_data)
                db.session.add(setting)

        db.session.commit()


# FastAPI uygulaması başlatma (thread olarak)
def run_fastapi():
    """
    FastAPI uygulamasını uvicorn ile başlatan bir fonksiyon.

    Fonksiyon, belirtilen host ve port üzerinde FastAPI uygulamasını çalıştırır.
    Eğer çalıştırma sırasında bir hata oluşursa, hatanın detayları konsola yazdırılır.

    Raises:
        Exception: FastAPI'nin başlatılması sırasında oluşabilecek herhangi bir hata.

    """
    try:
        # FastAPI'yi uvicorn ile başlat (reload devre dışı bırakıldı)
        uvicorn.run("api:api", host="127.0.0.1", port=int(Config.FASTAPI_PORT), reload=False)
    except Exception as e:
        print(f"FastAPI başlatma hatası: {e}")


# Fonksiyon çalışma kontrolü için global değişken
_summaries_loaded = False


def load_summaries_with_app_context(app):
    """
    Uygulama bağlamında çalışarak bir dizin altındaki Jupyter Notebook dosyalarının özetlerini yükleyen ve bu özetleri
    veritabanında mevcut olmayanlar için FastAPI üzerinden talep eden bir işlem süreci sağlar.

    Args:
        app: Flask uygulama nesnesi. Uygulama bağlamının yönetilmesi ve loglama işlemleri için gereklidir.

    Raises:
        requests.RequestException: API isteği sırasında oluşabilecek bir iletişim hatasında.
        Exception: Genel hatalar için, örneğin veritabanı veya dosya sistemi hataları gibi.

    Functions:
        - Dizindeki tüm notebook dosyalarını tarayarak bir liste oluşturur.
        - Henüz özetlenmemiş notebooklar için FastAPI'ye POST talebi oluşturur.
        - Özet alınabilen dosyaları loglar ve oran sınırlamaları için uyumlu bir bekleme süresi uygular.
    """
    with app.app_context():
        from flask import current_app
        from app.models.notebook_summary import NotebookSummary
        import requests
        import os
        import time

        # Notebooks dizini yolu
        notebooks_dir = os.path.join(os.getcwd(), 'notebooks_repo')
        if not os.path.exists(notebooks_dir):
            current_app.logger.error(f"Notebooks dizini bulunamadı: {notebooks_dir}")
            return

        # Tüm notebook dosyalarını bul
        notebook_files = []
        for root, _, files in os.walk(notebooks_dir):
            for file in files:
                if file.endswith('.ipynb'):
                    rel_path = os.path.relpath(os.path.join(root, file), notebooks_dir)
                    notebook_files.append(rel_path)

        current_app.logger.info(f"Toplam {len(notebook_files)} notebook bulundu, özetleri kontrol edilecek")

        # FastAPI servisine istek gönder
        try:
            # Direkt FastAPI servisine bağlan
            fastapi_url = Config.FASTAPI_DOMAIN+":"+Config.FASTAPI_PORT+"/api/notebook-summary"

            for i, notebook_path in enumerate(notebook_files):
                current_app.logger.info(f"[{i + 1}/{len(notebook_files)}] İşleniyor: {notebook_path}")

                # Veritabanında özet var mı kontrol et
                existing_summary = NotebookSummary.query.filter_by(notebook_path=notebook_path).first()
                if existing_summary:
                    current_app.logger.info(f"  Bu notebook için özet zaten mevcut, atlanıyor: {notebook_path}")
                    continue

                try:
                    # FastAPI'ye notebook özet isteği gönder - POST metodunu kullanmalı
                    response = requests.post(
                        fastapi_url,
                        json={"notebook_path": notebook_path},
                        timeout=None  # Yeterli zaman tanı
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("error"):
                            current_app.logger.warning(f"  Özet alınırken hata: {data.get('error')}")
                        else:
                            current_app.logger.info(f"  Özet başarıyla alındı: {len(data.get('summary', ''))} karakter")
                    else:
                        current_app.logger.error(f"  API hatası: {response.status_code} - {response.text}")

                    # Rate limit için bekleme - AI hizmetleri için önemli
                    if i < len(notebook_files) - 1:
                        time.sleep(20)  # Her istek arasında 5 saniye bekle

                except requests.RequestException as e:
                    current_app.logger.error(f"  API isteği başarısız: {str(e)}")

        except Exception as e:
            current_app.logger.error(f"Notebook özetleri yüklenirken genel hata: {str(e)}")

def generate_questions_on_startup(app):
    """
    generate_questions_on_startup fonksiyonu, bir Flask uygulamasını kullanarak belirli zorluk seviyeleri için otomatik
    olarak soru üreten bir işlemi başlatır. Bu işlem sırasında dış bir API'ye istekte bulunulur, alınan veriler işlenir ve
    veritabanına kaydedilir. API'den alınan yanıtın durumu, hata durumları ve başarı durumları loglanır.
    Her işleme ait adımda detaylı bilgi sağlanarak sistemdeki loglama mekanizmasına kayıt yapılır.
    Fonksiyon, işlemler sırasında belirli aralıklarla bekleme süreleri uygulayarak API üzerinde olası yoğun kullanım
    kısıtlamalarına uyum gösterir.

    Args:
        app: Flask uygulama nesnesini temsil eder ve gerekli bağlamın sağlanması için kullanılır.

    Raises:
        Exception: Herhangi bir hata oluştuğunda loglanmak üzere yakalanır, ancak fonksiyonun
        çalışmasını engellemez ve diğer zorluk seviyeleri işlenir.
    """
    with app.app_context():
        import requests
        import time
        from flask import current_app

        difficulty_levels = [1, 2, 3, 4]  # Kolay, Orta, Zor, Çok Zor

        current_app.logger.info("Başlangıç sorularını üretme işlemi başlatılıyor...")

        for difficulty in difficulty_levels:
            try:
                current_app.logger.info(f"Zorluk seviyesi {difficulty} için soru üretiliyor...")
                import json
                # JSON request body olarak gönder, query parametreleri olarak değil
                url = Config.FASTAPI_DOMAIN+":"+Config.FASTAPI_PORT+"/api/generate-question"
                headers = {"Content-Type": "application/json"}
                data = {
                    "difficulty_level": difficulty,
                    "topic": "",
                    "description_hint": "",
                    "function_name_hint": "",
                    "tags": []
                }

                response = requests.post(url, headers=headers, data=json.dumps(data))

                if response.status_code == 200:
                    question_data = response.json()
                    if "error" in question_data and question_data["error"]:
                        current_app.logger.error(
                            f"Zorluk {difficulty} için soru üretme hatası: {question_data['error']}, {question_data['debug_info']}")
                    else:
                        # Soruyu veritabanına ekle
                        from app.models.programming_question import ProgrammingQuestion

                        new_question = ProgrammingQuestion(
                            title=question_data["title"],
                            description=question_data["description"],
                            function_name=question_data["function_name"],
                            difficulty=difficulty,
                            topic=question_data["topic"],
                            points=question_data["points"],
                            example_input=question_data["example_input"],
                            example_output=question_data["example_output"],
                            test_inputs=question_data["test_inputs"],
                            solution_code=question_data["solution_code"]
                        )

                        db.session.add(new_question)
                        db.session.commit()
                        current_app.logger.info(
                            f"Zorluk {difficulty} için soru başarıyla üretildi: '{question_data['title']}'")
                else:
                    current_app.logger.error(f"API yanıt hatası: {response.status_code} - {response.text}")

                # Rate limit için her istekten sonra bekleme süresi
                time.sleep(5)

            except Exception as e:
                import traceback
                current_app.logger.error(f"Zorluk {difficulty} için soru üretilirken hata: {str(e)}")
                current_app.logger.error(traceback.format_exc())

        current_app.logger.info("Başlangıç soruları üretme işlemi tamamlandı.")


if __name__ == '__main__':
    app, socketio = create_app()

    # DB başlat
    init_db(app)

    # FastAPI'yi ayrı bir thread'de başlat
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()

    # Özetleri ayrı bir thread'de yükle
    summaries_thread = threading.Thread(target=load_summaries_with_app_context, args=(app,))
    summaries_thread.daemon = True
    summaries_thread.start()

    ai_questions_thread = threading.Thread(target=generate_questions_on_startup, args=(app,))
    ai_questions_thread.daemon = True
    ai_questions_thread.start()

    # Flask sunucusunu başlat
    socketio.run(app, debug=False, port=5000, allow_unsafe_werkzeug=True, log_output=True)