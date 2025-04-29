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
    # URL'deki '/notebook/summary/' öneki dosya yoluna dahil edilmiş olabilir
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