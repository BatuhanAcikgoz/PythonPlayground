# app/models/notebook_summary.py
from datetime import datetime
from .base import db

class NotebookSummary(db.Model):
    __tablename__ = 'notebook_summaries'

    id = db.Column(db.Integer, primary_key=True)
    notebook_path = db.Column(db.String(255), unique=True, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    code_explanation = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    error = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<NotebookSummary {self.notebook_path}>'