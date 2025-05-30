# app/models/user_badges.py
from app.models.base import db
from datetime import datetime


class UserBadge(db.Model):
    """
    UserBadge modelini temsil eder.

    Bu sınıf, kullanıcıların aldığı rozet bilgilerini tutmak için bir veri modelini sağlar. Kullanıcı ve rozet
    ilişkilerini temsil eden bir ara tablo olarak çalışır ve kullanıcıların hangi rozetleri aldığını takip eder. Her
    bir kayıt, bir kullanıcının belirli bir rozeti aldığı tarihi ve ilişkili bilgiyi içerir. Kullanıcı ve rozetler
    arasında bireysel olmayan bir ilişki kurar.

    Attributes:
        id (int): UserBadge tablosundaki benzersiz kimlik numarasını temsil eder.
        user_id (int): Bu UserBadge kaydına ait kullanıcının kimlik numarası (foreign key).
        badge_id (int): Bu UserBadge kaydına ait rozetin kimlik numarası (foreign key).
        awarded_at (datetime): Rozetin kullanıcıya verildiği tarih ve saat bilgisi.

    Table Constraints:
        uix_user_badge: user_id ve badge_id kombinasyonunun benzersizliği sağlanır.
    """
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 'users' yerine 'user'
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # İlişkiler
    user = db.relationship('User', backref=db.backref('badges', lazy='dynamic'))
    badge = db.relationship('Badges', backref=db.backref('users', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='uix_user_badge'),
    )