from app.models.base import db

class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text)
    type = db.Column(db.String(20), default='str')
    category = db.Column(db.String(64), default='general')
    description = db.Column(db.String(255))

    @classmethod
    def get(cls, key, default=None):
        """Belirli bir anahtarın değerini döndür"""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            return default

        # Değeri tipine göre dönüştür
        if setting.type == 'int':
            return int(setting.value) if setting.value else 0
        elif setting.type == 'float':
            return float(setting.value) if setting.value else 0.0
        elif setting.type == 'bool':
            return setting.value.lower() in ('true', '1', 'yes') if setting.value else False
        else:  # str veya diğer tipler
            return setting.value

    @classmethod
    def set(cls, key, value, type=None, category=None, description=None):
        """Ayarı güncelle veya oluştur"""
        setting = cls.query.filter_by(key=key).first()

        if setting:
            setting.value = str(value)
            if type:
                setting.type = type
            if category:
                setting.category = category
            if description:
                setting.description = description
        else:
            setting = cls(
                key=key,
                value=str(value),
                type=type or 'str',
                category=category or 'general',
                description=description
            )
            db.session.add(setting)

def add_ai_settings():
    """AI ayarlarını Settings tablosuna ekler - Sadece Gemini API için"""
    ai_settings = [
        {'key': 'ai_enable_features', 'value': 'True', 'type': 'bool', 'category': 'ai',
         'description': 'AI özelliklerinin kullanımını etkinleştirir'},
        {'key': 'ai_api_provider', 'value': 'gemini', 'type': 'str', 'category': 'ai',
         'description': 'AI API sağlayıcısı (sadece Gemini destekleniyor)'},
        {'key': 'ai_default_model', 'value': 'gemini-2.0-flash', 'type': 'str', 'category': 'ai',
         'description': 'Varsayılan Gemini modeli'},
        {'key': 'ai_max_token_limit', 'value': '1000', 'type': 'int', 'category': 'ai',
         'description': 'Maksimum token limiti'},
        {'key': 'ai_api_key', 'value': '', 'type': 'str', 'category': 'ai',
         'description': 'Gemini API anahtarı'}
    ]

    for setting_data in ai_settings:
        setting = Setting.query.filter_by(key=setting_data['key']).first()
        if not setting:
            setting = Setting(**setting_data)
            db.session.add(setting)

    db.session.commit()