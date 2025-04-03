# PythonPlayground: İnteraktif Python Konsolu ve Eğitim Platformu

Bu web uygulaması, GitHub deposunda saklanan Jupyter notebook'larını görüntülemenizi ve çalıştırmanızı sağlar. Programiz benzeri bir interaktif konsol sunar ve rol tabanlı erişim kontrolü ile kullanıcı yönetimi içerir.

## İçindekiler
- [Özellikler](#özellikler)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Proje Yapısı](#proje-yapısı)
- [Sınıf Referansları](#sınıf-referansları)
- [API Endpointleri](#api-endpointleri)
- [Teknik Gereksinimler](#teknik-gereksinimler)

## Özellikler

- **Kullanıcı Yönetimi**: Kapsamlı kayıt, giriş ve rol atama sistemi
- **Rol Tabanlı Erişim**: Öğrenci, öğretmen ve admin yetki seviyeleri
- **Çoklu Dil Desteği**: Türkçe ve İngilizce arayüz
- **Notebook Entegrasyonu**: GitHub'dan Jupyter notebook'larını otomatik çekme ve güncelleme
- **İnteraktif Konsol**: Gerçek zamanlı kod çalıştırma ve çıktı görüntüleme
- **Yönetim Paneli**: Kullanıcı ve rollerin merkezi yönetimi

## Kurulum

1. Depoyu klonlayın:
   ```bash
   git clone https://github.com/BatuhanAcikgoz/PythonPlayground.git
   cd PythonPlayground
   ```

2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. MySQL veritabanını kurun:
   ```bash
   # 'python_platform' adında bir veritabanı oluşturun
   # Bağlantı bilgilerini config.py dosyasında güncelleyin
   ```

4. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

## Kullanım

- Tarayıcıda `http://localhost:5000` adresine gidin
- Admin hesabıyla giriş yapın: `admin/admin123`
- Ana sayfadan notebook'ları görüntüleyin ve çalıştırın
- Admin panelinden kullanıcıları ve rolleri yönetin

## Proje Yapısı

```
project_root/
  ├── app.py                 # Ana Flask uygulaması
  ├── api.py                 # FastAPI uygulaması
  ├── config.py              # Yapılandırma ayarları
  ├── models/                # Veritabanı modelleri
  ├── routes/                # Flask rotaları
  ├── services/              # İş mantığı 
  └── utils/                 # Yardımcı fonksiyonlar
```

## Sınıf Referansları

### 1. `User` Sınıfı (models/user.py)

Sistemdeki kullanıcıları temsil eden sınıf.

```python
class User(UserMixin, db.Model):
    # Kullanıcı tablosu özellikleri ve metotları
```

**Özellikler:**
- `id` - Benzersiz kullanıcı kimliği
- `username` - Kullanıcı adı
- `email` - E-posta adresi
- `password_hash` - Şifrelenmiş parola
- `created_at` - Hesap oluşturma tarihi
- `roles` - Kullanıcının sahip olduğu roller (many-to-many ilişki)

**Metotlar:**
- `set_password(password)` - Parolayı şifreler ve kaydeder
- `check_password(password)` - Verilen parolanın doğruluğunu kontrol eder
- `has_role(role_name)` - Kullanıcının belirli bir role sahip olup olmadığını kontrol eder
- `is_admin()` - Kullanıcının admin rolüne sahip olup olmadığını kontrol eder
- `is_teacher()` - Kullanıcının öğretmen rolüne sahip olup olmadığını kontrol eder

### 2. `Role` Sınıfı (models/user.py)

Sistem içindeki yetki rollerini tanımlar.

```python
class Role(db.Model):
    # Rol tablosu özellikleri
```

**Özellikler:**
- `id` - Benzersiz rol kimliği
- `name` - Rol adı (admin, teacher, student)
- `description` - Rol açıklaması

**İlişkiler:**
- `users` - Bu role sahip kullanıcılar (many-to-many ilişki)

### 3. `Course` Sınıfı (models/course.py)

Eğitim kurslarını temsil eden sınıf.

```python
class Course(db.Model):
    # Kurs tablosu özellikleri
```

**Özellikler:**
- `id` - Benzersiz kurs kimliği
- `name` - Kurs adı
- `description` - Kurs açıklaması
- `created_at` - Oluşturulma tarihi

**İlişkiler:**
- `questions` - Kursa ait sorular (one-to-many ilişki)

### 4. `Question` Sınıfı (models/course.py)

Kurslarda yer alan soruları temsil eden sınıf.

```python
class Question(db.Model):
    # Soru tablosu özellikleri
```

**Özellikler:**
- `id` - Benzersiz soru kimliği
- `title` - Soru başlığı
- `content` - Soru içeriği
- `created_at` - Oluşturulma tarihi
- `updated_at` - Son güncellenme tarihi
- `course_id` - Ait olduğu kursun kimliği (foreign key)

### 5. `Config` Sınıfı (config.py)

Uygulama yapılandırma ayarlarını içeren sınıf.

```python
class Config:
    # Yapılandırma ayarları
```

**Özellikler:**
- `SECRET_KEY` - Flask güvenlik anahtarı
- `SQLALCHEMY_DATABASE_URI` - Veritabanı bağlantı dizesi
- `BABEL_DEFAULT_LOCALE` - Varsayılan dil ayarı
- `BABEL_SUPPORTED_LOCALES` - Desteklenen diller
- `REPO_URL` - GitHub repo URL'si
- `REPO_DIR` - Notebook'ların yerel depolandığı klasör yolu

### 6. `NotebookService` Sınıfı (services/notebook_service.py)

Jupyter notebook'larını yönetmek için kullanılan servis sınıfı.

```python
class NotebookService:
    # Notebook işlemleri metotları
```

**Metotlar:**
- `get_repo_path()` - Repo dizin yolunu döndürür
- `ensure_repo_exists()` - Repo dizininin var olduğundan emin olur, yoksa Git'ten çeker
- `get_all_notebooks()` - Tüm notebook dosyalarını listeler
- `get_notebook(notebook_path)` - Belirli bir notebook dosyasının içeriğini okur
- `save_notebook(notebook_path, content)` - Notebook içeriğini kaydeder
- `run_code(code)` - Python kodunu çalıştırıp sonucu döndürür

## API Endpointleri

### FastAPI Endpointleri (api.py)

- **GET /api/server-status** - Sunucu durum bilgilerini döndürür
  - Python sürümü, Flask sürümü, MySQL sürümü
  - RAM ve CPU kullanım istatistikleri

## Teknik Gereksinimler

- **Python**: 3.8+
- **Flask**: 3.1.0
- **FastAPI**: 0.110.0
- **MySQL**: 5.7+ veya MariaDB 10.5+
- **Bağımlılıklar**: Tam liste için `requirements.txt` dosyasına bakın

---

Bu proje, eğitim ortamları için etkileşimli bir Python çalışma alanı sunar ve gelişmiş kullanıcı yönetimi özellikleriyle birlikte Jupyter notebook entegrasyonu sağlar.