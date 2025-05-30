# app/models/programming_question.py
from datetime import datetime
from .base import db

class ProgrammingQuestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, default=1)
    topic = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=10)
    example_input = db.Column(db.Text)
    example_output = db.Column(db.Text)
    function_name = db.Column(db.String(100), nullable=False)
    solution_code = db.Column(db.Text, nullable=False)
    test_inputs = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submissions = db.relationship('Submission', backref='question', lazy=True)

    def __repr__(self):
        return f'<ProgrammingQuestion {self.title}>'