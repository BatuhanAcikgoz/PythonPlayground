import os
import json
import nbformat
import subprocess
import sys
import io
import shutil
import uuid
import builtins
from flask import current_app
from flask_socketio import emit
import threading

class NotebookService:
    """NotebookService sınıfı, Jupyter notebook'ları ile etkileşim ve kod çalıştırma işlemlerini yönetir."""
    def __init__(self):
        # Repository URL ve klasör yolunu tanımla
        self.repo_url = 'https://github.com/msy-bilecik/ist204_2025'
        self.repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')
        self.lock = threading.Lock()
        self.user_namespaces = {}  # Kullanıcı başına çalıştırma ortamları
        self.input_response = None  # Input için global değişken

    def ensure_repo_exists(self):
        """Repository klonlama veya güncelleme işlemi"""
        if not os.path.exists(self.repo_dir):
            print(f"Repository {self.repo_dir} dizinine klonlanıyor")
            try:
                subprocess.run(['git', 'clone', self.repo_url, self.repo_dir], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Repository klonlanırken hata: {str(e)}")
                return None
        else:
            print(f"{self.repo_dir} dizinindeki repo güncelleniyor")
            try:
                # En son değişiklikleri çek
                subprocess.run(['git', 'pull'], cwd=self.repo_dir, check=True)
            except subprocess.CalledProcessError:
                print("Repo güncellenirken hata oluştu, yeniden klonlanıyor")
                # Çekme başarısız olursa, temiz bir şekilde klonla
                shutil.rmtree(self.repo_dir, ignore_errors=True)
                try:
                    subprocess.run(['git', 'clone', self.repo_url, self.repo_dir], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Repository yeniden klonlanırken hata: {str(e)}")
                    return None

        return self.repo_dir

    def get_notebook(self, notebook_path):
        """Belirtilen yoldaki notebook dosyasını açar ve içeriğini döndürür"""
        repo_dir = self.ensure_repo_exists()
        if not repo_dir:
            return None

        # 'view/' önekini kaldır (varsa)
        if notebook_path.startswith('view/'):
            notebook_path = notebook_path[5:]

        full_path = os.path.normpath(os.path.join(repo_dir, notebook_path))

        # Güvenlik kontrolü - path traversal önleme
        if not full_path.startswith(repo_dir):
            raise ValueError("Geçersiz notebook yolu")

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Notebook bulunamadı: {notebook_path}")

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                notebook_content = json.load(f)

            # nbformat ile notebook'u doğrula ve oku
            notebook = nbformat.reads(json.dumps(notebook_content), as_version=4)

            # Ayrıca cells erişimini kolaylaştırmak için
            return {
                'path': notebook_path,
                'name': os.path.basename(notebook_path),
                'content': notebook,
                'cells': notebook.cells  # cells doğrudan erişilebilir olsun
            }
        except Exception as e:
            print(f"Notebook yüklenirken hata: {str(e)}")
            return None

    def run_code(self, code, user_id=None):
        """Kodu çalıştırır ve sonucu döndürür (Socket.IO olmadan)"""
        try:
            # Kodu alt işlemde çalıştır
            process = subprocess.Popen(
                [sys.executable, '-c', code],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()

            if process.returncode == 0:
                return {'success': True, 'output': stdout}
            else:
                return {'success': False, 'error': stderr}
        except Exception as e:
            current_app.logger.error(f"Error running code: {str(e)}")
            return {'success': False, 'error': 'An internal error has occurred.'}

    def handle_socket_run_code(self, code, user_id, socketio=None):
        """Socket.IO ile kodu çalıştır ve çıktıyı Socket.IO kullanarak gönder"""
        if not socketio:
            return {'success': False, 'error': 'Socket.IO bağlantısı bulunamadı'}

        # Kullanıcı namespace'i oluştur
        if user_id not in self.user_namespaces:
            self.user_namespaces[user_id] = {'__builtins__': builtins}

        user_namespace = self.user_namespaces[user_id]

        # Çıktıyı yakalamak için StringIO kullan
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        # Takip edilen çıktı konumu
        last_output_position = 0

        # Özel input fonksiyonu
        def custom_input(prompt=''):
            # Bekleyen çıktıyı önce gönder
            nonlocal last_output_position
            current_output = redirected_output.getvalue()[last_output_position:]
            if current_output:
                emit('partial_output', {'output': current_output})
                last_output_position = len(redirected_output.getvalue())

            # Input iste
            self.input_response = None
            emit('input_request', {'prompt': prompt})

            # input_response ayarlanması için bekle
            while self.input_response is None:
                socketio.sleep(0.1)

            response = self.input_response
            self.input_response = None
            return response

        old_input = builtins.input
        user_namespace['input'] = custom_input

        try:
            # Basit ifade mi kontrolü
            is_simple_expression = False
            try:
                compiled_code = compile(code, '<string>', 'eval')
                is_simple_expression = True
            except SyntaxError:
                pass

            if is_simple_expression:
                # Basit ifade - değerlendir ve sonucu göster
                result = eval(compiled_code, user_namespace)
                if result is not None:
                    print(repr(result))
            else:
                # AST kullanarak son ifadenin değerini kontrol et
                import ast
                try:
                    parsed = ast.parse(code)
                    if parsed.body:
                        last_stmt = parsed.body[-1]
                        if isinstance(last_stmt, ast.Expr):
                            # Son ifade dışındaki tüm kod
                            lines = code.splitlines()
                            last_line_index = last_stmt.lineno - 1  # ast satır numaraları 1-indeksli

                            if len(lines) == 1:
                                exec(code, user_namespace)
                            else:
                                # Son ifade hariç tümünü çalıştır
                                exec('\n'.join(lines[:last_line_index]), user_namespace)
                                # Son ifadeyi değerlendir ve sonucunu göster
                                last_expr = lines[last_line_index]
                                result = eval(last_expr, user_namespace)
                                if result is not None:
                                    print(repr(result))
                        else:
                            # İfade değil, normal çalıştır
                            exec(code, user_namespace)
                    else:
                        # Boş kod
                        exec(code, user_namespace)
                except SyntaxError:
                    # AST ayrıştırma başarısız olursa, normal çalıştır
                    exec(code, user_namespace)

            # Kalan çıktıyı gönder
            final_output = redirected_output.getvalue()[last_output_position:]
            if final_output:
                emit('partial_output', {'output': final_output})
        except Exception as e:
            emit('partial_output', {'output': str(e)})
        finally:
            # Orijinal stdout'u geri yükle
            sys.stdout = old_stdout
            builtins.input = old_input

        emit('code_output', {'output': ''})  # Tamamlandı sinyali
        return {'success': True}

    def set_input_response(self, value):
        """Socket.IO input_response olayı için işleyici"""
        self.input_response = value

    def reset_namespace(self, user_id):
        """Kullanıcının namespace'ini sıfırla"""
        self.user_namespaces[user_id] = {'__builtins__': builtins}