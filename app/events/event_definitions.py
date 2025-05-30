# app/events/event_definitions.py
from enum import Enum, auto

class EventType(Enum):
    """
    EventType sınıfı, farklı olay türlerini temsil etmek için kullanılan bir enum sınıfıdır.

    Bu sınıf, genellikle bir sistemde meydana gelen olayların belirli bir türünü tanımlamak ve
    bu türlere göre işlem yapmak için kullanılır. Örneğin, kullanıcı kaydı, giriş yapma, bir
    sorunun çözülmesi gibi olay türlerini ayırt etmek adına kullanılabilir. Her olay türü için
    bir enum öğesi tanımlanmıştır, böylece kullanımı hem tutarlı hem de daha anlaşılır hale
    gelmiştir.
    """
    USER_REGISTERED = auto()
    USER_LOGGED_IN = auto()
    QUESTION_SOLVED = auto()
    NOTEBOOK_ACCESSED = auto()
    NOTEBOOK_SUMMARY_VIEWED = auto()
    BADGE_AWARDED = auto()
    USER_POINTS_UPDATED = auto()