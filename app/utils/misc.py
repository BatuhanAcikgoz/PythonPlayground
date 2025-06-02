from flask import url_for
from config import Config


def get_profile_image(user):
    """
    Kullanıcı profil resmini statik dosyalar dizininde döndürür.

    Fonksiyon, bir kullanıcı objesi alır ve eğer kullanıcıya atanmış bir profil
    resmi varsa, bu resmin dosya yolunu döndürür. Eğer kullanıcıya atanmış bir
    profil resmi yoksa, varsayılan profil resminin dosya yolunu döndürür.

    Args:
        user: Profil resmini almak istediğiniz kullanıcı objesi.

    Returns:
        str: Kullanıcıya ait profil resminin statik dosyalar dizinindeki dosya yolu.
    """
    if user.profile_image:
        return url_for('static', filename='profile_images/' + user.profile_image)
    else:
        return url_for('static', filename='profile_images/default.png')


def get_git_info():
    """
    Belirtilen bir GIT_COMMIT çevre değişkeninin veya mevcut bir .git klasörünün varlığına dayanarak,
    Git deposundan commit hash'ini ve ilgili tarih bilgilerini almak için kullanılan bir yardımcı fonksiyondur.
    Eğer gerekli bilgiler sağlanamazsa, "unknown" ve geçerli tarih döndürülür.

    Returns:
        tuple[str, str]: En kısa commit hash'i (7 karakter) ve commit tarihi. Bilgi alınamazsa "unknown" ve
        geçerli tarih döndürülür.

    Raises:
        subprocess.SubprocessError: Git komutları çalıştırılırken bir alt işlemin başarısız olması durumunda ortaya çıkar.
        FileNotFoundError: Git ile ilgili dosyaların veya klasörlerin bulunamaması durumunda fırlatılır.
    """
    import subprocess
    import os
    from datetime import datetime

    # 1. Eğer GIT_COMMIT çevre değişkeni varsa onu kullan
    if os.environ.get('GIT_COMMIT'):
        git_hash = os.environ.get('GIT_COMMIT')
        short_hash = git_hash[:7] if git_hash else "unknown"

        try:
            # Git hash'e göre tarihi al
            if git_hash and git_hash != "unknown":
                if os.path.exists('.git') or os.path.exists('/code/.git'):
                    git_dir = '.git' if os.path.exists('.git') else '/code/.git'
                    date_result = subprocess.run(
                        ['git', f'--git-dir={git_dir}', 'show', '-s', '--format=%ci', git_hash],
                        capture_output=True, text=True, check=True
                    )
                    commit_date = date_result.stdout.strip()
                    return short_hash, commit_date

            # Tarih bulunamazsa şu anki tarihi kullan
            return short_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except:
            return short_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 2. Eğer .git klasörü varsa git komutunu çalıştır
    try:
        if os.path.exists('.git') or os.path.exists('/code/.git'):
            git_dir = '.git' if os.path.exists('.git') else '/code/.git'
            # Hash'i al
            hash_result = subprocess.run(
                ['git', f'--git-dir={git_dir}', 'rev-parse', 'HEAD'],
                capture_output=True, text=True, check=True
            )
            git_hash = hash_result.stdout.strip()
            short_hash = git_hash[:7]

            # Tarihi al
            date_result = subprocess.run(
                ['git', f'--git-dir={git_dir}', 'show', '-s', '--format=%ci', 'HEAD'],
                capture_output=True, text=True, check=True
            )
            commit_date = date_result.stdout.strip()

            return short_hash, commit_date
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # 3. Hiçbiri çalışmazsa "unknown" döndür
    return "unknown", datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def wait_for_fastapi():
    """
    FastAPI servisinin belirtilen endpoint'ler üzerinde çalışmaya başladığını kontrol eden bir fonksiyon.
    Fonksiyon, belirli bir süre boyunca belirlenen endpoint'lere istek yaparak FastAPI'nin hazır olup olmadığını test eder.

    Errors:
        requests.exceptions.ConnectionError: Belirtilen bir endpoint'e bağlantı kurulamadığında oluşur.
        requests.exceptions.Timeout: Belirtilen endpoint'e yapılan istek zaman aşımına uğradığında oluşur.
        Exception: Genel istisnalar için yakalanan hata nesnesi.

    Returns:
        bool: FastAPI servisi belirtilen süre içerisinde hazırsa True, aksi halde False.
    """
    import requests
    import time
    import logging

    # Farklı endpoint'leri dene
    endpoints_to_try = [
        f"{Config.FASTAPI_DOMAIN}:{Config.FASTAPI_PORT}/health",
        f"{Config.FASTAPI_DOMAIN}:{Config.FASTAPI_PORT}/",
        f"{Config.FASTAPI_DOMAIN}:{Config.FASTAPI_PORT}/docs",
        "http://127.0.0.1:7923/",
        "http://localhost:7923/"
    ]

    max_wait = 45  # Docker için daha uzun bekleme
    start_time = time.time()
    logger = logging.getLogger('app')

    logger.info("FastAPI servisinin hazır olması bekleniyor...")
    logger.info(f"Test edilecek endpoint'ler: {endpoints_to_try}")

    while time.time() - start_time < max_wait:
        for url in endpoints_to_try:
            try:
                logger.info(f"Test ediliyor: {url}")
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 404]:  # 404 da kabul edilebilir
                    logger.info(f"FastAPI servisi hazır! URL: {url}")
                    return True
                else:
                    logger.info(f"Beklenmeyen yanıt kodu: {response.status_code}")

            except requests.exceptions.ConnectionError:
                logger.debug(f"Bağlantı kurulamadı: {url}")
            except requests.exceptions.Timeout:
                logger.debug(f"Zaman aşımı: {url}")
            except Exception as e:
                logger.debug(f"Genel hata: {url} - {e}")

        time.sleep(3)  # Docker için daha uzun aralık

    logger.error(f"FastAPI servisi {max_wait} saniye içinde hazır olmadı.")
    logger.warning("FastAPI olmadan devam ediliyor...")
    return False