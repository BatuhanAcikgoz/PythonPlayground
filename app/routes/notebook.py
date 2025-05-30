from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.services.notebook_service import NotebookService

notebook_bp = Blueprint('notebook', __name__)

notebook_service = NotebookService()

@notebook_bp.route('/<path:notebook_path>')
@login_required
def view(notebook_path):
    """
    Notebook gösterim rotası. Bu işlev, kullanıcıların bir not defterini görüntülemesine olanak tanır. Kullanıcı oturumu
    gerekir. Eğer istenilen not defteri bulunamazsa veya yükleme sırasında bir hata oluşursa bir hata mesajı ile ana
    sayfaya yönlendirilir.

    Args:
        notebook_path (str): Görüntülenmek istenen not defterinin yolu.

    Returns:
        Response: Eğer not defteri başarıyla yüklenirse not defteri görüntüleyici şablonunu döner. Aksi halde kullanıcı,
        hata mesajı ile ana sayfaya yönlendirilir.
    """
    notebook = notebook_service.get_notebook(notebook_path)
    if not notebook:
        flash('Notebook bulunamadı veya yüklenemedi.', 'error')
        return redirect(url_for('main.index'))
    return render_template('notebook_viewer.html', notebook=notebook)

@notebook_bp.route('/run', methods=['POST'])
@login_required
def run():
    """
    Fonksiyon, POST yöntemi ile çalıştırılacak bir API uç noktası tanımlar. Kullanıcı doğrulaması
    ile korunan bu uç nokta, gelen JSON formatındaki kodu çalıştırır ve sonucu JSON formatında
    geri döner.

    Parameters:
        None

    Returns:
        Response: Çalıştırılan kodun çıktısını JSON formatında döner.
    """
    code = request.json.get('code')
    result = notebook_service.run_code(code)
    return jsonify(result)

# SocketIO işleyicilerini tanımlamak için fonksiyon
def register_socketio_handlers(socketio):
    """
    register_socketio_handlers(socketio)

    Belirtilen socket.io olayları için handler fonksiyonlarını kaydeder. Bu handlers'lar, gelen socket.io
    isteklerini işleyerek uygun hizmetlere yönlendirme yapar.

    Args:
        socketio: Socket.IO kullanımı için gereken nesne.

    Decorator-based event handlers:

    'run_code': Kullanıcıdan gelen kod çalıştırma isteğini işler ve kodun gerekli hizmete gönderilmesini sağlar.
    'input_response': Kullanıcıdan gelen giriş yanıtlarını işler ve belirtilen değerleri kaydeder.
    'connect': Socket.IO bağlantısı sırasında kullanıcı kimlik doğrulamasını kontrol eder ve
    gerekli oturum başlatma işlemlerini yapar.

    Raises:
        ValueError: Args veya fire edilen event'teki eksik veya hatalı verilerden dolayı gerçekleşebilir.
    """
    @socketio.on('run_code')
    def handle_run_code(data):
        """
        register_socketio_handlers fonksiyonu soket tabanlı dinleyiciler oluşturur ve bu dinleyicilere
        spesifik event işlemleri tanımlar. Bu, özellikle 'run_code' event'ini işler ve gönderilen kodu,
        ilgili kullanıcı bilgisi ile işleyen bir hizmete yönlendirir.

        Arguments:
            socketio: Flask-SocketIO örneği olup, WebSocket bağlantılarını ve event'lerini yönetir.
        """
        code = data['code']
        user_id = current_user.id
        notebook_service.handle_socket_run_code(code, user_id, socketio)

    @socketio.on('input_response')
    def handle_input_response(data):
        """
        Fonksiyon, Flask-SocketIO ile ilgili olay işleyicilerini kaydeder ve belirli bir olay
        oluştuğunda yürütülecek olan işlevi tanımlar. Bu işleyiciler, istemci tarafından gönderilen
        verilere yanıt olarak sunucu tarafında işlem yapılmasını sağlar.

        Args:
            socketio: Flask-SocketIO nesnesi. Olay işleyicilerinin kaydedileceği nesne.
        """
        notebook_service.set_input_response(data['value'])

    @socketio.on('connect')
    def handle_connect():
        """
        Socket.IO bağlantı işleyicilerini kayıt eder.

        Bu fonksiyon, verilen Socket.IO nesnesine bağlantı işleyicilerini ekler.
        Fonksiyon içinde tanımlanan `handle_connect` işlevi, istemcinin web soketi
        bağlantısının başarılı şekilde gerçekleştiği durumda çağrılır.

        Fonksiyonun temel amacı, kullanıcı doğrulandıktan sonra ilgili oturum
        için not defteri hizmetlerini sıfırlamaktır.

        Arguments:
            socketio: Socket.IO uygulama nesnesi.

        Raises:
            Bu fonksiyon doğrudan bir hata yükseltmez fakat içindeki çağrılar hata
            oluşturabilir. Örneğin, `current_user` doğrulaması veya
            `notebook_service.reset_namespace` çağrısı başarısız olabilir.
        """
        if current_user.is_authenticated:
            notebook_service.reset_namespace(current_user.id)


@notebook_bp.route('/summary/<path:notebook_path>')
@login_required
def summary(notebook_path):
    """
    Route işlevi, belirli bir notebook'un özet bilgilerini almak için bir Flask endpoint'idir. Kullanıcı
    oturum açmış durumda olmalıdır ve notebook belirtilen yol aracılığıyla seçilir. Önce notebook'un
    varlığı kontrol edilir, ardından özet bilgileri FastAPI proxy çağrısıyla veya veritabanı sorgusuyla
    alınır. Elde edilen özet bilgileri uygun şablon ile render edilir ve istemciye sunulur.

    Parameters:
        notebook_path (str): Özet bilgileri alınacak notebook'un yolunu belirtir.

    Raises:
        None

    Returns:
        Flask Response: Kullanıcıya render edilmiş özet bilgilerini içeren bir HTML sayfası döndürür.
    """
    if notebook_path.startswith('notebook/summary/'):
        notebook_path = notebook_path[len('notebook/summary/'):]

    # Notebook'u önce kontrol et
    notebook = notebook_service.get_notebook(notebook_path)
    if not notebook:
        flash(f"Notebook bulunamadı: {notebook_path}", 'error')
        return redirect(url_for('main.index'))

    # FastAPI'den özet iste
    try:
        from app.routes.api import proxy
        response, status_code = proxy('notebook-summary')
        if status_code != 200 or "error" in response and response["error"]:
            flash(f"Özet alınırken bir hata oluştu: {response.get('error', 'Bilinmeyen hata')}", 'error')
            summary_data = None
        else:
            summary_data = response
    except Exception as e:
        flash(f"API bağlantı hatası: {str(e)}", 'error')
        # Veritabanından direkt sorgula
        from app.models.notebook_summary import NotebookSummary
        existing_summary = NotebookSummary.query.filter_by(notebook_path=notebook_path).first()

        if existing_summary:
            summary_data = {
                'summary': existing_summary.summary,
                'code_explanation': existing_summary.code_explanation,
                'last_updated': existing_summary.last_updated,
                'error': existing_summary.error
            }
        else:
            summary_data = None
            flash(f"Bu notebook için henüz özet bulunmuyor.", 'warning')

    if not summary_data:
        return redirect(url_for('notebook.view', notebook_path=notebook_path))

    return render_template(
        'notebook_summary.html',
        notebook_path=notebook_path,
        summary_data=summary_data,
        notebook=notebook
    )