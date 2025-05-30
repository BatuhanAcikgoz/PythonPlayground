# app/models/programming_question.py
from datetime import datetime
from .base import db

class ProgrammingQuestion(db.Model):
    """
    Programlama sorularını temsil eden bir sınıf.

    Bu sınıf, bir programlama sorusunun özelliklerini ve bu soruya bağlı diğer verileri
    depolamak için tasarlanmıştır. Sorunun başlığı, zorluk seviyesi, örnek giriş-çıkış
    verileri, çözüm kodu gibi bilgileri içerir. Bu sınıf genellikle veritabanında
    programlama sorularını saklamak ve ilgili kayıtları ilişkilendirmek için kullanılır.

    Attributes:
        id (int): Soru için benzersiz bir tanımlayıcı.
        title (str): Sorunun başlığı.
        description (str): Sorunun tam açıklaması.
        difficulty (int): Sorunun zorluk seviyesi, varsayılan olarak 1'dir.
        topic (str): Sorunun ele aldığı konu/başlık.
        points (int): Sorunun çözümü için verilecek puan, varsayılan olarak 10'dur.
        example_input (str): Sorunun örnek giriş verisi.
        example_output (str): Sorunun örnek çıkış verisi.
        function_name (str): Sorunun beklediği başlıca fonksiyon ismi.
        solution_code (str): Sorunun çözüm kodu.
        test_inputs (str): Sorunun test giriş verileri.
        created_at (datetime): Sorunun oluşturulma tarihi ve saati.
        updated_at (datetime): Sorunun en son güncellenme tarihi ve saati.

    Relationships:
        submissions: Soruyla ilişkili gönderimler (Submission modeli ile ilişki).
    """
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
        """
        Represent the ProgrammingQuestion instance as a string.

        This method provides a clear, human-readable string representation of
        a ProgrammingQuestion instance, useful for debugging or logging
        purposes.

        Returns:
            str: A string representation of the ProgrammingQuestion instance
            in the format "<ProgrammingQuestion {self.title}>".
        """
        return f'<ProgrammingQuestion {self.title}>'