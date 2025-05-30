# app/models/submission.py
from datetime import datetime
import json
from app.models.base import db
from flask_login import current_user

class Submission(db.Model):
    """
    Submission sınıfı, kullanıcıların bir soruya göndermiş olduğu çözüm kodlarının
    veritabanında saklanması ve yönetilmesi için bir model sağlar.

    Bu sınıf, kullanıcıların herhangi bir programlama sorusuna yüklediği kod çözümünü,
    bu çözümün test sonuçlarını ve başarı durumunu barındırır. Aynı zamanda kullanıcıya
    ait belirli sorular için doğru çözümün olup olmadığını kontrol etmek için de araçlar
    sunar.

    Attributes:
        id: Her gönderim için benzersiz bir tanımlayıcı.
        user_id: Gönderimi yapan kullanıcının ID değeri.
        question_id: Çözümün ilişkilendirildiği sorunun ID değeri.
        code: Kullanıcının gönderdiği çözümün kaynak kodu.
        is_correct: Çözümün doğru olup olmadığını belirten bayrak.
        test_results: Çözüm için yapılan testlerin sonuçları. JSON formatındadır.
        execution_time: Gönderimin testlerde çalıştırılma süresi.
        error_message: Test sırasında oluşan hata mesajları.
        created_at: Gönderimin oluşturulma tarihi ve saati.

    Attributes (Relationships):
        user: Gönderimi gerçekleştiren kullanıcı ile ilişki sağlar.

    Methods:
        save_submission: Yeni bir gönderimi veritabanına kaydeder.
        has_correct_submission: Belirli bir kullanıcı ve sorunun doğru çözüm gönderimini
                                olup olmadığını kontrol eder.
        result_summary: Gönderim için test sonuçlarının özet bilgisini döner.
    """
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
        """
        Provides a string representation of the Submission object for easier debugging
        and output formatting. The returned string contains the Submission ID, the User ID
        associated with the submission, and the Question ID for which the submission was made.

        Returns:
            str: The string representation of the Submission instance.
        """
        return f'<Submission {self.id} by User {self.user_id} for Question {self.question_id}>'

    def __init__(self, **kwargs):
        """
        Submission sınıfının bir örneğini başlatmak için kullanılan yapılandırıcıdır.
        Bu yapılandırıcı, verilen anahtar kelime argümanlarını işler ve test_results adlı
        bir anahtar varsa, bunun bir sözlük olup olmadığını kontrol eder. Eğer bir sözlük ise,
        JSON formatına dönüştürür ve parent class'ın yapılandırıcısına aktarır.

        Args:
            kwargs: Anahtar kelime argümanları. `test_results` anahtarı sözlük ise JSON
            formatına dönüştürülür.

        """
        # test_results dictionary ise JSON'a dönüştür
        if 'test_results' in kwargs and isinstance(kwargs['test_results'], dict):
            kwargs['test_results'] = json.dumps(kwargs['test_results'])

        super(Submission, self).__init__(**kwargs)

    @classmethod
    def save_submission(cls, question, code, evaluation_result):
        """
        Bir SQLAlchemy modeli kullanarak bir kod gönderimini kaydeder. Bu metod, bir kullanıcı tarafından
        gerçekleştirilen kod gönderiminin veritabanına kaydedilmesini sağlar. Gönderim bilgileri, kod
        değerlendirme sonuçları, yürütme süresi ve hatalar gibi detayları içerir.

        Args:
            question (Question): Kullanıcı tarafından çözülmeye çalışılan soru nesnesi.
            code (str): Gönderilen kod.
            evaluation_result (dict): Kodun değerlendirilmesi sırasında alınan sonuçlar. Bu sözlük 'is_correct',
                                       'execution_time' ve 'error_message' gibi anahtarları içerir.

        Returns:
            Submission: Yeni kaydedilen gönderim nesnesi.
        """
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
        Checks if a user has a correct submission for a specific question.

        This class method determines whether there exists at least one correct
        submission for a given user and question combination. The correctness
        of the submission is verified by the `is_correct` flag in the database
        record.

        Parameters:
            user_id (int): The ID of the user.
            question_id (int): The ID of the question.

        Returns:
            bool: True if a correct submission exists for the user and question,
            False otherwise.
        """
        return cls.query.filter_by(
            user_id=user_id,
            question_id=question_id,
            is_correct=True
        ).first() is not None

    @property
    def result_summary(self):
        """
        result_summary özelliği, bir dizi test sonucunu değerlendirerek özet bir sonuç döndürmek için kullanılır.

        Attributes:
            None

        Returns:
            str: Eğer test sonuçları mevcut değilse "Sonuç bulunamadı" mesajını döndürür. Test sonuçları JSON formatında düzgün
            işlenebilirse ve tüm testler başarılıysa "Tüm testler başarılı" mesajını döndürür. Eğer başarısız testler varsa,
            başarısız test sayısını içeren bir mesaj döner, örneğin: "2 test başarısız". JSON yükleme işlemi sırasında hata
            oluşursa "Sonuç ayrıştırılamadı" döndürür.
        """
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