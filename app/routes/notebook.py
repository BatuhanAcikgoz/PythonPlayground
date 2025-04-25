from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.services.notebook_service import NotebookService

notebook_bp = Blueprint('notebook', __name__)

notebook_service = NotebookService()

@notebook_bp.route('/<path:notebook_path>')
@login_required
def view(notebook_path):
    notebook = notebook_service.get_notebook(notebook_path)
    if not notebook:
        flash('Notebook bulunamadı veya yüklenemedi.', 'error')
        return redirect(url_for('main.index'))
    return render_template('notebook_viewer.html', notebook=notebook)

@notebook_bp.route('/run', methods=['POST'])
@login_required
def run():
    code = request.json.get('code')
    result = notebook_service.run_code(code)
    return jsonify(result)

# SocketIO işleyicilerini tanımlamak için fonksiyon
def register_socketio_handlers(socketio):
    @socketio.on('run_code')
    def handle_run_code(data):
        code = data['code']
        user_id = current_user.id
        notebook_service.handle_socket_run_code(code, user_id, socketio)

    @socketio.on('input_response')
    def handle_input_response(data):
        notebook_service.set_input_response(data['value'])

    @socketio.on('connect')
    def handle_connect():
        if current_user.is_authenticated:
            notebook_service.reset_namespace(current_user.id)


@notebook_bp.route('/summary/<path:notebook_path>')
@login_required
def summary(notebook_path):
    from app.services.ai_service import AIService
    ai_service = AIService()

    try:
        # URL'deki '/notebook/summary/' öneki dosya yoluna dahil edilmiş olabilir
        if notebook_path.startswith('notebook/summary/'):
            notebook_path = notebook_path[len('notebook/summary/'):]

        # Notebook'u önce kontrol et
        notebook = notebook_service.get_notebook(notebook_path)
        if not notebook:
            flash(f"Notebook bulunamadı: {notebook_path}", 'error')
            return redirect(url_for('main.index'))

        # AI özeti oluştur veya varsa getir
        summary_data = ai_service.get_notebook_summary(notebook_path)

        # None kontrolü - daha spesifik hata mesajı
        if summary_data is None:
            flash("AI özeti şu anda oluşturulamıyor. API servisi yanıt vermiyor veya API anahtarı geçersiz.", 'warning')

            # Kullanıcılara yardımcı olacak detaylı bilgi verebilirsiniz
            if current_user.is_admin():
                flash(
                    "Lütfen Admin Panelinden API ayarlarını kontrol edin ve geçerli bir API anahtarı girdiğinizden emin olun.",
                    'info')

            # Notebook varsa, en azından notebook'u görüntüle
            return render_template(
                'notebook_summary.html',
                notebook_path=notebook_path,
                summary_data={"error": "AI servisi geçici olarak kullanılamıyor."},
                notebook=notebook
            )

        # Hata kontrolü - summary_data bir sözlük ve içinde 'error' var mı?
        if isinstance(summary_data, dict) and 'error' in summary_data:
            flash(summary_data['error'], 'error')
            # Notebook varsa, hataya rağmen notebook'u görüntüle
            return render_template(
                'notebook_summary.html',
                notebook_path=notebook_path,
                summary_data=summary_data,
                notebook=notebook
            )

        return render_template(
            'notebook_summary.html',
            notebook_path=notebook_path,
            summary_data=summary_data,
            notebook=notebook
        )
    except Exception as e:
        flash(f"İşlem sırasında hata oluştu: {str(e)}", 'error')
        return redirect(url_for('main.index'))