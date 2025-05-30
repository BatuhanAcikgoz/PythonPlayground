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
    """
    NotebookService sınıfı, Jupyter Notebook dosyalarını yönetmek, kod çalıştırmak ve Socket.IO desteği ile
    çıktıları paylaşmak için araçlar sağlar.

    Bu sınıf, bir repository yönetimi yaparak notebook dosyalarını indirebilir veya
    güncelleyebilir. Ayrıca, bir kullanıcı için kod çalıştırma ortamını simule eder
    ve Socket.IO entegrasyonu ile etkileşimli çıktı sunabilir. Seçenek olarak, kodu
    direkt olarak çalıştırma ve çıktısını döndürme yeteneklerine de sahiptir.
    """
    def __init__(self):
        # Repository URL ve klasör yolunu tanımla
        self.repo_url = 'https://github.com/msy-bilecik/ist204_2025'
        self.repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')
        self.lock = threading.Lock()
        self.user_namespaces = {}  # Kullanıcı başına çalıştırma ortamları
        self.input_response = None  # Input için global değişken

    def ensure_repo_exists(self):
        """
        ensure_repo_exists fonksiyonu, bir Git reposunun belirtilen dizinde mevcut
        olup olmadığını kontrol eder ve mevcut değilse klonlama işlemi yapar. Eğer
        repo zaten mevcutsa, güncelleme işlemi gerçekleştirilir. Güncelleme sırasında
        hata oluşması durumunda repo yeniden sıfırdan klonlanır. İşlem sonunda
        klonlanan veya güncellenen repo dizininin yolunu döndürür.

        Arguments:
            None

        Returns:
            str: Klonlanan veya güncellenmiş olan repo dizininin yolu. Eğer hata oluşursa None döner.
        """
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
        """
        Belirtilen yolda bulunan Jupyter not defterini yükleyen ve içeriğini bir sözlük yapısında
        dönen bir yöntem. Girdi olarak gelen not defteri dosyasının güvenlik önlemleriyle kontrolü
        sağlanır, ardından JSON biçiminde yüklenerek nbformat kütüphanesi yardımıyla doğrulanır
        ve okunur.

        Arguments:
            notebook_path (str): Yüklenmek istenen Jupyter not defterinin yolu.

        Returns:
            Optional[dict]: Başarıyla yüklenen not defteri dosyasının içerik bilgilerini içeren bir
            sözlük. Eğer yükleme başarısız olursa None döner.

        Raises:
            ValueError: Geçersiz bir yol belirtilmişse veya path traversal güvenlik hatası oluşmuşsa.
            FileNotFoundError: Belirtilen dosya yolu mevcut değilse.
        """
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
        """
        Belirtilen kodun bir alt işlemde çalıştırılmasını ve kodun çıktısını döndürmeyi amaçlayan bir fonksiyon.

        Functions:
            run_code: Kullanıcı ID'sine bağlı veya kullanıcı ID'siz kodun çalıştırılmasını sağlar.

        Args:
            code (str): Çalıştırılacak Python kodunu içeren metin.
            user_id (Optional[int]): Kullanıcı kimliğini temsil eden opsiyonel bir parametre.

        Returns:
            dict: Kodun başarıyla çalışıp çalışmadığını ve çıktı ya da hata mesajını içeren bir sözlük döndürür.

        Raises:
            Exception: Alt işlem çalıştırılırken oluşan tüm hataları kapsar.
        """
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
        """
        Kullanıcı tarafından gönderilen Python kodunu bir "sandbox" ortamında çalıştıran, çıktılarını
        gerçek zamanlı olarak bir Socket.IO bağlantısı üzerinden ileten ve gerektiğinde kullanıcıdan
        input alarak yürütmeyi sürdüren bir işlevdir. Kullanıcıların kod çalıştırma süreçlerini izleyebilmesine
        ve dışarıdan gelen inputlarla yönlendirebilmesine imkan tanır.

        Parameters:
            code: str
                Çalıştırılacak Python kodu.
            user_id: str
                Kullanıcının kimliğini belirten bir tanıtıcı.
            socketio: SocketIO, optional
                Socket.IO bağlantı nesnesi. Varsayılan olarak None.

        Returns:
            dict
                İşlevin başarı durumunu belirten bir sözlük.
                Örneğin:
                {'success': True} başarılı işlem sonrası döndürülür.
                {'success': False, 'error': 'Hata mesajı'} hata durumunda döndürülür.

        Raises:
            Exception
                Gönderilen kodun yürütülmesi sırasında oluşabilecek tüm istisnalar yakalanır
                ve Socket.IO bağlantısına bir hata çıktısı olarak iletilir.
        """
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
            """
            NotebookService sınıfı, bir kullanıcıdan bir kod parçasını çalıştırma talebi alarak bu süreci yönetir
            ve sonuçları istemciye uygun bir şekilde iletir. Kodu yürütme sırasında gerektiğinde kullanıcıdan
            girdi almayı destekler ve istemciye parçalı çıktı gönderebilir.

            Metotlar:
                - handle_socket_run_code: Gelen kod çalıştırma taleplerini işler, çıktıları gerekirse parçalı şekilde iletir.

            Metotların detaylı açıklamaları aşağıda verilmiştir.
            """
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
        """
        Fonksiyon bir değer alır ve bu değeri input_response niteliğine atar.

        Args:
            value: Atanacak değer. Parametre tipi belirtilmediğinden
                   çağrıyla bu sorumluluk geliştiriciye bırakılmıştır.

        Returns:
            None
        """
        self.input_response = value

    def reset_namespace(self, user_id):
        """
        Kullanıcıya ait ad alanını varsayılan değerlerine sıfırlayan bir fonksiyon.

        Bu fonksiyon, kullanıcının mevcut ad alanını temizler ve varsayılan '__builtins__' ile yeniden
        başlatır. Kullanıcının kimliğini temel alarak ad alanını günceller ya da oluşturur.

        Args:
            user_id (str): Ad alanı sıfırlanacak kullanıcının benzersiz kimlik numarası.

        Returns:
            None
        """
        self.user_namespaces[user_id] = {'__builtins__': builtins}