from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import login_required, current_user
from flask import send_from_directory
import os
import subprocess
import shutil

main_bp = Blueprint('main', __name__)

def clone_repo():
    """
    Repository'yi klonlayan veya mevcut ise güncelleyen bir fonksiyon.

    Bu fonksiyon, belirtilen bir URL'den bir GitHub repository'sini çalışma
    dizinine indirir ya da halihazırda dizinde bulunuyorsa güncellemeye çalışır.
    Eğer güncelleme işlemi başarısız olursa, mevcut repository dizinini siler ve
    temiz bir şekilde yeniden klonlar.

    Returns:
        str: Klonlanan veya güncellenen repository'nin dizin yolu. Eğer işlem
        başarısız olursa None döndürülür.
    """
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
    """
    Bu fonksiyon, belirli bir dizindeki notebook dosyalarını kontrol eder ve
    bunları görüntülemek için bir HTML şablonuna yönlendirir. Eğer dizin veya
    notebook dosyaları mevcut değilse, bu duruma uygun hata mesajları döndürür.

    Args:
        None

    Returns:
        HTML şablonu (str): 'index.html' şablonu, notebook dosyalarını ve/veya hata
        mesajlarını içerir.

    Raises:
        Exception: Repository klonlama işlemi sırasında oluşan hatalar
                    iletilir.
    """
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

    return render_template('index.html', notebooks=notebooks, error_message=error_message)

@main_bp.route('/<path:path>')
def redirect_notebook(path):
    """
    Rota işlevi. Verilen yolun (path) bir Jupyter Notebook dosyasına
    işaret edip etmediğini kontrol eder. Eğer yol bir `.ipynb` dosyasına
    işaret ediyorsa, bu dosya için bir yönlendirme yapar. Aksi takdirde
    bir 404 hata sayfasını render eder.

    Parameters:
        path (str): İşleme alınacak olan yolun tam adı.

    Returns:
        Werkzeug Response: Eğer yol bir Jupyter Notebook dosyasına işaret
        ediyorsa bir yönlendirme cevabı döner. Yol `.ipynb` dosyası değilse,
        404 hata sayfasını bir HTTP 404 durumu ile birlikte döner.
    """
    if path.endswith('.ipynb'):
        return redirect(url_for('notebook.view', notebook_path=path))
    return render_template('404.html'), 404

@main_bp.route('/refresh_repo')
@login_required
def refresh_repo():
    """
    Ana bloğa ait '/refresh_repo' yolunu işleyen ve kullanıcı deposunu
    güncelleyen bir Flask endpoint fonksiyonudur.

    Functions:
        refresh_repo: Kullanıcı oturum açmış ve gerekli yetkilere sahipse,
                      kaydedilmiş notebook deposunu güncelleyen veya klonlayan
                      bir işlevdir.

    Args:
        None

    Returns:
        Werkzeug.wrappers.response.Response: Yönlendirme metodu ile ana sayfaya
                                             yönlendirme veya ilgili flash mesajları

    Raises:
        None
    """
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


@main_bp.route('/language/<language>')
def set_language(language):
    """
    Rota handlerı belirli bir dil seçimini oturumda saklar ve önceki sayfaya ya da ana sayfaya yönlendirir.

    Args:
        language (str): Kullanıcının seçtiği dil kodu.

    Returns:
        werkzeug.wrappers.response.Response: Kullanıcıyı önceki sayfaya ya da ana sayfaya yönlendiren yanıt.
    """
    session['language'] = language
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/components/<path:filename>')
def serve_component(filename):
    """
    Flask route işlevi: Belirtilen dosyanın sunulmasını sağlar.

    Bu işlev, belirtilen bir dosya yolunu alır ve server tarafından belirtilen
    dizinde bulunan dosyayı istemciye sunar. Bu işlev, genellikle statik dosyaları
    dinamik bir şekilde sunmak için kullanılır.

    Args:
        filename (str): Sunulacak dosyanın yolu. Yol, işlev için belirtilmiş
            olan 'templates/js/components' dizinine bağlıdır.

    Returns:
        flask.wrappers.Response: Flask tarafından oluşturulmuş HTTP cevabı. Bu
            cevap istemciye belirtilen dosya içeriğini sunar.
    """
    return send_from_directory('templates/js/components', filename)

@main_bp.route('/leaderboard')
def leaderboard():
    """
    Bu fonksiyon, '/leaderboard' rotasında çalışan bir Flask rota fonksiyonudur ve
    `leaderboard.html` adlı HTML şablonunu döndürür. Uygulamanın liderlik tablosu
    sayfasını oluşturur.

    Returns:
        Flask.Response: `leaderboard.html` şablonunu içeren HTTP yanıtı.
    """
    return render_template('leaderboard.html')

@main_bp.route('/about')
def about():
    """
    Flask Blueprint route "/about" fonksiyonunu tanımlayan işlev. Bu işlev, "/about" rotasına yapılan
    GET istekleri için belirli bir HTML şablonunu döndürmek amacıyla kullanılır.

    Returns:
        Response: Flask tarafından döndürülen ve belirtilen şablonu içeren HTTP yanıtı.
    """
    return render_template('about.html')