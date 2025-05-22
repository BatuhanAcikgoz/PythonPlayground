# app/events/event_definitions.py
from enum import Enum, auto

class EventType(Enum):
    """Sistem içindeki olayların tanımlanması"""
    USER_REGISTERED = auto()
    USER_LOGGED_IN = auto()
    QUESTION_SOLVED = auto()
    NOTEBOOK_ACCESSED = auto()
    NOTEBOOK_SUMMARY_VIEWED = auto()
    # Yeni event tipi
    BADGE_AWARDED = auto()  # Rozet verildiğinde
    USER_POINTS_UPDATED = auto()  # Puanlar güncellendiğinde