# PythonPlayground: İnteraktif Python Konsolu ve Eğitim Platformu

Bu web uygulaması, GitHub deposunda saklanan Jupyter notebook'larını görüntülemenizi ve içindeki Python kodlarını çalıştırmanızı sağlar. Programiz benzeri bir interaktif konsol sunar ve kullanıcı yönetimi, rol tabanlı erişim kontrolü gibi gelişmiş özellikler içerir.

## Özellikler

- **Kullanıcı Yönetimi**: Kapsamlı kayıt, giriş, rol atama sistemi
- **Rol Tabanlı Erişim Kontrolü**: Üç farklı yetki seviyesi (admin, öğretmen, öğrenci)
- **Çoklu Dil Desteği**: Türkçe (varsayılan) ve İngilizce arayüz
- **Notebook Entegrasyonu**: GitHub'dan Jupyter notebook'larını otomatik çeker ve günceller
- **İnteraktif Konsol**: Gerçek zamanlı kod çalıştırma, çıktı görüntüleme
- **Gelişmiş Konsol Özellikleri**: 
  - Kod girişi ve anında çalıştırma
  - Komut geçmişi (yukarı/aşağı ok tuşlarıyla)
  - Kullanıcı girdisi alabilen programlar çalıştırabilme
  - Renk kodlamalı çıktı görüntüleme
- **Yönetim Paneli**: Kullanıcıları ve rolleri yönetme arayüzü

## Teknik Detaylar

- **Backend**: Flask ve Python ile geliştirilmiş web sunucusu
- **Gerçek Zamanlı İletişim**: Socket.IO ile kod çalıştırma ve çıktı gösterme
- **Veritabanı**: MySQL veritabanında kullanıcı ve rol bilgilerini saklama
- **Güvenlik**: Şifreleme, oturum yönetimi ve rol bazlı erişim kontrolleri
- **Çoklu Dil**: Flask-Babel ile farklı dil destekleri

## Kurulum

1. Bu depoyu klonlayın:
   ```bash
   git clone https://github.com/BatuhanAcikgoz/PythonPlayground.git
   cd PythonPlayground
   ```

2. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. MySQL veritabanını kurun:
   ```bash
   # 'python_platform' adında bir MySQL veritabanı oluşturun
   # Veritabanı bağlantı bilgilerini app.py dosyasında güncelleyin:
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://kullanici_adi:parola@localhost/python_platform'
   ```

4. Notebook deposu yapılandırması:
   ```python
   # app.py dosyasındaki REPO_URL değişkenini ihtiyacınıza göre düzenleyin
   REPO_URL = 'https://github.com/msy-bilecik/ist204_2025'  # veya başka bir notebook deposu
   ```

## Kullanım

1. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

2. Tarayıcınızda `http://localhost:5000` adresine gidin

3. Hesap oluşturun veya varsayılan admin hesabıyla giriş yapın:
   - Kullanıcı adı: `admin` 
   - Şifre: `admin123`

4. Uygulama özellikleri:
   - Ana sayfada mevcut notebook listesini görüntüleyin
   - İncelemek istediğiniz notebook'a tıklayın
   - "Çalıştır" butonuyla kod hücrelerini çalıştırın
   - Konsola doğrudan Python kodu yazabilirsiniz
   - Admin panelinden kullanıcıları ve rolleri yönetin
   - Sağ üst köşeden dil tercihini değiştirin

## Kullanıcı Rolleri ve İzinler

- **Öğrenci**:
  - Notebook'ları görüntüleme
  - Kod çalıştırma
  - Profil düzenleme

- **Öğretmen** (öğrenci yetkileri + şunlar):
  - Notebook deposunu güncelleme
  - Öğrenci ilerlemesini görüntüleme
  - İçerik yönetimi

- **Admin** (öğretmen yetkileri + şunlar):
  - Kullanıcı hesapları oluşturma/silme
  - Rol atama ve düzenleme
  - Sistem yapılandırması

## Proje Yapısı

```
PythonPlayground/
├── app.py                 # Ana uygulama dosyası
├── requirements.txt       # Bağımlılıklar
├── notebooks_repo/        # Klonlanan notebook deposu
├── static/                # Statik dosyalar (JS, CSS)
│   ├── css/               # Stil dosyaları
│   ├── js/                # JavaScript dosyaları
│   └── images/            # Görseller
├── templates/             # HTML şablonları
│   ├── admin/             # Admin paneli şablonları
│   ├── js/components/     # React bileşenleri
│   ├── index.html         # Ana sayfa
│   ├── login.html         # Giriş sayfası
│   ├── register.html      # Kayıt sayfası
│   └── notebook_viewer.html # Notebook görüntüleyici
└── translations/          # Dil çevirileri
    ├── en/                # İngilizce
    └── tr/                # Türkçe
```

## Teknik Gereksinimler

- Python 3.8+
- MySQL 5.7+ veya MariaDB 10.5+
- Tarayıcı: Chrome, Firefox, Edge (güncel sürümler)
- İnternet bağlantısı (notebook deposunu çekmek için)

## Bağımlılıklar

- Flask 2.3.3+
- Flask-SocketIO 5.3.6+
- Flask-SQLAlchemy
- Flask-Login
- Flask-Babel
- nbformat 5.9.2+
- python-socketio 5.10.0+
- eventlet 0.33.3+
- PyMySQL
- React (CDN üzerinden)
- TailwindCSS (CDN üzerinden)

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b ozellik/yenilik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: Açıklama'`)
4. Branch'inizi push edin (`git push origin ozellik/yenilik`)
5. Pull Request açın

## Lisans

Bu proje GPLv3 lisansı altında dağıtılmaktadır. Daha fazla bilgi için `LICENSE` dosyasını inceleyebilirsiniz.