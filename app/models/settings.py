from app.models.base import db

class Setting(db.Model):
    """
    Veritabanı modeli ile uygulama ayarlarını yönetir.

    Bu sınıf, uygulamanın dinamik ayarlarını yönetmek için bir model sunar. Ayarlar
    anahtar-değer çiftleri şeklinde saklanır ve gerekli olduğunda ayarın tipi
    dönüştürülerek kullanılabilir. Ayrıca, ayarlarda oluşturma veya güncelleme
    işlemlerini kolay bir şekilde yapmak için çeşitli yardımcı yöntemler içerir.
    """
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text)
    type = db.Column(db.String(20), default='str')
    category = db.Column(db.String(64), default='general')
    description = db.Column(db.String(255))

    @classmethod
    def get(cls, key, default=None):
        """
        classmethod get metodu, ayarları sorgulayıp anahtar değeri ile eşleşen ayarı döndürmek için kullanılır.
        Ayarlara karşılık gelen değer, ayarın türüne göre uygun şekilde dönüştürülür. Eğer herhangi bir eşleşen
        ayar bulunmazsa varsayılan değer döndürülür.

        Parameters:
            key (str): Aranan ayarın anahtar değeri.
            default (Optional[Any]): Ayar bulunamadığında döndürülecek olan varsayılan değer.

        Returns:
            Any: Anahtar ile eşleşen ayarın değeri, ayar bulunamazsa varsayılan değer döner.
        """
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
        """
        Sınıfın ayarlarını yapılandırma ve yönetme işlemleri için kullanılan bir yöntemi
        tanımlar.

        Args:
            key (str): Ayar için kullanılacak anahtar.
            value (Any): Ayar için atanacak değer.
            type (str, optional): Ayarın türünü belirtir. Varsayılan olarak None.
            category (str, optional): Ayarın kategorisini belirtir. Varsayılan olarak None.
            description (str, optional): Ayara ilişkin açıklama metni sağlar. Varsayılan
                olarak None.

        Returns:
            None
        """
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
    """
    add_ai_settings fonksiyonu, AI ile ilgili yapılandırma ayarlarını veri tabanına
    eklemek için oluşturulmuştur. Eğer belirli bir ayar veri tabanında zaten mevcut
    değilse, ayar eklenir. Mevcut ayarlara müdahale edilmez. Bu fonksiyon,
    yazılımın kullanıcı tarafından aktif edilen ya da yapılandırılan AI özelliklerini
    kullanabilmesine olanak tanır.

    Attributes:
        ai_settings (list): AI yapılandırma ayarlarını içeren bir liste. Her bir
        ayar, açıklama, tip, kategori, anahtar ve varsayılan değere sahiptir.

    Parameters:
        None

    Returns:
        None

    Raises:
        None
    """
    ai_settings = [
        {'key': 'ai_enable_features', 'value': 'True', 'type': 'bool', 'category': 'ai',
         'description': 'AI özelliklerinin kullanımını etkinleştirir'},
        {'key': 'ai_api_provider', 'value': 'gemini', 'type': 'str', 'category': 'ai',
         'description': 'AI API sağlayıcısı (sadece Gemini destekleniyor)'},
        {'key': 'ai_default_model', 'value': 'gemini-2.0-flash-lite', 'type': 'str', 'category': 'ai',
         'description': 'Varsayılan Gemini modeli'},
        {'key': 'ai_max_token_limit', 'value': '1000000000', 'type': 'int', 'category': 'ai',
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