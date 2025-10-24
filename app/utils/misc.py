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
    """Git commit hash bilgisini ve tarihini döndürür."""
    import subprocess
    import os
    from datetime import datetime

    # 1. Önce bilinen CI/CD ortam değişkenlerini kontrol et
    for env_var in ['GIT_COMMIT', 'SOURCE_COMMIT', 'COOLIFY_COMMIT_HASH', 'COOLIFY_GIT_COMMIT_HASH', 'CI_COMMIT_SHA']:
        if os.environ.get(env_var):
            git_hash = os.environ.get(env_var)
            short_hash = git_hash[:7] if git_hash else "unknown"
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
