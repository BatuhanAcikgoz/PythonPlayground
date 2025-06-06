import os

class Config:
    """
    Sistem yapılandırma ayarlarını tutar.

    Bu sınıf, uygulamanın çalışması için gerekli konfigürasyon ayarlarını içerir.
    Konfigürasyon, uygulamanın güvenlik anahtarı, veritabanı bağlantı bilgileri,
    dil ayarları gibi pek çok parametreyi belirler. Bu sınıf sabit parametreler
    ve bir özellik metodu ile yapılandırılmıştır.

    Attributes:
        SECRET_KEY (str): Uygulama için güvenlik anahtarı.
        SQLALCHEMY_DATABASE_URI (str): Veritabanı bağlantı bilgilerini taşıyan URI.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Veritabanı değişikliklerini izleme
            ayarının aktif olup olmadığını belirtir.
        BABEL_DEFAULT_LOCALE (str): Uygulamanın varsayılan dil ayarını tanımlar.
        BABEL_SUPPORTED_LOCALES (list): Uygulamanın desteklediği dilleri listeler.
        SESSION_TYPE (str): Oturum türünü belirtir. Örneğin, 'filesystem'.
        PERMANENT_SESSION_LIFETIME (int): Oturumların kalıcı ömrünü saniye
            cinsinden tanımlar.
        REPO_URL (str): GitHub depo URL'sini tanımlar.
    """
    FASTAPI_DOMAIN = os.environ.get('FASTAPI_DOMAIN') or 'http://127.0.0.1'
    FASTAPI_PORT = os.environ.get('FASTAPI_PORT') or '7923'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'mysql+pymysql://radome:12345@127.0.0.1/python_platform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'tr'
    BABEL_SUPPORTED_LOCALES = ['tr', 'en']
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600

    # GitHub repo URL
    REPO_URL = 'https://github.com/msy-bilecik/ist204_2025'

    # Repo dizin yolu
    @property
    def REPO_DIR(self):
        """
        Bu özellik, çalışma dizinindeki 'notebooks_repo' dizinini temsil eden bir dosya yolu döndürür.
        Kullanıcının not defteri deposunun tam yolunu sağlar ve dinamik olarak çalışma dizinine göre
        oluşturulur.

        Returns:
            str: Çalışma dizinindeki 'notebooks_repo' dizininin yolu.
        """
        return os.path.join(os.getcwd(), 'notebooks_repo')