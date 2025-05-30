# app/models/notebook_summary.py
from datetime import datetime
from .base import db

class NotebookSummary(db.Model):
    """
    NotebookSummary sınıfı, veritabanı için bir model tanımlar ve Jupyter Notebook'larıyla ilgili
    özet bilgileri ve açıklamaları saklamak amacıyla kullanılır.

    Bu sınıf, bir Jupyter Notebook dosyasının dosya yolu, özeti, kodların açıklamaları, son güncelleme
    tarihi ve varsa oluşabilecek hata mesajlarını veritabanında saklamak için tasarlanmıştır. Özet
    üzerinde düzenlemeler yapmak, notebook hakkında bilgi almak veya hataları incelemek için
    kullanılabilir.

    Attributes:
        id (int): Her notebook kaydı için benzersiz birincil anahtar değeri.
        notebook_path (str): Notebook dosyasının tam dosya yolu. Tekil olmalıdır ve boş bırakılamaz.
        summary (Optional[str]): Notebook içeriğinin özeti. Null olabilir.
        code_explanation (Optional[str]): Notebook'taki kodların açıklamaları. Null olabilir.
        last_updated (datetime): Kaydın son güncelleme zamanı. Varsayılan olarak mevcut zaman atanır.
        error (Optional[str]): Eğer varsa, notebook ile ilgili bir hata mesajı. Null olabilir.
    """
    id = db.Column(db.Integer, primary_key=True)
    notebook_path = db.Column(db.String(255), unique=True, nullable=False)
    summary = db.Column(db.Text, nullable=True)
    code_explanation = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    error = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """
        __repr__

        Temsil edici bir dize döndürür. Bu yöntem, NotebookSummary nesnesini anlaşılır bir
        şekilde metin biçiminde ifade etmek için kullanılır. Özellikle hata ayıklama ve
        günlük kaydı işlemleri için faydalıdır.

        Returns:
            str: NotebookSummary nesnesini temsil eden bir metin dizesi.
        """
        return f'<NotebookSummary {self.notebook_path}>'