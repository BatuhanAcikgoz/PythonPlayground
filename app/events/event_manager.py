# app/events/event_manager.py

import logging
from typing import Dict, List, Callable, Any
from .event_definitions import EventType

logger = logging.getLogger(__name__)


class EventManager:
    """Olay yöneticisi sınıfı"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._handlers = {event_type: [] for event_type in EventType}
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Handler'ları başlatma"""
        # Varsayılan handler'lar burada yüklenebilir
        from .handlers import register_default_handlers
        register_default_handlers(self)

    def register_handler(self, event_type: EventType, handler: Callable):
        """Belirli bir olay türü için handler ekler"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
        logger.info(f"{event_type.name} olayı için yeni handler eklendi: {handler.__name__}")

    def trigger_event(self, event_type: EventType, data: Dict[str, Any] = None):
        """Olayı tetikleyip ilgili handler'ları çalıştırır"""
        if data is None:
            data = {}

        logger.info(f"{event_type.name} olayı tetiklendi: {data}")

        if event_type not in self._handlers:
            logger.warning(f"{event_type.name} olayı için hiç handler bulunamadı")
            return

        for handler in self._handlers[event_type]:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"{event_type.name} olayında handler hatası: {str(e)}")


# Global event manager instance
event_manager = EventManager()