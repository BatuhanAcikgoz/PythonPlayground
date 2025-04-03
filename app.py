from flask import Flask, session, render_template
from flask_login import LoginManager
import uvicorn
import threading
from flask_babel import Babel
from flask_socketio import SocketIO
import logging

# Config ve modeller
from config import Config
from app.models.base import db
from app.models.user import User, Role
from app.routes import register_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Loglama
    logging.basicConfig(level=logging.ERROR)

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
        # Tabloları oluştur
        db.create_all()

        # Rolleri başlat
        roles = {
            'student': 'Basic access to view notebooks',
            'teacher': 'Can manage notebooks and view student progress',
            'admin': 'Full administrative access'
        }

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

        db.session.commit()


# FastAPI uygulaması başlatma (thread olarak)
def run_fastapi():
    try:
        # FastAPI'yi uvicorn ile başlat (reload devre dışı bırakıldı)
        uvicorn.run("api:api", host="127.0.0.1", port=8000, reload=False)
    except Exception as e:
        print(f"FastAPI başlatma hatası: {e}")


if __name__ == '__main__':
    app, socketio = create_app()

    # DB başlat
    init_db(app)

    # FastAPI'yi ayrı bir thread'de başlat (multiprocessing yerine)
    fastapi_thread = threading.Thread(target=run_fastapi)
    fastapi_thread.daemon = True  # Ana process bitince FastAPI thread'i de sonlanır
    fastapi_thread.start()

    # Flask sunucusunu başlat
    socketio.run(app, debug=True, port=5000, allow_unsafe_werkzeug=True)