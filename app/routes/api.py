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
def proxy(endpoint):
    fastapi_url = "http://127.0.0.1:8000/api/" + endpoint

    # Request metoduna göre FastAPI'ye istek yap
    try:
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ['host', 'content-length']}

        # İsteği yönlendir
        if request.method == 'GET':
            resp = requests.get(fastapi_url, params=request.args, headers=headers, timeout=60)
        elif request.method == 'POST':
            resp = requests.post(fastapi_url, json=request.get_json(), headers=headers, timeout=60)
        elif request.method == 'PUT':
            resp = requests.put(fastapi_url, json=request.get_json(), headers=headers, timeout=60)
        elif request.method == 'DELETE':
            resp = requests.delete(fastapi_url, headers=headers, timeout=60)

        return jsonify(resp.json()), resp.status_code

    except requests.RequestException as e:
        # FastAPI'ye erişim hatalarında, alternatif olarak doğrudan Flask yanıtları
        current_app.logger.error(f"API proxy hatası: {str(e)}")

        return jsonify({"error": "API request failed", "message": str(e)}), 500