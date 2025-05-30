from functools import wraps
from flask import redirect, url_for, request, abort
from flask_login import current_user

def role_required(role_name):
    """
    Role tabanlı erişim kontrolü için bir decorator.

    Bu decorator, bir kullanıcının belirli bir role sahip olup olmadığını kontrol eder. Eğer kullanıcı
    oturum açmamışsa, giriş sayfasına yönlendirilir. Ayrıca kullanıcı, beklenen role sahip değilse
    403 (Forbidden) hatası döner. Aksi takdirde, hedef işlev normal şekilde çalıştırılır.

    Arguments:
        role_name: str - Doğrulama yapılacak rolün adı.

    Raises:
        403: Kullanıcının erişmek istediği kaynağa yetkisi olmadığında ortaya çıkar.

    Returns:
        function: Hedef işlevi doğrulama mekanizmasıyla sarmalayan yeni işlev.
    """
    def decorator(f):
        """
        Bir decorator fonksiyonu olan `role_required`, bir kullanıcının belirli bir role sahip olup olmadığını kontrol etmek için kullanılır.
        Kullanıcı rolü kontrol altında değilse belirlenen işlemler gerçekleştirilir, aksi halde ilgili rota çalıştırılır.

        Parameters:
            role_name (str): Kontrol edilecek kullanıcı rolünün adı.

        Returns:
            Callable: Orijinal fonksiyonun çalışabilmesi için dekore edilmiş bir fonksiyon döndürür.
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            """
            Bir Flask rotasına erişim kontrolü ekleyen bir dekoratördür. Kullanıcının kimlik doğrulamasını
            ve bir role sahip olup olmadığını kontrol eder. Kimliği doğrulanmamış kullanıcıyı oturum
            açma sayfasına yönlendirir, uygun role sahip olmayan kullanıcıya ise yetkisiz erişim (403)
            hatası döner.

            Args:
                f (Callable): Sarmalanacak olan işlev.

            Returns:
                Callable: Erişim kontrolü uygulayan yeni bir işlev.

            Raises:
                werkzeug.exceptions.HTTPException: Eğer kullanıcı yeterli izinlere sahip değilse,
                403 hatası tetiklenir.
            """
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            if not current_user.has_role(role_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator