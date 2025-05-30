# app/events/handlers.py
import logging
from .event_definitions import EventType
from app.models.badges import Badges
from app.models.badge_criteria import BadgeCriteria
from app.models.user_badges import UserBadge
from app.models.base import db
import logging
from .event_definitions import EventType
from ..models.submission import Submission

logger = logging.getLogger(__name__)

def notebook_accessed_handler(data):
    """Notebook erişildiğinde çalışacak handler"""
    username = data.get("username", "bilinmeyen")
    notebook_id = data.get("notebook_id", "bilinmeyen")
    logger.info(f"{username} kullanıcısı {notebook_id} numaralı not defterine erişti")


def notebook_summary_viewed_handler(data):
    """Notebook özeti görüntülendiğinde çalışacak handler"""
    username = data.get("username", "bilinmeyen")
    notebook_id = data.get("notebook_id", "bilinmeyen")
    logger.info(f"{username} kullanıcısı {notebook_id} numaralı not defterinin özetini görüntüledi")

logger = logging.getLogger(__name__)


def user_registered_handler(data):
    """Kullanıcı kaydolduğunda çalışacak handler"""
    username = data.get("username", "bilinmeyen")
    user_id = data.get("user_id")

    logger.info(f"Yeni kayıt: {username}")

    # Kullanıcı ID'si varsa rozet kontrolü yap
    if user_id:
        check_and_award_badges_for_registration(user_id)


def question_solved_handler(data):
    """Bir soru çözüldüğünde çalışacak handler"""
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
    """Kullanıcı puanları güncellendiğinde çalışacak handler"""
    user_id = data.get("user_id")
    points = data.get("points", 0)

    if user_id:
        check_and_award_badges_for_points(user_id, points)


# ----- Badge verme yardımcı fonksiyonları -----

def award_badge(user_id, badge_id):
    """Kullanıcıya rozet verir. Zaten verilmişse işlem yapmaz."""
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
    """Kayıt olma rozetlerini kontrol eder ve verir"""
    registration_criteria = BadgeCriteria.query.filter_by(
        criteria_type=BadgeCriteria.TYPE_REGISTRATION
    ).all()

    for criteria in registration_criteria:
        award_badge(user_id, criteria.badge_id)


def check_and_award_badges_for_question(user_id, question_id):
    """Belirli soru çözme rozetlerini kontrol eder ve verir"""
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
    """Çözülen soru sayısı rozetlerini kontrol eder ve verir"""
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
    """Puan eşiği rozetlerini kontrol eder ve verir"""
    point_criteria = BadgeCriteria.query.filter_by(
        criteria_type=BadgeCriteria.TYPE_POINT_THRESHOLD
    ).all()

    for criteria in point_criteria:
        threshold = int(criteria.get_value() or 0)
        if points >= threshold:
            award_badge(user_id, criteria.badge_id)


def register_default_handlers(event_manager):
    """Varsayılan handler'ları event manager'a kaydeder"""
    event_manager.register_handler(EventType.USER_REGISTERED, user_registered_handler)
    event_manager.register_handler(EventType.QUESTION_SOLVED, question_solved_handler)
    event_manager.register_handler(EventType.USER_POINTS_UPDATED, points_updated_handler)
    event_manager.register_handler(EventType.NOTEBOOK_ACCESSED, notebook_accessed_handler)
    event_manager.register_handler(EventType.NOTEBOOK_SUMMARY_VIEWED, notebook_summary_viewed_handler)