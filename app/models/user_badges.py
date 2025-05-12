# app/models/user_badges.py
from app.models.base import db
from datetime import datetime


class UserBadge(db.Model):
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