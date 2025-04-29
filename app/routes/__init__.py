def register_routes(app, socketio=None):
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.notebook import notebook_bp, register_socketio_handlers
    from app.routes.programming import programming_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp  # Yeni API blueprint'i

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(notebook_bp, url_prefix='/view')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp)  # API blueprint'ini kaydet
    app.register_blueprint(programming_bp)

    # SocketIO işleyicilerini kaydet
    if socketio:
        register_socketio_handlers(socketio)
        print("SocketIO işleyicileri başarıyla kaydedildi")