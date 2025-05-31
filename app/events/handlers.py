# app/events/handlers.py
from app.models.badges import Badges
from app.models.badge_criteria import BadgeCriteria
from app.models.user_badges import UserBadge
from app.models.base import db
import logging
from .event_definitions import EventType
from ..models.submission import Submission

logger = logging.getLogger(__name__)

def notebook_accessed_handler(data):
    """
    notebook_accessed_handler(data)

    Belirtilen veri sözlüğünü kullanarak bir kullanıcı tarafından bir not defterine erişim 
    olduğunu kaydeder. Kullanıcı adını ve not defteri kimliğini alır ve bu bilgileri bir 
    log mesajı olarak kaydeder.

    Parameters:
        data (dict): Kullanıcı adı ("username") ve not defteri kimliğini ("notebook_id") 
        içeren bir sözlük. Varsayılan değerler olarak "bilinmeyen" atanır.
    """
    username = data.get("username", "bilinmeyen")
    notebook_id = data.get("notebook_id", "bilinmeyen")
    logger.info(f"{username} kullanıcısı {notebook_id} numaralı not defterine erişti")


def notebook_summary_viewed_handler(data):
    """
    notebook_summary_viewed_handler işlevi, kullanıcı tarafından bir not defterinin 
    özetinin görüntülenme olayını işlemektedir ve bu işlemi günlükleme (loglama) 
    yaparak kayıt altına alır.

    Arguments:
        data (dict): Kullanıcının "username" ve "notebook_id" bilgilerini içeren bir sözlük.

    Notlar:
        Eğer "username" veya "notebook_id" ilgili sözlükte bulunmuyorsa, işlev sırasıyla 
        "bilinmeyen" değerini kullanır.
    """
    username = data.get("username", "bilinmeyen")
    notebook_id = data.get("notebook_id", "bilinmeyen")
    logger.info(f"{username} kullanıcısı {notebook_id} numaralı not defterinin özetini görüntüledi")

logger = logging.getLogger(__name__)


def user_registered_handler(data):
    """
    Kullanıcı kayıt işlemi sırasında gerçekleştirilecek durumları ele alan fonksiyon.

    Bu fonksiyon, yeni kaydolan bir kullanıcı için belirli bir işlemi yürütür. Kullanıcı
    ismini loglar ve kullanıcı ID'si mevcutsa, kayıt ile ilişkili rozetlerin kontrol
    edilmesi ve verilebilmesi için uygun yöntemi çağırır.

    Args:
        data (dict): Kullanıcı ile ilgili bilgileri içeren bir sözlük. `username` ve 
            `user_id` anahtarlarını içerebilir. `username` bulunamazsa, varsayılan 
            olarak "bilinmeyen" değeri kullanılır.

    Raises:
        None
    """
    username = data.get("username", "bilinmeyen")
    user_id = data.get("user_id")

    logger.info(f"Yeni kayıt: {username}")

    # Kullanıcı ID'si varsa rozet kontrolü yap
    if user_id:
        check_and_award_badges_for_registration(user_id)


def question_solved_handler(data):
    """
    Kullanıcıların soruları çözmesi durumunda çağrılan bir olay işleyicisidir. Kullanıcının puanını günceller
    ve ilgili rozetleri değerlendirerek gereken ödülleri verir.

    Arguments:
        data (dict): İşlemle ilgili bilgileri içeren bir sözlük olup "user_id" ve "question_id" gibi anahtarlar içerir.

    Raises:
        Exception: Veri tabanı işlemleri sırasında veya diğer işlemlerde bir hata oluşursa bu durum kaydedilir.

    Returns:
        None
    """
    user_id = data.get("user_id")
    question_id = data.get("question_id", "bilinmeyen")

    # Kullanıcı adını veritabanından alalım
    username = "bilinmeyen"
    points = 0

    try:
        if user_id:
            from app.models.user import User
            from sqlalchemy import text

            # Kullanıcı bilgilerini al
            user = User.query.get(user_id)
            if user:
                username = user.username or "bilinmeyen"

            # Soru puanını al
            question_query = text("""
                                  SELECT points
                                  FROM programming_question
                                  WHERE id = :question_id
                                  """)
            question_result = db.session.execute(question_query, {'question_id': question_id}).first()

            if question_result and question_result.points:
                points = question_result.points

                # Kullanıcıya puanı ekle
                if user:
                    user.points = (user.points or 0) + points
                    db.session.add(user)
                    db.session.commit()

                    # Puan güncellendiğini bildir
                    from .event_manager import event_manager
                    event_manager.trigger_event(EventType.USER_POINTS_UPDATED, {
                        'user_id': user_id,
                        'points': user.points
                    })
    except Exception as e:
        logger.error(f"Soru çözme puan hesaplama hatası: {str(e)}")
        db.session.rollback()

    logger.info(f"{username} kullanıcısı {question_id} numaralı soruyu çözdü ve {points} puan kazandı")

    if user_id:
        # Soru çözme rozeti kontrolü
        check_and_award_badges_for_question(user_id, question_id)

        # Soru sayısı rozeti kontrolü
        check_and_award_badges_for_question_count(user_id)


def points_updated_handler(data):
    """
    Points updated handler fonksiyonu.

    Bu fonksiyon, belirli bir kullanıcının puanlarının güncellenmesi durumunda çağrılır ve ilgili
    rozeti kazanıp kazanmadığını kontrol eder. Fonksiyon herhangi bir dönüş değeri sağlamaz.

    Args:
        data (dict): Güncellenen veri sözlüğü. Bu sözlükte, puanı güncellenen kullanıcıya
        ilişkin bilgiler yer alır. 'user_id' anahtarı ile kullanıcı kimliği belirtilirken,
        'points' anahtarı ile kullanıcının yeni puan değeri sağlanır.
        Varsayılan olarak 'points' değeri 0'dır.

    Raises:
        Bu fonksiyon doğrudan bir hata yükseltmez ancak dolaylı hatalar, rozet kontrolü
        yapılan `check_and_award_badges_for_points` fonksiyonundan gelebilir.
    """
    user_id = data.get("user_id")
    points = data.get("points", 0)

    if user_id:
        check_and_award_badges_for_points(user_id, points)


# ----- Badge verme yardımcı fonksiyonları -----

def award_badge(user_id, badge_id):
    """
    Kullanıcıya bir rozet verme işlemini gerçekleştirir. Verilen rozetin daha önce
    kullanıcıya atanıp atanmadığını kontrol eder. Eğer rozet daha önce kullanıcıya
    atanmadıysa, rozet atama işlemini tamamlar, ardından ilgili bir olayı tetikler.
    İşlem sırasında bir hata oluşursa, hata günlüğe kaydedilir ve işlem geri alınır.

    Args:
        user_id (int): Rozetin atanacağı kullanıcının kimliği.
        badge_id (int): Atanacak rozeti temsil eden kimlik.

    Returns:
        bool: Rozetin başarılı bir şekilde atanıp atanmadığını belirten bir sonuç.
        Eğer rozet daha önce kullanıcıya atanmışsa ya da bir hata oluşmuşsa
        False döner, aksi durumda True döner.
    """
    try:
        # Rozet daha önce verilmiş mi kontrol et
        existing = UserBadge.query.filter_by(user_id=user_id, badge_id=badge_id).first()
        if existing:
            return False

        # Rozeti ver
        user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
        db.session.add(user_badge)
        db.session.commit()

        # Rozet verildiğine dair event tetikle
        badge = Badges.query.get(badge_id)
        from .event_manager import event_manager
        event_manager.trigger_event(EventType.BADGE_AWARDED, {
            "user_id": user_id,
            "badge_id": badge_id,
            "badge_name": badge.name if badge else "Bilinmeyen rozet"
        })

        return True
    except Exception as e:
        logger.error(f"Rozet verme hatası: {str(e)}")
        db.session.rollback()
        return False


def check_and_award_badges_for_registration(user_id):
    """
    Bu fonksiyon, kullanıcının kayıt işlemi sırasında belirli rozet kriterlerini karşılayıp
    karşılamadığını kontrol eder ve uygun rozetleri verir.

    Args:
        user_id: Rozet verilecek olan kullanıcının kimlik numarası.

    Returns:
        None
    """
    registration_criteria = BadgeCriteria.query.filter_by(
        criteria_type=BadgeCriteria.TYPE_REGISTRATION
    ).all()

    for criteria in registration_criteria:
        award_badge(user_id, criteria.badge_id)


def check_and_award_badges_for_question(user_id, question_id):
    """
    Belirli bir soru ve kullanıcı için kriterleri kontrol edip uygun olan rozetleri kullanıcıya
    verir. Rozet kriterleri, BadgeCriteria modelinden çekilerek her biri doğrulanır ve sağlanan
    koşullara uygun olduğu durumda kullanıcıya ilgili rozet atanır.

    Args:
        user_id (int): Rozet verilecek kullanıcının benzersiz kimliği.
        question_id (int): Kontrol edilecek sorunun benzersiz kimliği.

    Returns:
        None

    Raises:
        None
    """
    question_criteria = BadgeCriteria.query.filter_by(
        criteria_type=BadgeCriteria.TYPE_QUESTION_SOLVED
    ).all()

    for criteria in question_criteria:
        value = criteria.get_value()
        # Liste kontrolü
        if isinstance(value, list) and str(question_id) in map(str, value):
            award_badge(user_id, criteria.badge_id)
        # Tek değer kontrolü
        elif str(value) == str(question_id):
            award_badge(user_id, criteria.badge_id)

def check_and_award_badges_for_question_count(user_id):
    """
    Bu fonksiyon, bir kullanıcının doğru çözdüğü soruların sayısına bağlı olarak, bu kriteri
    karşılayan rozetleri kazandırır.

    Parameters
    ----------
    user_id : int
        Rozet kazanımı için değerlendirilecek kullanıcının kimlik numarası.

    Notes
    -----
    - Kullanıcının doğru çözdüğü benzersiz soruların sayısı veri tabanından sorgulanır.
    - Rozet kriterleri veri tabanından alınır ve kullanıcının çözüm sayısıyla karşılaştırılır.
    - Kriterler karşılandığı takdirde ilgili rozet kullanıcıya atanır.
    """
    # Doğru çözülmüş benzersiz soruların sayısını al
    solved_count = db.session.query(Submission.question_id)\
        .filter(Submission.user_id == user_id, Submission.is_correct == True)\
        .distinct().count()

    # Soru sayısı kriterlerini kontrol et
    count_criteria = BadgeCriteria.query.filter_by(
        criteria_type=BadgeCriteria.TYPE_QUESTIONS_COUNT
    ).all()

    for criteria in count_criteria:
        threshold = int(criteria.get_value() or 0)
        if solved_count >= threshold:
            award_badge(user_id, criteria.badge_id)


def check_and_award_badges_for_points(user_id, points):
    """
    Bir kullanıcının aldığı puanlara göre rozet ödüllerini kontrol eder ve uygun rozetleri
    kazandırır. Rozet ödüllerini belirlemek için puan eşiklerini denetler.


    Parameters:
        user_id (int): Rozet kontrolünün gerçekleştirileceği kullanıcının ID'si.
        points (int): Kullanıcının değerlendirme için sahip olduğu puan.

    Raises:
        ValueError: Kullanıcı ID'si veya puan değeri geçersiz ise.

    """
    point_criteria = BadgeCriteria.query.filter_by(
        criteria_type=BadgeCriteria.TYPE_POINT_THRESHOLD
    ).all()

    for criteria in point_criteria:
        threshold = int(criteria.get_value() or 0)
        if points >= threshold:
            award_badge(user_id, criteria.badge_id)


def register_default_handlers(event_manager):
    """
    register_default_handlers fonksiyonu, belirtilen bir EventManager nesnesine varsayılan
    olay işleyicilerini kaydeder. Bu işlem, belirli olay türleri için uygun işleyicilerin
    tanımlanmasını sağlar ve olayların doğru bir şekilde ele alınmasını mümkün kılar.

    Args:
        event_manager (EventManager): Olay işleyicilerinin kaydedileceği EventManager
        nesnesi.

    Raises:
        TypeError: event_manager argümanı doğru bir EventManager nesnesi değilse.

    """
    event_manager.register_handler(EventType.USER_REGISTERED, user_registered_handler)
    event_manager.register_handler(EventType.QUESTION_SOLVED, question_solved_handler)
    event_manager.register_handler(EventType.USER_POINTS_UPDATED, points_updated_handler)
    event_manager.register_handler(EventType.NOTEBOOK_ACCESSED, notebook_accessed_handler)
    event_manager.register_handler(EventType.NOTEBOOK_SUMMARY_VIEWED, notebook_summary_viewed_handler)