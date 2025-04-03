import requests
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from functools import wraps

api_bp = Blueprint('api', __name__, url_prefix='/api')


# Admin erişim kontrolü için decorator
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify({"error": "Admin yetkisi gerekiyor"}), 403
        return f(*args, **kwargs)

    return decorated_function


@api_bp.route('/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@admin_required
def proxy(endpoint):
    # FastAPI adresi - önce admin yetkisini kontrol ediyoruz
    fastapi_url = "http://127.0.0.1:8000/api/" + endpoint

    # Request metoduna göre FastAPI'ye istek yap
    try:
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}

        # İsteği yönlendir
        if request.method == 'GET':
            resp = requests.get(fastapi_url, params=request.args, headers=headers, timeout=5)
        elif request.method == 'POST':
            resp = requests.post(fastapi_url, json=request.get_json(), headers=headers, timeout=5)
        elif request.method == 'PUT':
            resp = requests.put(fastapi_url, json=request.get_json(), headers=headers, timeout=5)
        elif request.method == 'DELETE':
            resp = requests.delete(fastapi_url, headers=headers, timeout=5)

        return jsonify(resp.json()), resp.status_code

    except requests.RequestException as e:
        # FastAPI'ye erişim hatalarında, alternatif olarak doğrudan Flask yanıtları
        current_app.logger.error(f"API proxy hatası: {str(e)}")

        # FastAPI bağlantı hatası durumunda geriye dönüş (fallback) fonksiyonları
        if endpoint == "server-status":
            return fallback_server_status()
        elif endpoint == "recent-users":
            return fallback_recent_users()
        elif endpoint == "recent-questions":
            return fallback_recent_questions()

        return jsonify({"error": "API request failed", "message": str(e)}), 500


# Geriye dönüş (fallback) fonksiyonları
def fallback_server_status():
    import platform
    import psutil
    import os
    import flask

    # Python sürümü
    python_version = platform.python_version()

    # Flask sürümü
    flask_version = flask.__version__

    # Sistem RAM kullanımı
    mem = psutil.virtual_memory()
    ram_used = round(mem.used / (1024 * 1024 * 1024), 2)  # GB
    ram_total = round(mem.total / (1024 * 1024 * 1024), 2)  # GB

    # Süreç RAM kullanımı
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    process_ram_used = round(process_memory.rss / (1024 * 1024 * 1024), 2)
    process_ram_allocated = round(process_memory.vms / (1024 * 1024 * 1024), 2)

    # CPU kullanımı
    cpu_usage = psutil.cpu_percent(interval=1)

    return jsonify({
        'python_version': python_version,
        'flask_version': flask_version,
        'mysql_version': "N/A (Fallback)",
        'ram_used': ram_used,
        'ram_total': ram_total,
        'cpu_usage': cpu_usage,
        'process_ram_used': process_ram_used,
        'process_ram_allocated': process_ram_allocated,
        '_fallback': True
    })


def fallback_recent_users():
    from models.user import User

    users = User.query.order_by(User.id.desc()).limit(5).all()
    recent_users = []

    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "registered": user.created_at.strftime("%d.%m.%Y") if hasattr(user,
                                                                          'created_at') and user.created_at else "01.01.2025",
            "roles": [role.name for role in user.roles],
            "_fallback": True
        }
        recent_users.append(user_data)

    return jsonify(recent_users)


def fallback_recent_questions():
    # Örnek veri
    sample_questions = [
        {"id": 1, "title": "Python döngüleri nasıl kullanılır?", "user": "student1", "date": "02.04.2025",
         "status": "answered"},
        {"id": 2, "title": "Flask Blueprint nedir?", "user": "student3", "date": "01.04.2025", "status": "pending"},
        {"id": 3, "title": "React ile Flask nasıl entegre edilir?", "user": "student2", "date": "31.03.2025",
         "status": "answered"},
        {"id": 4, "title": "SQLAlchemy ilişkiler nasıl kurulur?", "user": "student4", "date": "30.03.2025",
         "status": "pending"}
    ]

    for q in sample_questions:
        q["_fallback"] = True

    return jsonify(sample_questions)