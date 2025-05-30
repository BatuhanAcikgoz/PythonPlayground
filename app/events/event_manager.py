# app/events/event_manager.py

import logging
from typing import Dict, List, Callable, Any
from .event_definitions import EventType

logger = logging.getLogger(__name__)


class EventManager:
    """
    EventManager sınıfı olay yönetimi için bir Singleton tasarım deseni uygular.

    EventManager sınıfı, sistemdeki olayları yönetmek, belirli olay türleri için
    hangi handler'ların çalıştırılacağını belirlemek ve olayları tetiklemek için
    kullanılır. Bu sınıf, yalnızca bir kez oluşturulabilen bir Singleton sınıfı
    olarak implement edilmiştir. Ayrıca, her bir olay türü için ilgili handler'ları
    dinamik olarak kaydetme ve çalıştırma işlevselliğine sahiptir.
    """

    _instance = None

    def __new__(cls):
        """
        Singleton tasarım deseni ile EventManager sınıfının tek bir örneğinin oluşturulmasını
        ve bu örnek üzerinden kullanıcı tanımlı olayların yönetimini sağlar.

        Attributes:
            _instance (EventManager): Sınıfın tek örneğini saklar.
            _handlers (dict): Her bir olay türü için bir dizi işlemci (handler) listesi içerir.

        Returns:
            EventManager: Sınıfın mevcut bir örneğini döner ya da bir örnek oluşturur.
        """
        if cls._instance is None:
            cls._instance = super(EventManager, cls).__new__(cls)
            cls._instance._handlers = {event_type: [] for event_type in EventType}
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Bu metod, nesnenin gerekli başlangıç durumunu ayarlamak için kullanılan yardımcı
        bir metottur. Varsayılan işleyicileri yükler ve ilgili işlemleri gerçekleştirir.
        Bu işlem, nesne kullanımına başlamadan önce yapılması gereken önemli bir
        hazırlık aşamasıdır.

        Yöntem, diğer sınırlı işlevlere bağımlıdır ve bu işlevlerin doğrudan bir
        dönüş olmayabilir.

        Raises:
            ValueError: Eğer varsayılan işleyici kaydı sırasında bir hata meydana
            gelirse bu hata oluşabilir.
        """
        from .handlers import register_default_handlers
        register_default_handlers(self)

    def register_handler(self, event_type: EventType, handler: Callable):
        """
        Belirli bir olay türü için işleyici (handler) kaydeden bir yöntemdir. Her bir olay türü için birden fazla
        işleyici kaydedilebilir. Kaydedilen işleyiciler, ilgili olay tetiklendiğinde çalıştırılacaktır.

        Args:
            event_type (EventType): İşleyici eklenecek olay türü.
            handler (Callable): Olay tetiklendiğinde çalıştırılacak işlevsel işleyici.

        Raises:
            None

        Returns:
            None
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
        logger.info(f"{event_type.name} olayı için yeni handler eklendi: {handler.__name__}")

    def trigger_event(self, event_type: EventType, data: Dict[str, Any] = None):
        """
        Belirtilen türde bir olayı tetikler ve ilgili handler'ları çalıştırır.

        Bu metod, bir olay türüne bağlı tüm kayıtlı handler'lardan başlamak üzere,
        her bir handler'ı teker teker çağırır. Eğer bir handler çalıştırılırken
        bir istisna meydana gelirse, bu bilgi kaydedilir, ancak diğer handler'ların
        çalıştırılmasına devam edilir. Eğer belirtilen olay türü için herhangi bir
        handler bulunamazsa, bir uyarı loglanır ve metod işlem yapmadan sonlanır.

        Args:
            event_type (EventType): Tetiklenecek olayın türü.
            data (Dict[str, Any], optional): Handler'lara aktarılacak ek bilgiler.
                Varsayılan olarak boş bir sözlük atanır.

        Raises:
            Exception: Herhangi bir handler çağrısı sırasında meydana gelebilecek
                istisnalar loglanır, ancak dışarıya iletilmez. Dışa aktarılabilir
                istisna durumlarını kontrol etmeniz gerekmez.
        """
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


event_manager = EventManager()