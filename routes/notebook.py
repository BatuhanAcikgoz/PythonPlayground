from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from services.notebook_service import NotebookService
from flask import current_app

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