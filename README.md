# Python Notebook Görüntüleyici ve İnteraktif Konsol

Bu web uygulaması, GitHub deposunda saklanan Jupyter notebook'larını görüntülemenizi ve içindeki Python kodlarını çalıştırmanızı sağlar. [Programiz'in çevrimiçi Python derleyicisi](https://www.programiz.com/python-programming/online-compiler/) benzeri bir interaktif konsol sunar.

## Özellikler

- Jupyter notebook'larını içeren GitHub deposunu otomatik olarak klonlar ve günceller
- Notebook'ları okunabilir HTML olarak görüntüler
- Kod çalıştırmak için interaktif bir Python konsolu sağlar
- Gerçek zamanlı kod yürütme ve anında çıktı görüntüleme
- Girdi (input) işlemlerini interaktif bir komut istemiyle halleder
- Yukarı/aşağı ok tuşlarıyla komut geçmişine erişim imkanı

## Kurulum

1. Bu depoyu klonlayın:
   ```bash
   git clone https://github.com/kullaniciadi/python-notebook-viewer.git
   cd python-notebook-viewer
   ```

2. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```

3. `app.py` dosyasındaki GitHub deposu URL'sini güncelleyin:
   ```python
   REPO_URL = 'https://github.com/hedef-deponuz/notebooks'
   ```

## Kullanım

1. Uygulamayı başlatın:
   ```bash
   python app.py
   ```

2. Tarayıcınızı açın ve `http://localhost:5000` adresine gidin

3. Depodaki mevcut notebook'ları görüntüleyin

4. İçeriğini görmek için herhangi bir notebook'a tıklayın

5. Herhangi bir kod hücresini interaktif konsolda çalıştırmak için "Çalıştır" düğmesine tıklayın

6. Python komutlarını doğrudan konsola yazın ve çalıştırmak için Enter tuşuna basın

## Bağımlılıklar

- Flask 2.3.3
- Flask-SocketIO 5.3.6
- nbformat 5.9.2
- python-socketio 5.10.0
- eventlet 0.33.3

## Proje Yapısı

- `app.py`: Flask rotaları ve Socket.IO olay işleyicileri içeren ana uygulama dosyası
- `templates/`: HTML şablonları
  - `index.html`: Mevcut notebook'ları listeleyen ana sayfa
  - `notebook_viewer.html`: Notebook görüntüleme şablonu
  - `console.html`: İnteraktif Python konsol arayüzü
- `requirements.txt`: Python bağımlılıklarının listesi

## Lisans

GPLv3 lisansı altında lisanslanmıştır. Daha fazla bilgi için [LİSANS](LICENSE) dosyasına bakın.