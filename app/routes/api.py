import requests
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from functools import wraps
from flask import Blueprint, jsonify, request, current_app, Response

from config import Config

api_bp = Blueprint('api', __name__, url_prefix='/api')


# Admin erişim kontrolü için decorator
def admin_required(f):
    """
    Bir Flask dekoratörü olan `admin_required`, yalnızca admin yetkisine sahip
    olan kullanıcıların belirli bir rota veya işlevi kullanmasına izin verilmesini
    sağlar. Kullanıcı admin değilse, bir hata mesajı ve 403 durum kodu döner.

    Args:
        f (Callable): Dekore edilecek işlev.

    Returns:
        Callable: Bünyesinde admin yetkisi kontrolü bulunan yeni işlev.

    Raises:
        403: Eğer kullanıcı admin değilse ve rota erişimine yetkisi yoksa bu durum
        kodu ile hata mesajı döner.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        """
        Bir Flask wrapper fonksiyonudur. Bu dekoratör, yalnızca yönetici yetkisi bulunan
        kullanıcıların erişebilmesini sağlamak için kullanılır. Eğer giriş yapmış olan
        kullanıcı yönetici değilse, bir hata mesajı döndürür.

        Parameters:
            f (Callable): Dekore edilecek olan işlev.

        Returns:
            Callable: Yönetici yetki kontrolü uygulanmış işlev.

        Raises:
            403: Giriş yapan kullanıcı yönetici değilse, HTTP 403 hatası döner.
        """
        if not current_user.is_admin():
            return jsonify({"error": "Admin yetkisi gerekiyor"}), 403
        return f(*args, **kwargs)

    return decorated_function


@api_bp.route('/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(endpoint):
    """
    Belirtilen bir FastAPI URL'sine HTTP isteklerini proxy aracılığıyla yönlendiren bir Flask view fonksiyonu.
    Modifiye edilmiş HTTP başlıklarını ve orijinal istekte bulunan bilgileri koruyarak hedef sunucuya istek gönderir
    ve yanıtları istemciye döndürür.

    Parameters:
        endpoint (str): Yönlendirilecek API endpoint adı. Bu, isteğin hedef sağlayıcıya yönlendirilmesinde kullanılır.

    Returns:
        Response: HTTP isteğinin hedef FastAPI sunucusundan gelen yanıtı.
    """
    fastapi_url = Config.FASTAPI_DOMAIN+":"+Config.FASTAPI_PORT+"/api/" + endpoint

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

        # Eğer proxy-image endpoint'i ise, binary içeriği doğrudan döndür
        if endpoint == 'proxy-image':
            return Response(
                resp.content,
                status=resp.status_code,
                content_type=resp.headers.get('Content-Type', 'image/jpeg')
            )

        # Diğer API istekleri için JSON yanıtı döndür
        return jsonify(resp.json()), resp.status_code

    except requests.RequestException as e:
        current_app.logger.error(f"API proxy hatası: {str(e)}")
        return jsonify({"error": "API request failed", "message": str(e)}), 500