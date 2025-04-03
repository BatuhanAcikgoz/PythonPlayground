from flask import Blueprint


def register_routes(app):
    # Auth routes
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Admin routes
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    # Notebook routes
    from .notebook import notebook_bp
    app.register_blueprint(notebook_bp)

    # Main routes
    from .main import main_bp
    app.register_blueprint(main_bp)