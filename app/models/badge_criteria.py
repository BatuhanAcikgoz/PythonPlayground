# app/models/badge_criteria.py
from app.models.base import db
import json


class BadgeCriteria(db.Model):
    __tablename__ = 'badge_criteria'

    id = db.Column(db.Integer, primary_key=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)

    # Kriter tipleri
    TYPE_REGISTRATION = 'registration'  # Kayıt olunca
    TYPE_POINT_THRESHOLD = 'point_threshold'  # Belirli puana ulaşınca
    TYPE_QUESTION_SOLVED = 'question_solved'  # Belirli soruyu çözünce
    TYPE_QUESTIONS_COUNT = 'questions_count'  # Belirli sayıda soru çözünce

    criteria_type = db.Column(db.String(50), nullable=False)
    criteria_value = db.Column(db.Text, nullable=True)  # JSON veya değer

    # İlişkiler
    badge = db.relationship('Badges', backref=db.backref('criteria', cascade='all, delete-orphan'))

    def set_value(self, value):
        """Değeri JSON olarak kaydet"""
        if isinstance(value, (dict, list)):
            self.criteria_value = json.dumps(value)
        else:
            self.criteria_value = str(value)

    def get_value(self):
        """Değeri uygun formatta döndür"""
        if not self.criteria_value:
            return None

        try:
            return json.loads(self.criteria_value)
        except:
            return self.criteria_value