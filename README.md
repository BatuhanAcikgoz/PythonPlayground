# 🚀 PythonPlayground: İnteraktif Python Konsolu ve Eğitim Platformu

<div align="center">
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+"/>
    <img src="https://img.shields.io/badge/Flask-3.1.0-green.svg" alt="Flask 3.1.0"/>
    <img src="https://img.shields.io/badge/FastAPI-0.110.0-teal.svg" alt="FastAPI 0.110.0"/>
    <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker Ready"/>
    <img src="https://img.shields.io/badge/Status-Geliştiriliyor-orange.svg" alt="Status: Geliştiriliyor"/>
  </p>
</div>

Bu web uygulaması, GitHub deposunda saklanan Jupyter notebook'larını görüntülemenizi ve çalıştırmanızı sağlar AI özetleri ile daha hızlı python öğrenmenize yardımcı olur. AI tarafından hazırlanan python sorulari ile bilginizi pekiştirebilirsiniz ve diğer kullanıcılarla yarışabilirsiniz.

![PythonPlayground Demo](https://via.placeholder.com/800x450.png?text=PythonPlayground+Demo)

## 📑 İçindekiler
- [🌟 Özellikler](#-özellikler)
- [🔧 Kurulum](#-kurulum)
- [🐳 Docker ile Deployment](#-docker-ile-deployment)
- [🚦 Kullanım](#-kullanım)
- [📁 Proje Yapısı](#-proje-yapısı)
- [⚡ FastAPI Entegrasyonu](#-fastapi-entegrasyonu)
- [🔌 API Endpointleri](#-api-endpointleri)
- [🛠️ Teknik Gereksinimler](#️-teknik-gereksinimler)
- [❓ Sık Sorulan Sorular](#-sık-sorulan-sorular)
- [👥 Katkıda Bulunma](#-katkıda-bulunma)
- [📄 Lisans](#-lisans)

## 🌟 Temel Özellikler

### 🎓 **Eğitim Yönetimi**
- **Jupyter Notebook Entegrasyonu**: GitHub'dan otomatik çekme ve senkronizasyon
- **İnteraktif Kod Editörü**: Gerçek zamanlı Python kodu çalıştırma
- **AI Destekli Soru Üretimi**: Otomatik programlama soruları ve çözümleri
- **Notebook Özetleme**: AI ile otomatik ders özetleri

### 👥 **Kullanıcı Yönetimi**
- **Rol Tabanlı Erişim**: Öğrenci, Öğretmen, Admin rolleri
- **Kapsamlı Profil Sistemi**: İlerleme takibi ve istatistikler
- **Güvenli Kimlik Doğrulama**: Flask-Login entegrasyonu
- **Çoklu Dil Desteği**: Türkçe ve İngilizce arayüz

### 🏆 **Gamification & Motivasyon**
- **Rozet Sistemi**: Başarılar için özel rozetler
- **Puan Sistemi**: Aktivite bazlı puan kazanımı
- **Liderlik Tablosu**: Kullanıcı sıralamaları
- **İlerleme Takibi**: Detaylı analitik dashboard

### 💻 **Teknik Özellikler**
- **WebSocket Desteği**: Gerçek zamanlı etkileşim
- **Responsive Tasarım**: Mobil uyumlu arayüz
- **API İntegrasyonu**: RESTful API ve FastAPI backend
- **Güvenlik**: CSRF koruması ve güvenli kod çalıştırma

## 🎯 Detaylı Özellikler

### 📚 **Notebook ve İçerik Yönetimi**

#### Otomatik İçerik Senkronizasyonu
- GitHub repository'lerinden otomatik notebook çekme
- Değişiklik algılama ve güncelleme
- Sürüm kontrolü ve geri alma özellikleri
- Batch işleme ile performans optimizasyonu

#### AI Destekli İçerik Üretimi
- **Otomatik Soru Üretimi**: Zorluk seviyelerine göre programlama soruları
- **Notebook Özetleme**: AI ile ders içeriği özetleri
- **Kod Analizi**: Otomatik kod kalitesi değerlendirmesi
- **Öneri Sistemi**: Kişiselleştirilmiş öğrenme önerileri

### 🎮 **İnteraktif Kod Çalıştırma**

#### Güvenli Kod Ortamı
- Sandbox ortamda Python kodu çalıştırma
- Zaman aşımı ve kaynak limitasyonları
- Hata yakalama ve detaylı debugging
- Çıktı formatlaması ve görselleştirme

#### Gerçek Zamanlı Etkileşim
- WebSocket ile anında sonuç alma
- Çoklu kullanıcı desteği
- Collaborative coding özelliği
- Live code sharing

### 🏅 **Gelişmiş Gamification**

#### Rozet Sistemi
- **Başlangıç Rozetleri**: İlk adımlar için
- **Öğrenme Rozetleri**: Ders tamamlama
- **Beceri Rozetleri**: Özel yetenekler
- **Sosyal Rozetler**: Topluluk katkısı

#### Puan ve Seviye Sistemi
- Aktivite bazlı puan kazanımı
- Günlük/haftalık hedefler
- Seviye atlama ödülleri
- Bonus puan etkinlikleri

#### Liderlik ve Rekabet
- Genel liderlik tablosu
- Kategori bazlı sıralamalar
- Haftalık/aylık turnuvalar
- Takım bazlı yarışmalar

### 📊 **Analitik ve Raporlama**

#### Öğrenci Analitiği
- Detaylı ilerleme raporu
- Zaman bazlı aktivite analizi
- Güçlü/zayıf yönler analizi
- Kişiselleştirilmiş öneriler

#### Öğretmen Dashboard'u
- Sınıf performans analizi
- Öğrenci ilerleme takibi
- Eksik konular tespiti
- Otomatik raporlama

## 🔧 Kurulum

### Ön Gereksinimler
- Python 3.8 veya daha yeni bir sürüm
- MySQL 5.7+ veya MariaDB 10.5+
- Git (notebook repo'larını çekmek için)

### Adımlar

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/BatuhanAcikgoz/PythonPlayground.git
   cd PythonPlayground
   ```

2. Sanal ortam oluşturun (opsiyonel ama önerilir):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. MySQL veritabanını kurun:
   ```bash
   # 'python_platform' adında bir veritabanı oluşturun
   mysql -u root -p
   CREATE DATABASE python_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. Yapılandırma dosyasını düzenleyin:
   ```bash
   cp config.example.py config.py
   # config.py dosyasını açın ve veritabanı bilgilerinizi girin
   ```

6. Veritabanı tablolarını oluşturun:
   ```bash
   python manage.py create_tables
   ```

7. Uygulamayı başlatın:
   ```bash
   # Flask uygulaması için
   python app.py
   
   # FastAPI uygulaması için (ayrı bir terminalde)
   python api.py
   ```

## 🐳 Docker ile Deployment

PythonPlayground'u hızlıca ve tutarlı bir şekilde deploy etmek için Docker kullanabilirsiniz:

### Docker Compose ile Kurulum

1. Docker ve Docker Compose'un yüklü olduğundan emin olun
2. Repo kök dizininde docker-compose.yml dosyasını kullanarak:

```bash
# Tüm servisleri başlatmak için
docker-compose up -d

# Logları görmek için
docker-compose logs -f

# Servisleri durdurmak için
docker-compose down
```

### Docker Compose Yapısı

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
      - fastapi
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql://user:password@db:3306/python_platform
    volumes:
      - ./logs:/app/logs
    restart: always

  db:
    image: mariadb:10.5
    volumes:
      - db_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=python_platform
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    restart: always

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "7923:7923"
    restart: always

volumes:
  db_data:
```

### Docker Optimizasyonu

PythonPlayground Docker container'ları, üretim ortamı için optimize edilmiştir:

- Multi-stage builds ile küçük image boyutu
- Health check ile container durumu izleme
- Volume kullanımı ile veri kalıcılığı
- Güvenlik iyileştirmeleri
- Auto-restart politikaları

## 🚦 Kullanım

### Hızlı Başlangıç
- Tarayıcıda Flask uygulaması için `http://localhost:5000` adresine gidin
- FastAPI Swagger belgeleri için `http://localhost:7923/docs` adresini ziyaret edin
- Admin hesabıyla giriş yapın: `admin@example.com / admin123`

### Kullanıcı Türleri ve Yetkiler

| Rol | Yetkiler |
|-----|----------|
| **Öğrenci** | Notebook'ları görüntüleme, kodu çalıştırma, yorumlar yazma |
| **Öğretmen** | Öğrencilere ek olarak, notebook oluşturma ve düzenleme, ödev verme |
| **Admin** | Tüm yetkiler + kullanıcı yönetimi, rol atama, sistem ayarları |

### Örnek İş Akışı
1. Giriş yapın veya yeni bir hesap oluşturun
2. Ana sayfadan bir kurs veya notebook seçin
3. "Çalıştır" butonuna tıklayarak interaktif konsolu açın
4. Kod yazın ve gerçek zamanlı çıktıyı görün

## 📁 Proje Yapısı

```
PythonPlayground/
├── app/                          # Ana uygulama paketi
│   ├── models/                   # Veritabanı modelleri
│   │   ├── user.py              # Kullanıcı ve rol modelleri
│   │   ├── user_badges.py       # Kullanıcı rozet modeli
│   │   ├── notebook_summary.py  # Notebook özet modeli
│   │   ├── base.py              # Ana fonksiyonların bulunduğu model
│   │   ├── badge_criteria.py    # Rozet kriterleri modeli
│   │   ├── programming_question.py # Soru modeli
│   │   ├── submission.py        # Çözüm gönderimi modeli
│   │   ├── badges.py           # Rozet sistemi
│   │   └── settings.py         # Sistem ayarları
│   ├── routes/                  # Flask rotaları
│   │   ├── auth.py             # Kimlik doğrulama
│   │   ├── admin.py            # Yönetici paneli
│   │   ├── main.py             # Ana sayfalar
│   │   ├── programming.py      # Programlama ile ilgili sayfalar
│   │   ├── notebooks.py        # Notebook işlemleri
│   │   └── api.py              # API endpointleri
│   ├── services/               # İş mantığı servisleri
│   │   └── notebook_service.py # Notebook işlemleri
│   ├── static/                 # Statik dosyalar
│   │   ├── css/               # Stil dosyaları
│   │   ├── js/                # JavaScript dosyaları
│   │   └── img/               # Resim dosyaları
│   ├── templates/             # HTML şablonları
│   │   ├── admin/             # Yönetici sayfaları
│   │   └── components/        # Tekrar kullanılabilir bileşenler
│   └── utils/                 # Yardımcı fonksiyonlar
│       ├── decorators.py      # Custom decorator'lar
│       └── misc.py            # Çeşitli fonksiyonlar
├── notebooks_repo/            # Jupyter notebook'lar
├── logs/                      # Log dosyaları
├── tests/                     # Test dosyaları
├── migrations/                # Veritabanı migration'ları
├── app.py                     # Ana Flask uygulaması
├── api.py                     # FastAPI backend
├── config.py                  # Konfigürasyon
├── requirements.txt           # Python bağımlılıkları
├── docker-compose.yml         # Docker Compose konfigürasyonu
├── Dockerfile                 # Docker build dosyası
└── README.md                  # Proje dokümantasyonu
```

## ⚡ FastAPI Entegrasyonu

PythonPlayground, Flask'in yanı sıra hızlı ve modern bir API çerçevesi olan FastAPI'yi de kullanmaktadır. Bu hibrit yaklaşım, geleneksel web uygulamasının gücünü, yüksek performanslı API hizmetleriyle birleştirir.

### FastAPI'nin Avantajları

- **🚄 Yüksek Performans**: Starlette ve Pydantic sayesinde Node.js ve Go'ya yakın hızlarda çalışır
- **📝 Otomatik API Belgeleri**: OpenAPI (Swagger) ve ReDoc entegrasyonu ile interaktif API belgeleri
- **🧩 Modern Python Özellikleri**: Python 3.8+ özellikleri ve type hints kullanımı
- **⏱️ Asenkron Destek**: `async`/`await` ile asenkron endpoint tanımlama imkanı
- **✅ Veri Doğrulama**: Pydantic ile otomatik veri doğrulama ve dönüştürme

## 🔌 API Endpointleri

PythonPlayground, çeşitli işlevleri için kullanılabilecek kapsamlı bir API sunar:

### 🔍 Sistem Durumu ve İzleme
- **GET /api/server-status**: Sunucu durumunu ve temel metrikleri döndürür
- **GET /api/health**: Sistem sağlık kontrolü için basit endpoint

### 👥 Kullanıcı ve Aktivite
- **GET /api/recent-users**: Son aktif kullanıcıların listesi
- **GET /api/user-profile/{username}**: Belirli bir kullanıcının profil bilgilerini döndürür
- **GET /api/leaderboard**: Liderlik tablosu verilerini döndürür

### 📊 İstatistikler ve Grafikler
- **GET /api/chart/registrations**: Günlük kayıt istatistikleri
- **GET /api/chart/solved-questions**: Çözülen soru istatistikleri
- **GET /api/chart/activity-stats**: Kullanıcı aktivite istatistikleri
- **GET /api/last-questions-detail**: Son soruların detayları
- **GET /api/last-submissions**: Son gönderimler

### 💻 Kod ve Soru Yönetimi
- **POST /api/evaluate**: Kullanıcı çözümünü değerlendirir
- **POST /api/generate-question**: Yeni programlama sorusu üretir
- **POST /api/notebook-summary**: Notebook özeti oluşturur

### 🎯 Etkinlik ve Gamification
- **POST /api/trigger-event**: Sistem etkinliği tetikler (rozet, puan vb.)

## 🛠️ Teknik Gereksinimler

### Temel Gereksinimler
- **Python**: 3.8+
- **Flask**: 3.1.0
- **FastAPI**: 0.110.0
- **Uvicorn**: 0.29.0 (ASGI sunucusu)
- **MySQL**: 5.7+ veya MariaDB 10.5+
- **SQLAlchemy**: 2.0.0+

### Geliştirme Ortamı
- **Git**: 2.30.0+
- **Visual Studio Code** veya **PyCharm** (önerilen)
- **Docker**: 20.10.0+ (opsiyonel, konteynerleştirme için)

### Üretim Ortamı
- **Nginx**: 1.18.0+ (ters proxy olarak)
- **Gunicorn**: 20.1.0+ (Flask WSGI sunucusu)
- **Systemd**: Servis yönetimi için
- **Redis**: 6.0.0+ (önbellek ve oturum yönetimi)

### Tam bağımlılık listesi için `requirements.txt` dosyasına bakın.

## ❓ Sık Sorulan Sorular

<details>
<summary><strong>PythonPlayground'u Docker ile nasıl çalıştırırım?</strong></summary>

Depo içinde Dockerfile ve docker-compose.yml dosyaları bulunmaktadır. Aşağıdaki komutlarla Docker'da çalıştırabilirsiniz:

```bash
# Servisleri oluşturmak ve başlatmak için
docker-compose up -d

# Logları izlemek için
docker-compose logs -f

# Servisleri durdurmak için
docker-compose down

# Eğer Dockerfile'da değişiklik yaptıysanız yeniden build etmek için
docker-compose up -d --build
```

Bu komutlar, uygulamayı, veritabanını ve gerekli tüm servisleri başlatacaktır.
</details>

<details>
<summary><strong>Uygulamayı üretim ortamında nasıl dağıtırım?</strong></summary>

Üretim ortamında dağıtım için aşağıdaki adımları izleyin:

1. Güvenli bir SECRET_KEY ayarlayın
2. Debug modunu kapatın
3. HTTPS kullanın
4. Gunicorn veya uWSGI arkasında çalıştırın
5. Nginx veya Apache gibi bir ters proxy kullanın

Detaylı dağıtım kılavuzu için `DEPLOYMENT.md` dosyasına bakın.
</details>

<details>
<summary><strong>Kendi notebook'larımı nasıl eklerim?</strong></summary>

1. Notebook'larınızı GitHub deposuna yükleyin
2. `config.py` içinde `REPO_URL` değişkenini kendi deponuzun URL'si ile güncelleyin
3. Uygulamayı yeniden başlatın veya `/admin/refresh-notebooks` endpoint'ini çağırın
</details>

## 👥 Katkıda Bulunma

Projeye katkıda bulunmak isteyenler için adımlar:

1. Projeyi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

Daha fazla bilgi için `CONTRIBUTING.md` dosyasına bakın.

## 📄 Lisans

Bu proje GPL-3.0 lisansı altında lisanslanmıştır. Daha fazla detay için `LICENSE` dosyasına bakın.

---

📫 **İletişim:** [iletisim@radome.web.tr](mailto:iletisim@radome.web.tr)

🌐 **Web sitesi:** [https://python.batuhanacikgoz.com.tr](https://python.batuhanacikgoz.com.tr)

Bu proje, eğitim ortamları için etkileşimli bir Python çalışma alanı sunar ve gelişmiş kullanıcı yönetimi özellikleriyle birlikte Jupyter notebook entegrasyonu sağlar.

## 🔧 Kurulum

### Ön Gereksinimler
- Python 3.8 veya daha yeni bir sürüm
- MySQL 5.7+ veya MariaDB 10.5+
- Git (notebook repo'larını çekmek için)

### Adımlar

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/BatuhanAcikgoz/PythonPlayground.git
   cd PythonPlayground
   ```

2. Sanal ortam oluşturun (opsiyonel ama önerilir):
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

4. MySQL veritabanını kurun:
   ```bash
   # 'python_platform' adında bir veritabanı oluşturun
   mysql -u root -p
   CREATE DATABASE python_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. Yapılandırma dosyasını düzenleyin:
   ```bash
   cp config.example.py config.py
   # config.py dosyasını açın ve veritabanı bilgilerinizi girin
   ```

6. Veritabanı tablolarını oluşturun:
   ```bash
   python manage.py create_tables
   ```

7. Uygulamayı başlatın:
   ```bash
   # Flask uygulaması için
   python app.py
   
   # FastAPI uygulaması için (ayrı bir terminalde)
   python api.py
   ```

## 🐳 Docker ile Deployment

PythonPlayground'u hızlıca ve tutarlı bir şekilde deploy etmek için Docker kullanabilirsiniz:

### Docker Compose ile Kurulum

1. Docker ve Docker Compose'un yüklü olduğundan emin olun
2. Repo kök dizininde docker-compose.yml dosyasını kullanarak:

```bash
# Tüm servisleri başlatmak için
docker-compose up -d

# Logları görmek için
docker-compose logs -f

# Servisleri durdurmak için
docker-compose down
```

### Docker Compose Yapısı

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "5000:5000"
    depends_on:
      - db
      - fastapi
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql://user:password@db:3306/python_platform
    volumes:
      - ./logs:/app/logs
    restart: always

  db:
    image: mariadb:10.5
    volumes:
      - db_data:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=python_platform
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    restart: always

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile.fastapi
    ports:
      - "7923:7923"
    restart: always

volumes:
  db_data:
```

### Docker Optimizasyonu

PythonPlayground Docker container'ları, üretim ortamı için optimize edilmiştir:

- Multi-stage builds ile küçük image boyutu
- Health check ile container durumu izleme
- Volume kullanımı ile veri kalıcılığı
- Güvenlik iyileştirmeleri
- Auto-restart politikaları

## 🚦 Kullanım

### Hızlı Başlangıç
- Tarayıcıda Flask uygulaması için `http://localhost:5000` adresine gidin
- FastAPI Swagger belgeleri için `http://localhost:7923/docs` adresini ziyaret edin
- Admin hesabıyla giriş yapın: `admin@example.com / admin123`

### Kullanıcı Türleri ve Yetkiler

| Rol | Yetkiler |
|-----|----------|
| **Öğrenci** | Notebook'ları görüntüleme, kodu çalıştırma, yorumlar yazma |
| **Öğretmen** | Öğrencilere ek olarak, notebook oluşturma ve düzenleme, ödev verme |
| **Admin** | Tüm yetkiler + kullanıcı yönetimi, rol atama, sistem ayarları |

### Örnek İş Akışı
1. Giriş yapın veya yeni bir hesap oluşturun
2. Ana sayfadan bir kurs veya notebook seçin
3. "Çalıştır" butonuna tıklayarak interaktif konsolu açın
4. Kod yazın ve gerçek zamanlı çıktıyı görün

## 📁 Proje Yapısı

```
PythonPlayground/
├── app/                          # Ana uygulama paketi
│   ├── models/                   # Veritabanı modelleri
│   │   ├── user.py              # Kullanıcı ve rol modelleri
│   │   ├── user_badges.py       # Kullanıcı rozet modeli
│   │   ├── notebook_summary.py  # Notebook özet modeli
│   │   ├── base.py              # Ana fonksiyonların bulunduğu model
│   │   ├── badge_criteria.py    # Rozet kriterleri modeli
│   │   ├── programming_question.py # Soru modeli
│   │   ├── submission.py        # Çözüm gönderimi modeli
│   │   ├── badges.py           # Rozet sistemi
│   │   └── settings.py         # Sistem ayarları
│   ├── routes/                  # Flask rotaları
│   │   ├── auth.py             # Kimlik doğrulama
│   │   ├── admin.py            # Yönetici paneli
│   │   ├── main.py             # Ana sayfalar
│   │   ├── programming.py      # Programlama ile ilgili sayfalar
│   │   ├── notebooks.py        # Notebook işlemleri
│   │   └── api.py              # API endpointleri
│   ├── services/               # İş mantığı servisleri
│   │   └── notebook_service.py # Notebook işlemleri
│   ├── static/                 # Statik dosyalar
│   │   ├── css/               # Stil dosyaları
│   │   ├── js/                # JavaScript dosyaları
│   │   └── img/               # Resim dosyaları
│   ├── templates/             # HTML şablonları
│   │   ├── admin/             # Yönetici sayfaları
│   │   └── components/        # Tekrar kullanılabilir bileşenler
│   └── utils/                 # Yardımcı fonksiyonlar
│       ├── decorators.py      # Custom decorator'lar
│       └── misc.py            # Çeşitli fonksiyonlar
├── notebooks_repo/            # Jupyter notebook'lar
├── logs/                      # Log dosyaları
├── tests/                     # Test dosyaları
├── migrations/                # Veritabanı migration'ları
├── app.py                     # Ana Flask uygulaması
├── api.py                     # FastAPI backend
├── config.py                  # Konfigürasyon
├── requirements.txt           # Python bağımlılıkları
├── docker-compose.yml         # Docker Compose konfigürasyonu
├── Dockerfile                 # Docker build dosyası
└── README.md                  # Proje dokümantasyonu
```

## ⚡ FastAPI Entegrasyonu

PythonPlayground, Flask'in yanı sıra hızlı ve modern bir API çerçevesi olan FastAPI'yi de kullanmaktadır. Bu hibrit yaklaşım, geleneksel web uygulamasının gücünü, yüksek performanslı API hizmetleriyle birleştirir.

### FastAPI'nin Avantajları

- **🚄 Yüksek Performans**: Starlette ve Pydantic sayesinde Node.js ve Go'ya yakın hızlarda çalışır
- **📝 Otomatik API Belgeleri**: OpenAPI (Swagger) ve ReDoc entegrasyonu ile interaktif API belgeleri
- **🧩 Modern Python Özellikleri**: Python 3.8+ özellikleri ve type hints kullanımı
- **⏱️ Asenkron Destek**: `async`/`await` ile asenkron endpoint tanımlama imkanı
- **✅ Veri Doğrulama**: Pydantic ile otomatik veri doğrulama ve dönüştürme

## 🔌 API Endpointleri

PythonPlayground, çeşitli işlevleri için kullanılabilecek kapsamlı bir API sunar:

### 🔍 Sistem Durumu ve İzleme
- **GET /api/server-status**: Sunucu durumunu ve temel metrikleri döndürür
- **GET /api/health**: Sistem sağlık kontrolü için basit endpoint

### 👥 Kullanıcı ve Aktivite
- **GET /api/recent-users**: Son aktif kullanıcıların listesi
- **GET /api/user-profile/{username}**: Belirli bir kullanıcının profil bilgilerini döndürür
- **GET /api/leaderboard**: Liderlik tablosu verilerini döndürür

### 📊 İstatistikler ve Grafikler
- **GET /api/chart/registrations**: Günlük kayıt istatistikleri
- **GET /api/chart/solved-questions**: Çözülen soru istatistikleri
- **GET /api/chart/activity-stats**: Kullanıcı aktivite istatistikleri
- **GET /api/last-questions-detail**: Son soruların detayları
- **GET /api/last-submissions**: Son gönderimler

### 💻 Kod ve Soru Yönetimi
- **POST /api/evaluate**: Kullanıcı çözümünü değerlendirir
- **POST /api/generate-question**: Yeni programlama sorusu üretir
- **POST /api/notebook-summary**: Notebook özeti oluşturur

### 🎯 Etkinlik ve Gamification
- **POST /api/trigger-event**: Sistem etkinliği tetikler (rozet, puan vb.)

## 🛠️ Teknik Gereksinimler

### Temel Gereksinimler
- **Python**: 3.8+
- **Flask**: 3.1.0
- **FastAPI**: 0.110.0
- **Uvicorn**: 0.29.0 (ASGI sunucusu)
- **MySQL**: 5.7+ veya MariaDB 10.5+
- **SQLAlchemy**: 2.0.0+

### Geliştirme Ortamı
- **Git**: 2.30.0+
- **Visual Studio Code** veya **PyCharm** (önerilen)
- **Docker**: 20.10.0+ (opsiyonel, konteynerleştirme için)

### Üretim Ortamı
- **Nginx**: 1.18.0+ (ters proxy olarak)
- **Gunicorn**: 20.1.0+ (Flask WSGI sunucusu)
- **Systemd**: Servis yönetimi için
- **Redis**: 6.0.0+ (önbellek ve oturum yönetimi)

### Tam bağımlılık listesi için `requirements.txt` dosyasına bakın.

## ❓ Sık Sorulan Sorular

<details>
<summary><strong>PythonPlayground'u Docker ile nasıl çalıştırırım?</strong></summary>

Depo içinde Dockerfile ve docker-compose.yml dosyaları bulunmaktadır. Aşağıdaki komutlarla Docker'da çalıştırabilirsiniz:

```bash
# Servisleri oluşturmak ve başlatmak için
docker-compose up -d

# Logları izlemek için
docker-compose logs -f

# Servisleri durdurmak için
docker-compose down

# Eğer Dockerfile'da değişiklik yaptıysanız yeniden build etmek için
docker-compose up -d --build
```

Bu komutlar, uygulamayı, veritabanını ve gerekli tüm servisleri başlatacaktır.
</details>

<details>
<summary><strong>Uygulamayı üretim ortamında nasıl dağıtırım?</strong></summary>

Üretim ortamında dağıtım için aşağıdaki adımları izleyin:

1. Güvenli bir SECRET_KEY ayarlayın
2. Debug modunu kapatın
3. HTTPS kullanın
4. Gunicorn veya uWSGI arkasında çalıştırın
5. Nginx veya Apache gibi bir ters proxy kullanın

Detaylı dağıtım kılavuzu için `DEPLOYMENT.md` dosyasına bakın.
</details>

<details>
<summary><strong>Kendi notebook'larımı nasıl eklerim?</strong></summary>

1. Notebook'larınızı GitHub deposuna yükleyin
2. `config.py` içinde `REPO_URL` değişkenini kendi deponuzun URL'si ile güncelleyin
3. Uygulamayı yeniden başlatın veya `/admin/refresh-notebooks` endpoint'ini çağırın
</details>

## 👥 Katkıda Bulunma

Projeye katkıda bulunmak isteyenler için adımlar:

1. Projeyi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

Daha fazla bilgi için `CONTRIBUTING.md` dosyasına bakın.

## 📄 Lisans

Bu proje GPL-3.0 lisansı altında lisanslanmıştır. Daha fazla detay için `LICENSE` dosyasına bakın.

---

📫 **İletişim:** [iletisim@radome.web.tr](mailto:iletisim@radome.web.tr)

🌐 **Web sitesi:** [https://python.batuhanacikgoz.com.tr](https://python.batuhanacikgoz.com.tr)

Bu proje, eğitim ortamları için etkileşimli bir Python çalışma alanı sunar ve gelişmiş kullanıcı yönetimi özellikleriyle birlikte Jupyter notebook entegrasyonu sağlar.
