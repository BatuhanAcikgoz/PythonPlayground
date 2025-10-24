import schedule
import time
import threading
from typing import List
from sqlalchemy import text
from app.models.base import db
from app.services.instagram_service import InstagramService


class InstagramTaskManager:
    def __init__(self):
        self.instagram_service = InstagramService()
        self.running = False
        self.thread = None

    def get_tracked_usernames(self) -> List[str]:
        """Takip edilen Instagram kullanıcılarını döndürür"""
        try:
            # Settings tablosundan Instagram kullanıcılarını al
            query = text("""
                         SELECT `value`
                         FROM settings
                         WHERE `key` = 'tracked_instagram_users'
                         """)
            result = db.session.execute(query).first()

            if result and result.value:
                # Virgülle ayrılmış kullanıcı adları
                usernames = [username.strip() for username in result.value.split(',')]
                return [username for username in usernames if username]

            return []

        except Exception as e:
            print(f"Takip edilen kullanıcılar alınırken hata: {str(e)}")
            return []

    def update_instagram_cache(self):
        """Instagram cache'ini günceller"""
        print("Instagram cache güncelleme başlatıldı...")

        try:
            tracked_usernames = self.get_tracked_usernames()

            if not tracked_usernames:
                print("Takip edilen Instagram kullanıcısı bulunamadı")
                return

            updated_count = 0
            for username in tracked_usernames:
                try:
                    # Force refresh ile yeni veriyi çek ve cache'e kaydet
                    posts = self.instagram_service.get_posts(username, db.session, force_refresh=True)
                    if posts:
                        updated_count += 1
                        print(f"✓ {username}: {len(posts)} post güncellendi")
                    else:
                        print(f"✗ {username}: Post bulunamadı")

                    # Rate limiting için 2 saniye bekle
                    time.sleep(2)

                except Exception as e:
                    print(f"✗ {username} güncellenirken hata: {str(e)}")

            print(
                f"Instagram cache güncelleme tamamlandı. {updated_count}/{len(tracked_usernames)} kullanıcı güncellendi.")

        except Exception as e:
            print(f"Instagram cache güncelleme genel hatası: {str(e)}")

    def schedule_tasks(self):
        """Görevleri zamanlar"""
        # Her saat başı Instagram cache'ini güncelle
        schedule.every().hour.at(":00").do(self.update_instagram_cache)

        # İlk çalıştırmada da güncelle
        self.update_instagram_cache()

    def run_scheduler(self):
        """Scheduler'ı çalıştırır"""
        self.running = True
        print("Instagram cron job sistemi başlatıldı...")

        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Her dakika kontrol et

    def start(self):
        """Scheduler'ı arka planda başlatır"""
        if not self.running:
            self.schedule_tasks()
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
            print("Instagram task manager başlatıldı")

    def stop(self):
        """Scheduler'ı durdurur"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("Instagram task manager durduruldu")


# Global instance
instagram_task_manager = InstagramTaskManager()