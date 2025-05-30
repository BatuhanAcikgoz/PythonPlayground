from app.models.base import db
from enum import Enum


class CriteriaType(Enum):
    """
    CriteriaType, ödüllendirme kriterlerini temsil eden enum sınıfıdır.

    Bu sınıf, belirli ödüllendirme kriterlerini tanımlamak ve sınıflandırmak amacıyla
    kullanılır. Enum yapısı ile farklı kriter türlerini sembolik isimler aracılığıyla
    ifade eder.
    """
    TYPE_REGISTRATION = "registration"
    TYPE_POINT_THRESHOLD = "point_threshold"
    TYPE_QUESTION_SOLVED = "question_solved"
    TYPE_QUESTIONS_COUNT = "questions_count"


class BadgeCriteria(db.Model):
    """
    BadgeCriteria sınıfı kriterleri tanımlar ve işlemlerini gerçekleştirir.

    Bu sınıf, ödül sisteminde kullanılan kriterlerin tanımlanmasını ve işlenmesini sağlar. Farklı
    kriter tipleri (örneğin, kayıt, puan eşiği, çözülmüş soru vb.) için gerekli bilgilerin
    saklanması ve bu kriterlerin bir kullanıcı tarafından karşılanıp karşılanmadığının kontrol
    edilmesi gibi işlemleri gerçekleştirir. Ayrıca badge nesneleri ile ilişkilidir.

    Attributes:
        TYPE_REGISTRATION: str
            Kullanıcı kaydı üzerine bir kriteri temsil eder.
        TYPE_POINT_THRESHOLD: str
            Kullanıcının belirli bir puan eşiğini geçmesini gerektiren bir kriteri temsil eder.
        TYPE_QUESTION_SOLVED: str
            Kullanıcının belirli bir soruyu çözmesini gerektiren bir kriteri temsil eder.
        TYPE_QUESTIONS_COUNT: str
            Kullanıcının belirli sayıda soru çözmesini gerektiren bir kriteri temsil eder.
        id: int
            Kriterin benzersiz kimliği.
        badge_id: int
            Kriterin bağlı olduğu badge'in kimliği.
        criteria_type: str
            Kriter tipi.
        criteria_value: str
            Kriter için gereken eşik ya da değer.
        created_at: datetime
            Kriterin oluşturulduğu tarih ve saat.
        updated_at: datetime
            Kriterin güncellendiği tarih ve saat.
        badge: Badges
            Kriterin ilişkilendirildiği badge nesnesi.
    """
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
        """
        __repr__ özel metodu, BadgeCriteria nesnesinin metinsel temsili için özelleştirilmiş
        bir string döndürür. Bu, genellikle nesnenin okunabilir bir özetini sağlar ve hata
        ayıklama veya kayıt işlemleri sırasında kullanışlıdır.

        Returns:
            str: BadgeCriteria nesnesini temsil eden özelleştirilmiş string.
        """
        return f'<BadgeCriteria {self.criteria_type} for Badge {self.badge_id}>'

    def is_satisfied_by(self, user):
        """
        Belirli bir kullanıcı ve kriter türüne göre kriterin sağlanıp sağlanmadığını kontrol eder.

        Bu metod, farklı kriter türleri ve değerlerini temel alarak, bir kullanıcının belirli koşulları
        sağlayıp sağlamadığını değerlendirir. Değerlendirme işlemi kullanıcının verisine ve ilgili
        kriterin belirttiği koşullara bağlıdır.

        Args:
            user (User): Kriter değerlendirilirken kontrol edilecek kullanıcının örneği.

        Returns:
            bool: Sağlanan kriteri kullanıcının karşılayıp karşılamadığına bağlı olarak True veya False döner.
        """
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
        """
        Bu yöntem, `criteria_value` özelliğinin değerini döndürmek için
        kullanılır. Özellik, sınıf içindeki belirli bir kriterin değerini
        temsil eder ve bu değer çağrıldığında erişilebilir hale gelir.

        Returns:
            Any: `criteria_value` özelliğinin değeri.
        """
        return self.criteria_value

    def get_value(self):
        """
        Bu fonksiyon, bir nesne içinde yer alan 'criteria_value' özelliğini kontrol ederek dönüş
        değerini belirler. Eğer 'criteria_value' özelliği bir tamsayıya dönüştürülebiliyorsa bu
        tamsayı değeri döndürülür. Aksi takdirde 'criteria_value' olduğu gibi döndürülür. Eğer
        'criteria_value' None ise None değerini döndürür.

        Returns:
            int | str | None: Fonksiyon, 'criteria_value' özelliğini tamsayıya dönüştürebilirse
            bir tamsayı değer döndürür, dönüştürmeyi başaramazsa string değer döndürür. Eğer
            'criteria_value' None ise None döner.
        """
        if self.criteria_value:
            try:
                return int(self.criteria_value)
            except ValueError:
                return self.criteria_value
        return None