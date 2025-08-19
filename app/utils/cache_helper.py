import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Any
from sqlalchemy import text
from api import get_db


class CacheManager:
    @staticmethod
    def get_cache_key(prefix: str, identifier: str) -> str:
        """Cache anahtarı oluşturur"""
        key = f"{prefix}:{identifier}"
        return hashlib.md5(key.encode()).hexdigest()[:50]

    @staticmethod
    def get_cached_data(key: str, db) -> Optional[dict]:
        """Cache'den veri çeker"""
        try:
            query = text("""
                         SELECT value, expires_at
                         FROM cache
                         WHERE `key` = :key
                         """)
            result = db.execute(query, {"key": key}).first()

            if not result:
                return None

            # Expire kontrolü
            if result.expires_at and datetime.utcnow() > result.expires_at:
                # Süresi dolmuş cache'i sil
                CacheManager.delete_cache(key, db)
                return None

            return json.loads(result.value)
        except Exception as e:
            print(f"Cache okuma hatası: {str(e)}")
            return None

    @staticmethod
    def set_cache_data(key: str, data: Any, expires_in_hours: int = 1, db=None):
        """Cache'e veri kaydeder"""
        try:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            value = json.dumps(data, ensure_ascii=False, default=str)

            # Upsert query
            query = text("""
                         INSERT INTO cache (`key`, value, expires_at, created_at, updated_at)
                         VALUES (:key, :value, :expires_at, NOW(), NOW()) ON DUPLICATE KEY
                         UPDATE
                             value =
                         VALUES (value), expires_at =
                         VALUES (expires_at), updated_at = NOW()
                         """)

            db.execute(query, {
                "key": key,
                "value": value,
                "expires_at": expires_at
            })
            db.commit()

        except Exception as e:
            print(f"Cache yazma hatası: {str(e)}")
            db.rollback()

    @staticmethod
    def delete_cache(key: str, db):
        """Cache'den veri siler"""
        try:
            query = text("DELETE FROM cache WHERE `key` = :key")
            db.execute(query, {"key": key})
            db.commit()
        except Exception as e:
            print(f"Cache silme hatası: {str(e)}")
            db.rollback()