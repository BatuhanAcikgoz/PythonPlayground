from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import login_required, current_user
from app.models.course import Course
from flask import send_from_directory
import os
import subprocess
import shutil

main_bp = Blueprint('main', __name__)

def clone_repo():
    """Repository klonlama veya güncelleme işlemi"""
    # REPO_URL'yi doğrudan tanımla - app_legacy'den alındı
    repo_url = 'https://github.com/msy-bilecik/ist204_2025'
    repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')

    if os.path.exists(repo_dir):
        print(f"{repo_dir} dizinindeki repo güncelleniyor")
        try:
            # En son değişiklikleri çek
            subprocess.run(['git', 'pull'], cwd=repo_dir, check=True)
            return repo_dir
        except subprocess.CalledProcessError:
            print("Repo güncellenirken hata oluştu, yeniden klonlanıyor")
            # Çekme başarısız olursa, temiz bir şekilde klonla
            shutil.rmtree(repo_dir, ignore_errors=True)

    print(f"Repository {repo_dir} dizinine klonlanıyor")
    try:
        subprocess.run(['git', 'clone', repo_url, repo_dir], check=True)
        return repo_dir
    except subprocess.CalledProcessError as e:
        print(f"Repository klonlanırken hata: {str(e)}")
        return None


@main_bp.route('/')
def index():
    courses = Course.query.all()
    # Notebook dosyalarını kontrol et
    repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')
    notebooks = []
    error_message = None

    # Repo dizini var mı kontrol et
    if os.path.exists(repo_dir):
        # Tüm ipynb dosyalarını listele
        for root, dirs, files in os.walk(repo_dir):
            for file in files:
                if file.endswith('.ipynb'):
                    rel_path = os.path.relpath(os.path.join(root, file), repo_dir)
                    notebooks.append(rel_path)

        if not notebooks:
            error_message = "Henüz notebook mevcut değil."
    else:
        # Repo yoksa, oluşturma girişimi yap
        try:
            repo_dir = clone_repo()
            if repo_dir and os.path.exists(repo_dir):
                # Yeniden notebook listesini dene
                for root, dirs, files in os.walk(repo_dir):
                    for file in files:
                        if file.endswith('.ipynb'):
                            rel_path = os.path.relpath(os.path.join(root, file), repo_dir)
                            notebooks.append(rel_path)

                if not notebooks:
                    error_message = "Henüz notebook mevcut değil."
            else:
                error_message = "Repository klonlanamadı."
        except Exception as e:
            error_message = f"Repository işlemi sırasında hata: {str(e)}"

    return render_template('index.html', courses=courses, notebooks=notebooks, error_message=error_message)

@main_bp.route('/<path:path>')
def redirect_notebook(path):
    if path.endswith('.ipynb'):
        return redirect(url_for('notebook.view', notebook_path=path))
    return render_template('404.html'), 404

@main_bp.route('/refresh_repo')
@login_required
def refresh_repo():
    # Kullanıcı yetkisini kontrol et
    if not (current_user.is_admin() or current_user.is_teacher()):
        flash('Bu işlem için yetkiniz bulunmuyor.')
        return redirect(url_for('main.index'))

    try:
        # Repository'yi güncelle veya klonla
        result = clone_repo()

        if result:
            flash('Notebook deposu başarıyla güncellendi.', 'success')
        else:
            flash('Depo güncellenirken hata oluştu.', 'error')
    except Exception as e:
        flash(f'Depo güncellenirken hata oluştu: {str(e)}', 'error')

    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/language/<language>')
def set_language(language):
    session['language'] = language
    return redirect(request.referrer or url_for('main.index'))


@main_bp.route('/components/<path:filename>')
def serve_component(filename):
    # JSX bileşenleri templates/js/components klasöründe
    return send_from_directory('templates/js/components', filename)

@main_bp.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@main_bp.route('/about')
def about():
    return render_template('about.html')