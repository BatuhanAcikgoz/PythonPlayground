# app/models/submission.py
from datetime import datetime
import json
from app.models.base import db
from flask_login import current_user

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('programming_question.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)
    test_results = db.Column(db.Text)
    execution_time = db.Column(db.Float)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # İlişkiler
    user = db.relationship('User', backref=db.backref('submissions', lazy=True))

    def __repr__(self):
        return f'<Submission {self.id} by User {self.user_id} for Question {self.question_id}>'

    def __init__(self, **kwargs):
        # test_results dictionary ise JSON'a dönüştür
        if 'test_results' in kwargs and isinstance(kwargs['test_results'], dict):
            kwargs['test_results'] = json.dumps(kwargs['test_results'])

        super(Submission, self).__init__(**kwargs)

    @classmethod
    def save_submission(cls, question, code, evaluation_result):
        submission = cls(
            user_id=current_user.id,
            question_id=question.id,
            code=code,
            is_correct=evaluation_result['is_correct'],
            test_results=evaluation_result,
            execution_time=evaluation_result.get('execution_time', 0),
            error_message=evaluation_result.get('error_message', ''),
        )
        db.session.add(submission)
        db.session.commit()
        return submission

    @classmethod
    def has_correct_submission(cls, user_id, question_id):
        """
        Kullanıcının belirli bir soru için doğru çözüm gönderip göndermediğini kontrol eder
        """
        return cls.query.filter_by(
            user_id=user_id,
            question_id=question_id,
            is_correct=True
        ).first() is not None

    @property
    def result_summary(self):
        """Test sonuçlarının özeti"""
        if not self.test_results:
            return "Sonuç bulunamadı"

        try:
            results = json.loads(self.test_results)
            if self.is_correct:
                return "Tüm testler başarılı"

            failed_count = 0
            if 'errors' in results and results['errors']:
                failed_count = len([e for e in results['errors'] if e.startswith("Test başarısız:")])

            return f"{failed_count} test başarısız"
        except:
            return "Sonuç ayrıştırılamadı"