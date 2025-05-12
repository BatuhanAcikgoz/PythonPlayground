import logging
import threading

import uvicorn
from flask import Flask, session, render_template
from flask_babel import Babel
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_wtf import CSRFProtect

from app.models.base import db
from app.models.settings import Setting
from app.models.user import User, Role
from app.routes import register_routes
# Config ve modeller
from config import Config

# app.py içinde logging yapılandırması
import colorlog
import logging


def setup_logger():
    """Renkli loglamayı yapılandırır"""
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
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
    root_logger.setLevel(logging.INFO)  # Log seviyesi
    root_logger.handlers = []  # Mevcut handler'ları temizle
    root_logger.addHandler(handler)

def create_app():
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
        from datetime import datetime
        return {
            'datetime': datetime,
            # Diğer global değişkenler
        }

    # Babel için locale seçici
    def get_locale():
        if 'language' in session:
            return session['language']
        return app.config['BABEL_DEFAULT_LOCALE']

    babel = Babel(app, locale_selector=get_locale)

    # UserLoader tanımı
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Rotaları kaydet
    register_routes(app, socketio)

    # Hata sayfaları
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    return app, socketio


def init_db(app):
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
    try:
        # FastAPI'yi uvicorn ile başlat (reload devre dışı bırakıldı)
        uvicorn.run("api:api", host="127.0.0.1", port=8000, reload=False)
    except Exception as e:
        print(f"FastAPI başlatma hatası: {e}")


# Fonksiyon çalışma kontrolü için global değişken
_summaries_loaded = False


def load_summaries_with_app_context(app):
    """Notebook özetlerini arka planda FastAPI servisi aracılığıyla yükler."""
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
            fastapi_url = "http://127.0.0.1:8000/api/notebook-summary"

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
                        timeout=None # Yeterli zaman tanı
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


def init_db(app):
    with app.app_context():
        # NotebookSummary modelini açıkça import et
        from app.models.notebook_summary import NotebookSummary
        from app.models.programming_question import ProgrammingQuestion
        from app.models.submission import Submission
        from app.models.badges import Badges
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


def generate_questions_on_startup(app):
    with app.app_context():
        import requests
        import time
        from flask import current_app

        difficulty_levels = [1, 2, 3, 4]  # Kolay, Orta, Zor, Çok Zor

        current_app.logger.info("Başlangıç sorularını üretme işlemi başlatılıyor...")

        for difficulty in difficulty_levels:
            try:
                current_app.logger.info(f"Zorluk seviyesi {difficulty} için soru üretiliyor...")

                # FastAPI endpoint'ine istek gönder
                response = requests.post(
                    "http://127.0.0.1:8000/api/generate-question",
                    params={"difficulty_level": difficulty},
                    timeout=180  # 180 saniye timeout
                )

                if response.status_code == 200:
                    question_data = response.json()

                    if "error" in question_data and question_data["error"]:
                        current_app.logger.error(f"Zorluk {difficulty} için soru üretme hatası: {question_data['error']}")
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

    # FastAPI'yi ayrı bir thread'de başlat (multiprocessing yerine)
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True  # Ana process bitince FastAPI thread'i de sonlanır
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
