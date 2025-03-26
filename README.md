# PythonPlayground: İnteraktif Konsol ve Eğitim Platformu 

Bu web uygulaması, GitHub deposunda saklanan Jupyter notebook'larını görüntülemenizi ve içindeki Python kodlarını çalıştırmanızı sağlar. [Programiz'in çevrimiçi Python derleyicisi](https://www.programiz.com/python-programming/online-compiler/) benzeri bir interaktif konsol sunar ve kullanıcı kimlik doğrulama, rol tabanlı erişim kontrolü gibi ek özellikler içerir.

## Özellikler

- Kullanıcı kaydı ve giriş sistemi
- Rol tabanlı erişim kontrolü (admin, öğretmen, öğrenci)
- Çoklu dil desteği (şu anda Türkçe ve İngilizce)
- Jupyter notebook'larını içeren GitHub deposunu otomatik olarak klonlar ve günceller
- Notebook içeriğini HTML olarak görüntüler
- Kod çalıştırmak için interaktif Python konsolu
- Gerçek zamanlı kod yürütme ve çıktı görüntüleme
- Komut istemi aracılığıyla interaktif girdi işleme
- Yukarı/aşağı ok tuşlarıyla komut geçmişi navigasyonu
- Kullanıcı yönetimi ve rol ataması için admin paneli

## Kurulum

1. Bu depoyu klonlayın:
   ```bash
   git clone https://github.com/msy-bilecik/ist204_2025.git
   cd ist204_2025
   ```

2. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. MySQL veritabanını kurun:
   ```bash
   # 'python_platform' adında bir MySQL veritabanı oluşturun
   # Gerekirse app.py içindeki veritabanı bağlantı dizesini güncelleyin:
   app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://kullanici_adi:parola@localhost/python_platform'
   ```

## Kullanım

1. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

2. Tarayıcınızı açın ve `http://localhost:5000` adresine gidin

3. Hesap oluşturun veya mevcut kimlik bilgileriyle giriş yapın
   - Varsayılan admin hesabı: kullanıcı adı: `admin`, şifre: `admin123`

4. Depodaki mevcut notebook'ları görüntüleyin

5. İçeriğini görmek için herhangi bir notebook'a tıklayın

6. Herhangi bir kod hücresini çalıştırmak için "Çalıştır" düğmesine tıklayın

7. Python komutlarını doğrudan konsola yazın ve çalıştırmak için Enter tuşuna basın

## Kullanıcı Rolleri

- **Öğrenci**: Notebook'ları görüntülemek ve kod çalıştırmak için temel erişim
- **Öğretmen**: Notebook'ları yönetebilir, depo içeriğini yenileyebilir ve öğrenci ilerlemesini görüntüleyebilir
- **Admin**: Tam yönetici erişimi, kullanıcı yönetimi ve rol atama dahil

## Çoklu Dil Desteği

Uygulama birden fazla dili destekler. Şu anda uygulanmış olanlar:
- Türkçe (varsayılan)
- İngilizce

Dil değiştirici üzerine tıklayarak veya `/language/en` veya `/language/tr` adreslerini ziyaret ederek dili değiştirebilirsiniz.

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

## Proje Yapısı

- `app.py`: Flask rotaları ve Socket.IO olay işleyicilerini içeren ana uygulama dosyası
- `templates/`: HTML şablonları
  - `index.html`: Mevcut notebook'ları listeleyen ana sayfa
  - `login.html`, `register.html`: Kimlik doğrulama sayfaları
  - `notebook_viewer.html`: Notebook görüntüleme şablonu
  - `admin/`: Admin paneli şablonları
- `static/`: Statik dosyalar (CSS, JS)
- `translations/`: Dil çeviri dosyaları

## Lisans

GPLv3 lisansı altında lisanslanmıştır. Daha fazla bilgi için [LİSANS](LICENSE) dosyasına bakın.