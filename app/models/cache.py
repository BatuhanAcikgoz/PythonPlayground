from app.models.base import db
from sqlalchemy import DateTime, func

class Cache(db.Model):
    """
    Cache sınıfı, veritabanında önbellek verilerini saklamak için kullanılır.

    Bu sınıf, belirli bir anahtar altında saklanan verileri ve bu verilerin
    oluşturulma zamanını içerir. Önbellek, sık erişilen verilerin hızlı bir şekilde
    alınmasını sağlamak için kullanılır.

    Attributes:
        id (int): Önbellek kaydı için benzersiz birincil anahtar.
        key (str): Önbellek verisinin anahtarı, benzersiz olmalıdır.
        value (str): Önbellekte saklanan veri.
        created_at (datetime): Verinin oluşturulma zamanı.
    """
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)
    expires_at = db.Column(DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Cache {self.key}>'