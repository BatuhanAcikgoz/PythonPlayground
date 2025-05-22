from app.models.base import db
from enum import Enum


class CriteriaType(Enum):
    TYPE_REGISTRATION = "registration"
    TYPE_POINT_THRESHOLD = "point_threshold"
    TYPE_QUESTION_SOLVED = "question_solved"
    TYPE_QUESTIONS_COUNT = "questions_count"


class BadgeCriteria(db.Model):
    __tablename__ = 'badge_criteria'

    TYPE_REGISTRATION = "registration"
    TYPE_POINT_THRESHOLD = "point_threshold"
    TYPE_QUESTION_SOLVED = "question_solved"
    TYPE_QUESTIONS_COUNT = "questions_count"

    id = db.Column(db.Integer, primary_key=True)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id', ondelete='CASCADE'), nullable=False)
    criteria_type = db.Column(db.String(50), nullable=False)
    criteria_value = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # İlişkiler
    badge = db.relationship('Badges', backref=db.backref('criteria', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<BadgeCriteria {self.criteria_type} for Badge {self.badge_id}>'

    def is_satisfied_by(self, user):
        """Kullanıcının bu kriteri karşılayıp karşılamadığını kontrol eder"""
        from app.models.user import User
        from app.models.submission import Submission
        from sqlalchemy import func

        if not isinstance(user, User):
            return False

        if self.criteria_type == CriteriaType.TYPE_REGISTRATION.value:
            # Kullanıcı kayıtlı ise kriter karşılanmıştır
            return True

        elif self.criteria_type == CriteriaType.TYPE_POINT_THRESHOLD.value:
            # Kullanıcının puanı, kriter değerinden büyükse kriter karşılanmıştır
            try:
                point_threshold = int(self.criteria_value)
                return user.points >= point_threshold
            except (ValueError, TypeError):
                return False

        elif self.criteria_type == CriteriaType.TYPE_QUESTION_SOLVED.value:
            # Kullanıcı belirli soruyu çözmüş mü kontrol edilir
            try:
                question_id = int(self.criteria_value)
                return Submission.query.filter_by(
                    user_id=user.id,
                    question_id=question_id,
                    is_correct=True
                ).first() is not None
            except (ValueError, TypeError):
                return False

        elif self.criteria_type == CriteriaType.TYPE_QUESTIONS_COUNT.value:
            # Kullanıcı belirli sayıda soruyu çözmüş mü kontrol edilir
            try:
                questions_count = int(self.criteria_value)
                solved_count = Submission.query.filter_by(
                    user_id=user.id,
                    is_correct=True
                ).with_entities(func.count(func.distinct(Submission.question_id))).scalar()
                return solved_count >= questions_count
            except (ValueError, TypeError):
                return False

        return False

    def get_criteria_value(self):
        """Kriter değerini döndürür"""
        return self.criteria_value

    def get_value(self):
        """Kriter değerini döndürür"""
        if self.criteria_value:
            try:
                return int(self.criteria_value)
            except ValueError:
                return self.criteria_value
        return None