import requests
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from functools import wraps

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
    Bir Flask route fonksiyonu olan `proxy`, çeşitli HTTP yöntemleriyle yapılan istekleri,
    FastAPI'ye bir proxy görevi görerek yönlendirir. Gelen istek metodu ve içeriklerine
    göre FastAPI'ye uygun bir HTTP isteği yapılır. Alınan yanıt, istemciye aktarılır.

    @parameters:
    endpoint: str
        FastAPI içerisinde yönlendirilmek istenen endpoint. Gelen istekten
        alınan yol, FastAPI'nin kök URL'sine eklenerek kullanılır.

    @raises:
    requests.RequestException
        FastAPI'ye erişim sırasında meydana gelebilecek bir HTTP hata durumunda
        tetiklenir. Flask uygulaması içinde bu durum ele alınır, hata kaydedilir
        ve istemciye uygun bir hata yanıtı döndürülür.

    @returns:
    tuple
        FastAPI'ye yapılan istek sonucunda alınan yanıt (JSON olarak biçimlendirilmiş
        içerik ve HTTP durum kodu). Eğer proxy başarısız olursa Flask uygulaması
        üzerinden bir hata mesajı ve durum kodu döner.
    """
    fastapi_url = Config.FASTAPI_DOMAIN+":"+Config.FASTAPI_PORT+"/api/" + endpoint

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