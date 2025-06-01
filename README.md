# 🚀 PythonPlayground: İnteraktif Python Konsolu ve Eğitim Platformu

<div align="center">
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+"/>
    <img src="https://img.shields.io/badge/Flask-3.1.0-green.svg" alt="Flask 3.1.0"/>
    <img src="https://img.shields.io/badge/FastAPI-0.110.0-teal.svg" alt="FastAPI 0.110.0"/>
    <img src="https://img.shields.io/badge/Status-Geliştiriliyor-orange.svg" alt="Status: Geliştiriliyor"/>
  </p>
</div>

Bu web uygulaması, GitHub deposunda saklanan Jupyter notebook'larını görüntülemenizi ve çalıştırmanızı sağlar. Programiz benzeri bir interaktif konsol sunar ve rol tabanlı erişim kontrolü ile kullanıcı yönetimi içerir.

![PythonPlayground Demo](https://via.placeholder.com/800x450.png?text=PythonPlayground+Demo)

## 📑 İçindekiler
- [🌟 Özellikler](#-özellikler)
- [🔧 Kurulum](#-kurulum)
- [🚦 Kullanım](#-kullanım)
- [📁 Proje Yapısı](#-proje-yapısı)
- [⚡ FastAPI Entegrasyonu](#-fastapi-entegrasyonu)
- [🔌 API Endpointleri](#-api-endpointleri)
- [🛠️ Teknik Gereksinimler](#️-teknik-gereksinimler)
- [❓ Sık Sorulan Sorular](#-sık-sorulan-sorular)
- [👥 Katkıda Bulunma](#-katkıda-bulunma)
- [📄 Lisans](#-lisans)

## 🌟 Özellikler

- **👤 Kullanıcı Yönetimi**: Kapsamlı kayıt, giriş ve rol atama sistemi
- **🔑 Rol Tabanlı Erişim**: Öğrenci, öğretmen ve admin yetki seviyeleri
- **🌐 Çoklu Dil Desteği**: Türkçe ve İngilizce arayüz
- **📚 Notebook Entegrasyonu**: GitHub'dan Jupyter notebook'larını otomatik çekme ve güncelleme
- **💻 İnteraktif Konsol**: Gerçek zamanlı kod çalıştırma ve çıktı görüntüleme
- **⚙️ Yönetim Paneli**: Kullanıcı ve rollerin merkezi yönetimi
- **📱 Responsive Tasarım**: Mobil cihazlara uyumlu arayüz
- **📊 İlerleme Takibi**: Kullanıcıların eğitim ilerlemelerini izleme
- **🏆 Gamification**: Rozetler ve liderlik tablosu ile öğrenme motivasyonu
- **📝 Yorumlar ve Geri Bildirimler**: İşbirlikçi öğrenme için yorum sistemi

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

## 🚦 Kullanım

### Hızlı Başlangıç
- Tarayıcıda Flask uygulaması için `http://localhost:5000` adresine gidin
- FastAPI Swagger belgeleri için `http://localhost:8000/docs` adresini ziyaret edin
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

### FastAPI Mimarisi

FastAPI, özellikle aşağıdaki görevler için kullanılır:

- Jupyter notebook'ları çalıştırma ve yönetme
- Python kodu çalıştırma ve çıktı alma
- Gerçek zamanlı sistem izleme
- Mobil uygulamalar için backend API
- Performans kritik işlemler

### # 🚀 PythonPlayground: İnteraktif Python Eğitim Platformu

<div align="center">
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+"/>
    <img src="https://img.shields.io/badge/Flask-3.1.0-green.svg" alt="Flask 3.1.0"/>
    <img src="https://img.shields.io/badge/FastAPI-0.110.0-teal.svg" alt="FastAPI 0.110.0"/>
    <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker Ready"/>
    <img src="https://img.shields.io/badge/Status-Production-success.svg" alt="Status: Production"/>
  </p>
</div>

**PythonPlayground**, modern Python öğretimi için tasarlanmış kapsamlı bir eğitim platformudur. Jupyter notebook entegrasyonu, interaktif kod çalıştırma, AI destekli soru üretimi ve gamification özellikleriyle öğrenme deneyimini maksimize eder.

![PythonPlayground Demo](https://via.placeholder.com/800x450.png?text=PythonPlayground+Demo)

## 📑 İçindekiler
- [🌟 Temel Özellikler](#-temel-özellikler)
- [🎯 Detaylı Özellikler](#-detaylı-özellikler)
- [🔧 Kurulum](#-kurulum)
- [🐳 Docker ile Deployment](#-docker-ile-deployment)
- [🚦 Kullanım](#-kullanım)
- [📁 Proje Yapısı](#-proje-yapısı)
- [⚡ API Entegrasyonu](#-api-entegrasyonu)
- [🛠️ Teknik Gereksinimler](#️-teknik-gereksinimler)
- [🔧 Konfigürasyon](#-konfigürasyon)
- [👥 Katkıda Bulunma](#-katkıda-bulunma)

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
- **Python**: 3.8+
- **MySQL/MariaDB**: 5.7+
- **Git**: Repository yönetimi için
- **Node.js**: Frontend bağımlılıkları (opsiyonel)

### Hızlı Kurulum

1. **Repository'yi klonlayın:**
   ```bash
   git clone https://github.com/BatuhanAcikgoz/PythonPlayground.git
   cd PythonPlayground
   ```

2. **Python sanal ortamı oluşturun:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Bağımlılıkları yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Veritabanını kurun:**
   ```bash
   # MySQL'e bağlanın
   mysql -u root -p
   
   # Veritabanı oluşturun
   CREATE DATABASE python_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'pythonapp'@'localhost' IDENTIFIED BY 'secure_password';
   GRANT ALL PRIVILEGES ON python_platform.* TO 'pythonapp'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Konfigürasyon dosyasını ayarlayın:**
   ```bash
   cp config.example.py config.py
   # config.py dosyasını editörünüzle açın ve ayarları yapın
   ```

6. **Uygulamayı başlatın:**
   ```bash
   python app.py
   ```

### Gelişmiş Kurulum

#### Environment Variables
```bash
# .env dosyası oluşturun
export FLASK_ENV=development
export DATABASE_URL=mysql://user:password@localhost/python_platform
export SECRET_KEY=your-secret-key-here
export FASTAPI_PORT=8000
```

```python
# api.py örneği
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="PythonPlayground API",
    description="Jupyter notebook ve interaktif Python konsolu için REST API",
    version="1.0.0"
)

# CORS yapılandırması - Flask uygulamasından gelen isteklere izin ver
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str
    timeout: int = 5

class CodeResponse(BaseModel):
    success: bool
    output: str
    execution_time: float

@app.post("/api/execute-code", response_model=CodeResponse)
async def execute_code(request: CodeRequest):
    """
    Python kodunu güvenli bir ortamda çalıştırır ve sonuçları döndürür.
    """
    # İş mantığı burada...
    return {
        "success": True,
        "output": "Kod çıktısı burada...",
        "execution_time": 0.125
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### FastAPI Güvenliği

FastAPI'de OAuth2 token yetkilendirmesi ve JWT ile güvenli kimlik doğrulama:

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Kimlik doğrulama ve token oluşturma
    return {"access_token": token, "token_type": "bearer"}
```

## 🔌 API Endpointleri

### 🔐 Kimlik Doğrulama

- **POST /api/auth/token**
  - Kullanıcı adı ve parola ile JWT erişim tokeni oluşturur
  - İstek: `{"username": "user", "password": "pass"}`
  - Yanıt: `{"access_token": "eyJhbG...", "token_type": "bearer"}`

### 💻 Kod Çalıştırma

- **POST /api/execute-code**
  - Python kodunu güvenli bir şekilde yürütür ve sonuçları döndürür
  - İstek: 
  ```json
  {
    "code": "for i in range(5):\n    print(f'Sayı: {i}')",
    "timeout": 5
  }
  ```
  - Yanıt: 
  ```json
  {
    "success": true,
    "output": "Sayı: 0\nSayı: 1\nSayı: 2\nSayı: 3\nSayı: 4\n",
    "execution_time": 0.023,
    "memory_usage": "3.2 MB"
  }
  ```

### 📚 Notebook Yönetimi

- **GET /api/notebooks**
  - Mevcut tüm notebook'ların listesini döndürür
  - Yanıt:
  ```json
  {
    "notebooks": [
      {
        "name": "Python Temelleri",
        "path": "kurslar/python101/ders1.ipynb",
        "last_modified": "2023-07-15T14:32:10Z",
        "description": "Python programlamaya giriş"
      },
      {
        "name": "Veri Bilimi",
        "path": "kurslar/data_science/pandas_intro.ipynb",
        "last_modified": "2023-08-02T09:15:22Z",
        "description": "Pandas ile veri analizi"
      }
    ]
  }
  ```

- **GET /api/notebooks/{path}**
  - Belirtilen notebook içeriğini döndürür
  
- **POST /api/notebooks/{path}**
  - Notebook içeriğini günceller
  - İstek: `{"cells": [...], "metadata": {...}}`
  - Yanıt: `{"success": true, "message": "Notebook başarıyla güncellendi"}`

### 📊 Analitik ve İzleme

- **GET /api/server-stats**
  - Sunucu durum bilgilerini ve istatistikleri döndürür
  - Yanıt:
  ```json
  {
    "status": "online",
    "uptime": "3 gün 7 saat",
    "python_version": "3.9.10",
    "api_version": "1.2.0",
    "memory_usage": "42%",
    "cpu_load": "12%",
    "active_users": 28,
    "notebook_count": 45,
    "execution_count_today": 1253
  }
  ```

- **GET /api/user-progress/{user_id}**
  - Kullanıcı ilerleme istatistiklerini döndürür
  - Yanıt: `{"completed_courses": 3, "exercises_solved": 42, ...}`

### 📱 Mobil Uygulama API'leri

- **GET /api/mobile/courses**
  - Mobil uygulama için optimize edilmiş kurs listesi
  - Yanıt: `{"courses": [{"id": 1, "name": "Python 101", "thumbnail_url": "...", ...}, ...]}`

## 🛠️ Teknik Gereksinimler

### Temel Gereksinimler
- **Python**: 3.8+
- **Flask**: 3.1.0
- **FastAPI**: 0.110.0
- **Uvicorn**: 0.27.0 (ASGI sunucusu)
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
docker-compose up -d
```

Bu komut, uygulamayı, veritabanını ve gerekli tüm servisleri başlatacaktır.
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
