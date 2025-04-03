import os


class Config:
    SECRET_KEY = 'secret!'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://radome:12345@localhost/python_platform'
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
        return os.path.join(os.getcwd(), 'notebooks_repo')