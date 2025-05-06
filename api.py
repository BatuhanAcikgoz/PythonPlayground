from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
import platform
import psutil
import flask
from typing import Optional, List
import nbformat
import os
import time
import hashlib
import re
import json
from datetime import datetime, timedelta
from pydantic import BaseModel
import traceback
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config

# Veritabanı bağlantısı
DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

api = FastAPI(title="Python Playground API", version="1.0.0")

# CORS ekle - domain sınırlaması
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5000"],  # Sadece Flask uygulamasının adresine izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Veritabanı oturumu dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Admin yetkilendirme (basit)
def get_current_admin():
    # Gerçek bir uygulamada JWT token vb. ile yetkilendirme yapılmalı
    return {"is_admin": True}


class ServerStatus(BaseModel):
    python_version: str
    flask_version: str
    mysql_version: str
    ram_used: float
    ram_total: float
    cpu_usage: float
    process_ram_used: float
    process_ram_allocated: float


@api.get("/api/server-status", response_model=ServerStatus)
def server_status(admin: dict = Depends(get_current_admin), db=Depends(get_db)):
    # Python sürümü
    python_version = platform.python_version()

    # Flask sürümü
    flask_version = flask.__version__

    # MySQL sürümü
    mysql_result = db.execute(text("SELECT VERSION() as version")).first()
    mysql_version = mysql_result.version if mysql_result else "Unknown"

    # Sistem RAM kullanımı
    mem = psutil.virtual_memory()
    ram_used = round(mem.used / (1024 * 1024 * 1024), 2)  # GB
    ram_total = round(mem.total / (1024 * 1024 * 1024), 2)  # GB

    # Süreç RAM kullanımı
    process = psutil.Process(os.getpid())
    process_memory = process.memory_info()
    process_ram_used = round(process_memory.rss / (1024 * 1024 * 1024), 2)
    process_ram_allocated = round(process_memory.vms / (1024 * 1024 * 1024), 2)

    # CPU kullanımı
    cpu_usage = psutil.cpu_percent(interval=1)

    return {
        'python_version': python_version,
        'flask_version': flask_version,
        'mysql_version': mysql_version,
        'ram_used': ram_used,
        'ram_total': ram_total,
        'cpu_usage': cpu_usage,
        'process_ram_used': process_ram_used,
        'process_ram_allocated': process_ram_allocated
    }


# User model - sadece API amaçlı
class UserRole(BaseModel):
    id: int
    name: str


class UserData(BaseModel):
    id: int
    username: str
    email: str
    registered: str
    roles: List[str]


@api.get("/api/recent-users", response_model=List[UserData])
def recent_users(admin: dict = Depends(get_current_admin), db=Depends(get_db)):
    # Doğru import edilmiş text() kullanımı
    sql_query = text("""
        SELECT u.id, u.username, u.email, u.created_at
        FROM user u
        ORDER BY u.id DESC
        LIMIT 5
    """)

    result = db.execute(sql_query)

    users = []
    for row in result:
        # Kullanıcı rollerini al
        roles_query = text("""
            SELECT r.id, r.name
            FROM role r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = :user_id
        """)

        roles_result = db.execute(roles_query, {"user_id": row.id})

        roles = [role.name for role in roles_result]

        users.append({
            "id": row.id,
            "username": row.username,
            "email": row.email,
            "registered": row.created_at.strftime('%Y-%m-%d'),
            "roles": roles
        })

    return users

class EvaluationRequest(BaseModel):
    code: str
    function_name: str
    test_inputs: str
    solution_code: str

class EvaluationResult(BaseModel):
    is_correct: bool
    execution_time: float
    errors: List[str]
    test_count: int
    passed_tests: int
    failed_tests: int
    test_results: Optional[dict] = None


def check_indentation(code: str):
    """Kod içindeki girinti hatalarını kontrol eder"""
    lines = code.splitlines()

    # Tab ve boşluk karışımını kontrol et
    for i, line in enumerate(lines):
        if line.strip() and line.startswith(" ") and "\t" in line:
            return False, i + 1, "Tab ve boşluk karışımı tespit edildi"

    # Girinti tutarlılığını kontrol et
    try:
        # Gerçek Python derleyicisiyle girinti hatasını tespit et
        compile(code, "<string>", "exec")
        return True, 0, ""
    except IndentationError as e:
        # IndentationError, satır numarasını ve hata mesajını içerir
        return False, e.lineno, str(e)

    return True, 0, ""

def normalize_indentation(code: str) -> str:
    """Kod içindeki karışık girintileri normalleştirip tutarlı hale getirir"""
    lines = code.splitlines()
    normalized_lines = []

    # Her satır için
    for line in lines:
        if line.strip():  # Boş satır değilse
            # Satırın başındaki boşlukları say
            leading_space_count = len(line) - len(line.lstrip())
            leading_content = line[:leading_space_count]

            # Tab ve boşluk karışımını kontrol et ve düzelt
            if '\t' in leading_content and ' ' in leading_content:
                # Her tab'ı 4 boşlukla değiştir (Python standardı)
                fixed_indent = leading_content.replace('\t', '    ')
                normalized_lines.append(fixed_indent + line[leading_space_count:])
            elif '\t' in leading_content:
                # Tüm tab'ları 4 boşlukla değiştir
                fixed_indent = leading_content.replace('\t', '    ')
                normalized_lines.append(fixed_indent + line[leading_space_count:])
            else:
                normalized_lines.append(line)
        else:
            normalized_lines.append(line)

    return '\n'.join(normalized_lines)


@api.post("/api/evaluate", response_model=EvaluationResult)
def evaluate_solution(request: EvaluationRequest):
    """Kullanıcı kodunu değerlendirir ve sonuçları döndürür"""
    result = {
        "is_correct": False,
        "execution_time": 0,
        "test_count": 0,
        "test_results": {},
        "errors": []
    }

    # Kodu normalleştirme adımı ekle
    normalized_code = normalize_indentation(request.code)

    # Geliştirilmiş girinti kontrolü (normalleştirilmiş kod üzerinde)
    is_valid, line_num, error_msg = check_indentation(normalized_code)
    if not is_valid:
        result["errors"].append(f"Satır {line_num}'de girinti hatası: {error_msg}")
        return result

    test_inputs = []
    try:
        test_inputs = json.loads(request.test_inputs)
    except json.JSONDecodeError:
        result["errors"].append("Test girdileri geçerli JSON formatında değil")
        return result

    try:
        # Kullanıcı kodunu güvenli bir şekilde çalıştır (normalleştirilmiş kodu kullan)
        user_namespace = {}
        exec(normalized_code, user_namespace)
        user_function = user_namespace.get(request.function_name)

        if user_function is None:
            result["errors"].append(f"'{request.function_name}' adında bir fonksiyon bulunamadı")
            return result

        if not callable(user_function):
            result["errors"].append(f"'{request.function_name}' çağrılabilir bir fonksiyon değil")
            return result

        # Çözüm kodunu çalıştır
        solution_namespace = {}
        exec(request.solution_code, solution_namespace)
        solution_function = solution_namespace.get(request.function_name)

        if not solution_function:
            result["errors"].append("Çözüm fonksiyonu bulunamadı")
            return result

        # Testleri çalıştır
        all_correct = True
        start_time = time.time()

        for test_input in test_inputs:
            # Test girişlerinin liste olduğundan emin ol
            if not isinstance(test_input, list):
                test_input = [test_input]

            try:
                # Kullanıcı kodunu çalıştır
                user_result = user_function(*test_input)
                # Çözüm kodunu çalıştır
                expected_result = solution_function(*test_input)

                if user_result != expected_result:
                    all_correct = False
                    result["errors"].append(f"Girdi: {test_input}, Beklenen: {expected_result}, Alınan: {user_result}")

            except TypeError as e:
                error_msg = str(e)
                if "'builtin_function_or_method' object is not subscriptable" in error_msg:
                    # Hata konumunu bul
                    import traceback
                    tb = traceback.extract_tb(e.__traceback__)
                    line_number = None

                    # Kullanıcı kodundaki satır numarasını bul
                    for frame in tb:
                        if frame.filename == "<string>":
                            line_number = frame.lineno
                            break

                    # Daha açıklayıcı hata mesajı (satır numarası ile)
                    line_info = f"Satır {line_number}: " if line_number else ""
                    result["errors"].append(
                        f"{line_info}Yerleşik fonksiyon/metot indeks notasyonu ile kullanılamaz. "
                        "Örnek: 'max[0]' yerine 'max(liste)' kullanmalısınız."
                    )
                else:
                    result["errors"].append(f"Tip hatası: {error_msg}")
                all_correct = False

            except Exception as e:
                result["errors"].append(f"Çalışma zamanı hatası: {str(e)}")
                all_correct = False

        end_time = time.time()
        execution_time = round((end_time - start_time) * 1000, 2)  # milisaniye cinsinden

        result["is_correct"] = all_correct
        result["execution_time"] = execution_time

        return result

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        result["errors"].append(f"Değerlendirme hatası: {str(e)}")
        result["error_details"] = error_trace
        return result

# --- AI Notebook Summary Modelleri ---
class NotebookSummaryRequest(BaseModel):
    notebook_path: str


class NotebookSummaryResponse(BaseModel):
    summary: str
    code_explanation: str
    last_updated: str
    error: Optional[str] = None


# AI model ile iletişim için yardımcı sınıf
class AIClient:
    def __init__(self, api_provider, api_key, model_name):
        self.api_provider = api_provider
        self.api_key = api_key
        self.model = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1"

    def chat_completion(self, messages, max_tokens=100000):
        try:
            # Gemini API
            if self.api_provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)

                # Model adını düzelt
                gemini_model = self.model
                if "models/" in gemini_model:
                    gemini_model = gemini_model.replace("models/", "")

                # Gemini 1.5 modellerini doğru formatta kullan
                if gemini_model == "gemini-1.5-pro":
                    gemini_model = "gemini-1.5-pro-latest"
                elif gemini_model == "gemini-1.5-flash":
                    gemini_model = "gemini-1.5-flash-latest"

                # Mesajları Gemini formatına dönüştürme
                system_prompt = None
                user_messages = []
                assistant_messages = []

                for msg in messages:
                    if msg["role"] == "system":
                        system_prompt = msg["content"]
                    elif msg["role"] == "user":
                        user_messages.append(msg["content"])
                    elif msg["role"] == "assistant":
                        assistant_messages.append(msg["content"])

                gen_config = genai.GenerationConfig(max_output_tokens=max_tokens)
                gen_model = genai.GenerativeModel(model_name=gemini_model, generation_config=gen_config)

                chat = gen_model.start_chat()

                if system_prompt:
                    chat.send_message(f"SYSTEM: {system_prompt}")

                for i in range(max(len(user_messages), len(assistant_messages))):
                    if i < len(user_messages):
                        if i < len(assistant_messages):
                            chat.send_message(user_messages[i])
                            chat.send_message(assistant_messages[i])
                        else:
                            prompt = user_messages[i]
                    if i < len(assistant_messages) and i >= len(user_messages):
                        chat.send_message(assistant_messages[i])

                prompt = user_messages[-1] if user_messages else (
                        system_prompt or "Notebook hakkında bilgi verir misiniz?")

                response = chat.send_message(prompt)

                return {"content": response.text if hasattr(response, 'text') else str(response)}

            else:
                return {"error": "Desteklenmeyen AI sağlayıcısı"}

        except Exception as e:
            return {"error": str(e)}


@api.post("/api/notebook-summary", response_model=NotebookSummaryResponse)
def get_notebook_summary(request: NotebookSummaryRequest, force_update: bool = False, db=Depends(get_db)):
    """Notebook için özet oluşturur veya var olan özeti döndürür"""
    try:
        # Veritabanında özet var mı kontrol et
        summary_query = text("""
                             SELECT notebook_path, summary, code_explanation, last_updated
                             FROM notebook_summary
                             WHERE notebook_path = :path
                             """)

        existing = db.execute(summary_query, {"path": request.notebook_path}).first()

        # Force update parametresi ile zorla güncelleme imkanı, boş özet kontrolü eklendi
        if not force_update and existing and existing.summary and len(existing.summary.strip()) > 10:
            return {
                "summary": existing.summary,
                "code_explanation": existing.code_explanation,
                "last_updated": existing.last_updated.isoformat(),
                "error": None
            }

        # Ayarları veritabanından al
        settings = {}
        settings_query = text("SELECT `key`, `value` FROM settings WHERE `key` LIKE 'ai_%'")
        for row in db.execute(settings_query):
            settings[row.key] = row.value

        api_provider = settings.get('ai_api_provider', 'gemini')
        api_key = settings.get('ai_api_key', '')
        model_name = settings.get('ai_default_model', 'gemini-1.5-flash')
        max_tokens = int(settings.get('ai_max_token_limit', 10000000))
        enabled = settings.get('ai_enable_features', 'true').lower() == 'true'

        if not enabled:
            return {"summary": "", "code_explanation": "", "last_updated": datetime.utcnow().isoformat(),
                    "error": "AI özeti özelliği devre dışı bırakılmıştır."}

        if not api_key:
            return {"summary": "", "code_explanation": "", "last_updated": datetime.utcnow().isoformat(),
                    "error": "API anahtarı bulunamadı."}

        # Notebook dosyasının tam yolunu oluştur
        repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')
        notebook_file_path = os.path.join(repo_dir, request.notebook_path)

        if not os.path.exists(notebook_file_path):
            raise HTTPException(status_code=404, detail=f"Notebook bulunamadı: {request.notebook_path}")

        # Notebook içeriğini oku
        with open(notebook_file_path, 'r', encoding='utf-8') as f:
            notebook_content = f.read()

        # Jupyter notebook formatını parse et
        nb = nbformat.reads(notebook_content, as_version=4)

        # Metin içeriğini çıkart
        text_content = ""
        code_cells = []
        numbered_code_cells = []

        cell_number = 1
        for cell in nb.cells:
            if cell.cell_type == 'markdown':
                text_content += cell.source + "\n\n"
            elif cell.cell_type == 'code':
                code_cells.append(cell.source)
                cell_content = f"## Hücre {cell_number}:\n```python\n{cell.source}\n```"
                numbered_code_cells.append(cell_content)
                cell_number += 1

        # AI istemcisini oluştur
        client = AIClient(api_provider, api_key, model_name)

        # API bağlantı testi - sağlamlık kontrolü
        test_response = client.chat_completion(
            messages=[
                {"role": "system", "content": "Kısa bir test mesajı"},
                {"role": "user", "content": "Çalışıyor musun?"}
            ],
            max_tokens=100
        )

        if "error" in test_response:
            return {"summary": "", "code_explanation": "", "last_updated": datetime.utcnow().isoformat(),
                    "error": f"AI servisi bağlantı hatası: {test_response.get('error')}"}

        if not test_response.get("content"):
            return {"summary": "", "code_explanation": "", "last_updated": datetime.utcnow().isoformat(),
                    "error": "AI servisi boş yanıt döndürdü. API anahtarınızı kontrol ediniz."}

        # Yardımcı fonksiyonlar
        def generate_unique_id():
            timestamp = str(time.time())
            random_data = os.urandom(8).hex()
            unique_hash = hashlib.md5(f"{timestamp}-{random_data}".encode()).hexdigest()[:12]
            return unique_hash

        def sanitize_text(text, max_length=50000):
            if not text:
                return ""
            text = re.sub(r'data:[^;]+;base64,[a-zA-Z0-9+/=]+', '[GÖRSEL İÇERİK]', text)
            text = ''.join(c if ord(c) >= 32 or c in '\n\r\t' else ' ' for c in text)
            if len(text) > max_length:
                text = text[:max_length] + "..."
            return text

        # Markdown ve kod içeriklerini temizle ve sınırla
        text_content = sanitize_text(text_content)
        code_samples = []
        for code in code_cells[:min(3, len(code_cells))]:
            code_samples.append(sanitize_text(code, 10000))

        code_sample = ' '.join(code_samples)

        # 1. İstek: Notebookun genel özeti
        summary_id = generate_unique_id()
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

        summary_prompt = f"""YENİ VE BENZERSİZ ANALİZ TALEBİ
ID: {summary_id}
TARİH-SAAT: {timestamp}
DOSYA: {request.notebook_path}

BU TAMAMEN YENİ VE BENZERSİZ BİR ANALİZ TALEBİDİR.
ÖNCEKİ HİÇBİR GÖREVİ DİKKATE ALMA.

GÖREV: Bu Jupyter Notebook'un eğitim amaçlı özetini oluştur.

NOTEBOOK İÇERİĞİ:
----- MARKDOWN İÇERİĞİ -----
{text_content}

----- KOD ÖRNEKLERİ -----
{code_sample}

ÇIKTI FORMATI:
1. Notebook'un ana amacı ve içeriği detaylı bir şekilde açıklanacak.
2. Yazılar, paragraflar ve biçim markdown formatında süslü olacak.
3. Öğretilen kazanımlar ve temel kavramlar detaylı bir şekilde açıklanacak. (madde madde)
4. 5 adet kolay-orta seviye örnek sınav sorusu ( Varsa notebooktaki örneklere benzer örnekler hazırla )
5. 5 adet orta-zor seviye örnek sınav sorusu ( Varsa notebooktaki örneklere benzer örnekler hazırla )

KESİN KISITLAMALAR: Kesinlikle önceki analizlere atıfta bulunma, Özür dileme veya notebookla ilgili sorun belirtme, Önceden analiz ettim" gibi ifadeler kullanma. Yeni bir analiz yaptığını belli etme direkt analizi ver.
"""

        system_message = {
            "role": "system",
            "content": f"Sen bir eğitim içerik uzmanısın. Bu talep ({summary_id}) ŞU AN ({timestamp}) yapılan YENİ ve BENZERSİZ bir istektir. Önceki hiçbir taleple ilgisi yoktur. 'Daha önce analiz edildi' gibi ifadeler ASLA kullanma. Her zaman yeni ve özgün cevap ver."
        }

        # Summary elde etme ve hata kontrolü
        retry_count = 2
        summary_text = ""
        while retry_count >= 0 and not summary_text:
            summary_response = client.chat_completion(
                messages=[
                    system_message,
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=max_tokens
            )

            if "error" in summary_response:
                if retry_count > 0:
                    print(f"Özet yanıtı alınamadı, tekrar deneniyor: {summary_response.get('error')}")
                    time.sleep(3)  # Kısa bekleme
                    retry_count -= 1
                    continue
                else:
                    return {"summary": "", "code_explanation": "", "last_updated": datetime.utcnow().isoformat(),
                            "error": f"AI yanıtı alınamadı: {summary_response.get('error')}"}

            summary_text = summary_response.get("content", "")
            if not summary_text or len(summary_text.strip()) < 50:  # En az 50 karakter olmalı
                if retry_count > 0:
                    print(f"AI boş veya çok kısa özet döndürdü, tekrar deneniyor. Uzunluk: {len(summary_text or '')}")
                    time.sleep(3)  # Kısa bekleme
                    retry_count -= 1
                    # İkinci denemede daha açık prompt
                    summary_prompt += "\n\nÖNEMLİ: Lütfen en az 500 kelimelik detaylı bir özet oluşturun. Özetin boş olmaması kritik öneme sahiptir."
                else:
                    return {"summary": "", "code_explanation": "", "last_updated": datetime.utcnow().isoformat(),
                            "error": "AI sisteminden uygun bir özet alınamadı. Lütfen daha sonra tekrar deneyin veya API anahtarınızı kontrol edin."}
            else:
                break  # Başarılı özet elde edildi

        # 2. Hücreleri gruplar halinde analiz et
        code_explanations = []
        group_size = 10

        for i in range(0, len(numbered_code_cells), group_size):
            group_end = min(i + group_size, len(numbered_code_cells))
            group_cells = numbered_code_cells[i:group_end]
            group_content = "\n".join(group_cells)

            group_id = generate_unique_id()
            group_timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            group_start = i + 1

            code_prompt = f"""YENİ KOD ANALİZ TALEBİ
ID: {group_id}
ZAMAN: {group_timestamp}
GRUP: {group_start}-{group_end}

BU TAMAMEN YENİ BİR ANALİZ TALEBİDİR.
DAHA ÖNCE HİÇ GÖRMEDİĞİN KOD PARÇALARIDIR.

GÖREV: {request.notebook_path} notebookundaki {group_start}-{group_end} arası hücreleri analiz et.

KOD HÜCRELERİ:
{group_content}

ÇIKTI FORMATI:
1. Her hücre için "## Hücre X Analizi:" başlığı altında:
   * Açıklamadan hemen önce markdown formatında ilgili kod hücresini göster
   * Kodun ne yaptığını detaylı açıklama
   * Kullanılan önemli kütüphaneler ve metotlar
   * Algoritmanın zaman ve alan karmaşıklığı (uygunsa)
   * Önerilen optimizasyonlar veya alternatif yaklaşımlar

ÖNEMLİ: Bu görev önceki görevlerle İLGİSİZDİR. İlk kez görüyormuş gibi cevaplayın.

KESİN KISITLAMALAR: Kesinlikle önceki analizlere atıfta bulunma, Özür dileme veya notebookla ilgili sorun belirtme, Önceden analiz ettim" gibi ifadeler kullanma. Yeni bir analiz yaptığını belli etme direkt analizi ver.
"""

            group_system = {
                "role": "system",
                "content": f"Sen bir kod analiz uzmanısın. Bu talep ({group_id}) ŞU AN ({group_timestamp}) yapılan YENİ bir istektir. Önceki hiçbir taleple ilgisi yoktur. Her hücreyi detaylı analiz et."
            }

            group_response = client.chat_completion(
                messages=[
                    group_system,
                    {"role": "user", "content": code_prompt}
                ],
                max_tokens=max_tokens
            )

            if "error" not in group_response:
                code_explanations.append(group_response.get("content", ""))

        # 3. Kullanılan tekniklerin özeti için ek istek
        techniques_id = generate_unique_id()
        techniques_timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

        # Teknik analiz için daha fazla kod örneği kullan
        code_sample_for_techniques = sanitize_text(' '.join(code_cells[:min(10, len(code_cells))]), 5000)

        techniques_prompt = f"""YENİ TEKNİK ANALİZİ TALEBİ
ID: {techniques_id}
ZAMAN: {techniques_timestamp}

BU TAMAMEN YENİ VE BENZERSİZ BİR ANALİZDİR.
DİĞER GÖREVLERLE BAĞLANTISI YOKTUR.

GÖREV: {request.notebook_path} dosyasındaki tüm kodun kapsamlı teknik analizini yap.

KOD PARÇALARI:
{code_sample_for_techniques}

ÇIKTI FORMATI:
## Notebookun Teknik Özeti

1. Kullanılan Kütüphaneler:
   * [kütüphane adı] - [ana kullanım amacı ve işlevi]
   * ...

2. Tanımlanan Fonksiyonlar:
   * [fonksiyon adı] - [işlevi ve önemi]
   * ...

3. Kullanılan Programlama Yapıları:
   * Koşul İfadeleri (if-elif-else) - [nasıl kullanıldığı]
   * Döngüler (for, while) - [nasıl kullanıldığı]
   * List Comprehension - [varsa örnekleri]
   * Hata Yönetimi (try-except) - [varsa örnekleri]
   * ...

4. Veri Yapıları:
   * [kullanılan veri yapıları] - [nasıl kullanıldığı]
   * ...

5. Algoritma ve Teknikler:
   * [uygulanan özel teknikler/algoritmalar] - [kısa açıklaması]
   * ...

NOT: Tüm bu bilgileri maddeler halinde detaylı olarak ve kod örnekleriyle açıkla.
Bu özet, notebookun genel programlama tekniklerinin toplu bir analizi olmalıdır.

KESİN KISITLAMALAR: Kesinlikle önceki analizlere atıfta bulunma, Özür dileme veya notebookla ilgili sorun belirtme, Önceden analiz ettim" gibi ifadeler kullanma. Yeni bir analiz yaptığını belli etme direkt analizi ver.
"""

        techniques_system = {
            "role": "system",
            "content": f"Sen bir teknik programlama analisti olarak görev yapıyorsun. Bu talep ({techniques_id}) ŞU AN ({techniques_timestamp}) yapılan YENİ bir istektir. Tüm kodun teknik özelliklerini kapsamlı analiz et."
        }

        techniques_response = client.chat_completion(
            messages=[
                techniques_system,
                {"role": "user", "content": techniques_prompt}
            ],
            max_tokens=max_tokens
        )

        # Tüm analizleri birleştir
        try:
            code_explanation_combined = ""
            if code_explanations:
                code_explanation_combined = "\n\n".join(code_explanations)

            if "error" not in techniques_response:
                techniques_text = techniques_response.get("content", "")
                if techniques_text:
                    code_explanation_combined += "\n\n" + techniques_text
        except Exception as e:
            code_explanation_combined = f"Kod açıklaması oluşturulurken hata oluştu: {str(e)}"

        # Son kontrol - hala boş ise
        if not summary_text or len(summary_text.strip()) < 50:
            return {"summary": "", "code_explanation": "", "last_updated": datetime.utcnow().isoformat(),
                    "error": "AI özetleme işlemi başarısız oldu. Özet içeriği boş veya çok kısa."}

        # Veritabanına kaydet
        last_updated = datetime.utcnow()

        if existing:
            update_query = text("""
                                UPDATE notebook_summary
                                SET summary          = :summary,
                                    code_explanation = :code_explanation,
                                    last_updated     = :last_updated
                                WHERE notebook_path = :path
                                """)

            db.execute(update_query, {
                "summary": summary_text,
                "code_explanation": code_explanation_combined,
                "last_updated": last_updated,
                "path": request.notebook_path
            })
        else:
            insert_query = text("""
                                INSERT INTO notebook_summary (notebook_path, summary, code_explanation, last_updated)
                                VALUES (:path, :summary, :code_explanation, :last_updated)
                                """)

            db.execute(insert_query, {
                "path": request.notebook_path,
                "summary": summary_text,
                "code_explanation": code_explanation_combined,
                "last_updated": last_updated
            })

        db.commit()

        return {
            "summary": summary_text,
            "code_explanation": code_explanation_combined,
            "last_updated": last_updated.isoformat(),
            "error": None
        }

    except Exception as e:
        print(f"Notebook özeti oluşturulurken hata: {str(e)}")
        print(traceback.format_exc())
        return {
            "summary": "",
            "code_explanation": "",
            "last_updated": datetime.utcnow().isoformat(),
            "error": f"Notebook özeti oluşturulurken hata: {str(e)}"
        }

from typing import Optional, List

class DetailedQuestion(BaseModel):
    id: int
    title: str
    description: str
    difficulty: int
    points: int
    updated_at: str
    created_at: str

@api.get("/api/last-questions-detail", response_model=List[DetailedQuestion])
def get_last_questions_detail(limit: Optional[int] = 5, db=Depends(get_db)):
    """
    API fonksiyonunu, bir veritabanından en son eklenen programlama sorularını belirli bir
    sınır (varsayılan olarak 5) içinde sorgulatmak ve çağıran tarafın kullanımı için
    detaylı bir formatta döndürmek üzere tasarlar. Sorular, oluşturulma tarihine göre
    azalan bir biçimde sıralanır.

    Parameters:
        limit (Optional[int]): Sorguya dahil edilecek maksimum soru sayısını belirten
                               isteğe bağlı bir parametredir. Varsayılan olarak 5'tir.
        db: Veritabanı oturum bağımlılığını temsil eder.

    Returns:
        List: Her biri bir soru nesnesini ifade eden sözlük veri yapılarından oluşan bir
        liste döner. Dönüş verileri aşağıdaki bilgileri içerir:
            - id: Soru kimliği
            - title: Soru başlığı
            - description: Soru açıklaması
            - difficulty: Zorluk seviyesi
            - points: Sorunun puanı
            - created_at: Oluşturulma tarihi (Yıl-Ay-Gün formatında)
            - updated_at: Güncellenme tarihi (Yıl-Ay-Gün formatında)

    Raises:
        HTTPException: Eğer sorgu sırasında bir hata oluşursa, bu durum bir HTTP 500
        durum kodu ile birlikte hata detayları içeren bir istisna döner.
    """
    try:
        sql_query = text("""
            SELECT q.id, q.title, q.description, q.difficulty, q.points,
                   q.created_at, q.updated_at
            FROM programming_question q
            ORDER BY q.created_at DESC
            LIMIT :limit
        """)

        result = db.execute(sql_query, {"limit": limit})

        questions = []
        for row in result:
            questions.append({
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "difficulty": row.difficulty,
                "points": row.points,
                "updated_at": row.updated_at.strftime('%Y-%m-%d'),
                "created_at": row.created_at.strftime('%Y-%m-%d')
            })

        return questions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class LeaderboardEntry(BaseModel):
    """
    Bir liderlik tablosu girdisi için veri modelini temsil eder.

    LeaderboardEntry sınıfı, bir kullanıcının liderlik tablosundaki durumunu temsil
    eder. Kullanicinin adını, puanını ve sıralamasını içerir.

    Attributes:
        username (str): Kullanıcının kullanıcı adı.
        points (int): Kullanıcının kazandığı puan sayısı.
        rank (int): Kullanıcının liderlik tablosundaki sıralaması.
    """
    username: str
    points: int
    rank: int


class LeaderboardResponse(BaseModel):
    users: List[LeaderboardEntry]
    total: int
    limit: int

@api.get("/api/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard_api(limit: int = 20, db=Depends(get_db)):
    """
    Bu fonksiyon, kullanıcıları puanlarına göre sıralamak ve belirli bir sınır ile sınırlı
    bir liderlik tablosu döndürmek amacıyla kullanılır. Veritabanı ile iletişim kurarak
    puanlara göre bir sıralama yapar ve belirtilen limit kadar kullanıcıyı liderlik
    tablosuna ekler. Bunun sonucunda, her kullanıcının sıralamadaki konumu, kullanıcı
    adı ve puanı döndürülür. Liderlik tablosu, toplam kullanıcı sayısını ve sınır
    değerini de içerir.

    @param limit: Dönen kullanıcı sayısının sınırı. Varsayılan 20.
    @type limit: int
    @param db: Veritabanı bağlantısı için bağımlılık.
    @type db: Database connection provided by Depends(get_db)

    @return: Liderlik tablosu bilgilerini içeren bir sözlüğü döner. Sözlük, sıralanmış
    kullanıcı bilgileri listesini ve sınır değerini içerir.
    @rtype: dict

    @raises HTTPException: Veritabanı işlemi sırasında bir hata meydana gelirse veya
    istek gerçekleştirilemezse 500 durum kodu ile HTTPException yükselir.
    """
    try:
        # Kullanıcıları puanlarına göre sırala ve limit uygula
        sql_query = text("""
            SELECT id, username, points 
            FROM user 
            ORDER BY points DESC
            LIMIT :limit
        """)

        result = db.execute(sql_query, {"limit": limit})

        users = []
        for idx, row in enumerate(result):
            rank = idx + 1
            users.append({
                "username": row.username,
                "points": row.points,
                "rank": rank
            })

        return {
            "users": users,
            "total": len(users),
            "limit": limit
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SubmissionDetail(BaseModel):
    id: int
    user_id: int
    username: str
    question_id: int
    question_title: str
    is_correct: bool
    execution_time: float
    created_at: str

@api.get("/api/last-submissions", response_model=List[SubmissionDetail])
def get_last_submissions(limit: Optional[int] = 10, db=Depends(get_db)):
    """
    En son yapılan çözüm gönderimlerini listeler.
    """
    try:
        sql_query = text("""
            SELECT s.id, s.user_id, u.username, s.question_id, q.title as question_title, 
                   s.is_correct, s.execution_time, s.created_at
            FROM submission s
            JOIN user u ON s.user_id = u.id
            JOIN programming_question q ON s.question_id = q.id
            ORDER BY s.created_at DESC
            LIMIT :limit
        """)

        result = db.execute(sql_query, {"limit": limit})

        submissions = []
        for row in result:
            submissions.append({
                "id": row.id,
                "user_id": row.user_id,
                "username": row.username,
                "question_id": row.question_id,
                "question_title": row.question_title,
                "is_correct": row.is_correct,
                "execution_time": row.execution_time,
                "created_at": row.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return submissions

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import Optional

@api.get("/api/chart/registrations")
def chart_daily_registrations(days: Optional[int] = 30, db=Depends(get_db)):
    """Son X gün içindeki günlük kullanıcı kayıtlarını döndürür"""
    try:
        sql_query = text("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM user
            WHERE created_at >= CURDATE() - INTERVAL :days DAY
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """)

        result = db.execute(sql_query, {"days": days})

        data = []
        for row in result:
            data.append({
                "date": row.date.strftime('%Y-%m-%d'),
                "count": row.count
            })

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/chart/solved-questions")
def chart_solved_questions(days: Optional[int] = 30, db=Depends(get_db)):
    """Son X gün içindeki çözülen soruların sayısını döndürür"""
    try:
        sql_query = text("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM submission
            WHERE is_correct = 1 AND created_at >= CURDATE() - INTERVAL :days DAY
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """)

        result = db.execute(sql_query, {"days": days})

        data = []
        for row in result:
            data.append({
                "date": row.date.strftime('%Y-%m-%d'),
                "count": row.count
            })

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/chart/activity-stats")
def chart_activity_stats(days: Optional[int] = 30, db=Depends(get_db)):
    """Son X gün içindeki platform aktivitelerine ait özet istatistikler"""
    try:
        # Yeni kullanıcı kaydı sayısı
        users_query = text("""
            SELECT COUNT(*) as user_count
            FROM user
            WHERE created_at >= CURDATE() - INTERVAL :days DAY
        """)

        # Toplam soru çözüm sayısı
        submissions_query = text("""
            SELECT COUNT(*) as submission_count
            FROM submission
            WHERE created_at >= CURDATE() - INTERVAL :days DAY
        """)

        # Başarılı soru çözüm sayısı
        correct_submissions_query = text("""
            SELECT COUNT(*) as correct_count
            FROM submission
            WHERE is_correct = 1 AND created_at >= CURDATE() - INTERVAL :days DAY
        """)

        # Aktif kullanıcı sayısı
        active_users_query = text("""
            SELECT COUNT(DISTINCT user_id) as active_count
            FROM submission
            WHERE created_at >= CURDATE() - INTERVAL :days DAY
        """)

        # Sorguları çalıştır
        user_count = db.execute(users_query, {"days": days}).first().user_count
        submission_count = db.execute(submissions_query, {"days": days}).first().submission_count
        correct_count = db.execute(correct_submissions_query, {"days": days}).first().correct_count
        active_count = db.execute(active_users_query, {"days": days}).first().active_count

        return {
            "new_users": user_count,
            "total_submissions": submission_count,
            "correct_submissions": correct_count,
            "active_users": active_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class Badge(BaseModel):
    id: int
    name: str
    icon: str
    description: str


class Activity(BaseModel):
    id: int
    type: str
    content: dict
    date: str


class UserStats(BaseModel):
    solvedProblems: int
    codingDays: int
    activeDaysStreak: int
    solutedProblemsPercentage: float


class UserProfileData(BaseModel):
    username: str
    email: str
    joinDate: Optional[str]
    isCurrentUser: bool
    badges: List[Badge]
    stats: UserStats
    activities: List[Activity]
    dailyActivity: List[dict]

@api.get("/api/user-profile/{username}", response_model=UserProfileData)
def get_user_profile(username: str, current_user_id: Optional[int] = None, db=Depends(get_db)):
    """Kullanıcının profil verilerini döndürür"""
    try:
        # Kullanıcıyı bul
        user_query = text("""
                          SELECT id, username, email, created_at
                          FROM user
                          WHERE username = :username
                          """)
        user = db.execute(user_query, {"username": username}).first()

        if not user:
            raise HTTPException(status_code=404, detail=f"Kullanıcı bulunamadı: {username}")

        stats_query = text("""
                           SELECT (SELECT COUNT(*)
                                   FROM submission
                                   WHERE user_id = :user_id
                                     AND is_correct = 1)     as solved_problems,
                                  (SELECT COUNT(DISTINCT DATE (created_at))
                                   FROM submission
                                   WHERE user_id = :user_id) as coding_days,
                                  0                          as active_streak,
                                  IFNULL(
                                          (SELECT (COUNT(DISTINCT s.question_id) / (SELECT COUNT(*) FROM programming_question)) * 100
                                           FROM submission s
                                           WHERE s.user_id = :user_id
                                           AND s.is_correct = 1),
                                          0
                                        ) as question_participation_rate
                           """)

        stats = db.execute(stats_query, {"user_id": user.id}).first()

        badges = []
        activities = []

        # Kullanıcının çözülen problem aktivitelerini al
        activities_query = text("""
                                SELECT s.id, q.title as problem_title, s.created_at
                                FROM submission s
                                         JOIN programming_question q ON s.question_id = q.id
                                WHERE s.user_id = :user_id
                                  AND s.is_correct = 1
                                ORDER BY s.created_at DESC LIMIT 10
                                """)

        activities_result = db.execute(activities_query, {"user_id": user.id})
        for activity in activities_result:
            activities.append({
                "id": activity.id,
                "type": "problem_solved",
                "content": {"problem": activity.problem_title},
                "date": activity.created_at.strftime('%Y-%m-%d')
            })

        # Son 7 günlük aktiviteyi al
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=6)

        daily_activity_query = text("""
                                    SELECT DATE (created_at) as activity_date, COUNT(*) as count
                                    FROM submission
                                    WHERE user_id = :user_id
                                      AND DATE(created_at) BETWEEN :start_date
                                      AND :end_date
                                    GROUP BY DATE(created_at)
                                    ORDER BY DATE(created_at)
                                    """)

        daily_results = db.execute(daily_activity_query, {
            "user_id": user.id,
            "start_date": start_date,
            "end_date": end_date
        })

        # 7 günlük veriyi doldur (boş günler için 0 değeri)
        daily_activity = []
        date_counts = {row.activity_date: row.count for row in daily_results}

        for i in range(7):
            current_date = start_date + timedelta(days=i)
            label = ""
            if i == 6:
                label = "Bugün"
            elif i == 5:
                label = "Dün"
            else:
                label = f"{6 - i} gün önce"

            daily_activity.append({
                "date": current_date.strftime('%Y-%m-%d'),
                "label": label,
                "count": date_counts.get(current_date, 0)
            })

        is_current_user = current_user_id is not None and current_user_id == user.id

        return {
            "username": user.username,
            "email": user.email,
            "joinDate": user.created_at.strftime('%Y-%m-%d') if user.created_at else None,
            "isCurrentUser": is_current_user,
            "badges": badges,
            "stats": {
                "solvedProblems": stats.solved_problems if stats else 0,
                "codingDays": stats.coding_days if stats else 0,
                "activeDaysStreak": stats.active_streak if stats else 0,
                "solutedProblemsPercentage": stats.question_participation_rate if stats else 0
            },
            "activities": activities,
            "dailyActivity": daily_activity
        }
    except HTTPException as ex:
        raise ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel


class QuestionGenerationRequest(BaseModel):
    difficulty_level: int = 1
    topic: str = "genel"
    tags: list = []

class GeneratedQuestionResponse(BaseModel):
    title: str = ""
    description: str = ""
    function_name: str = ""
    difficulty: int = 1
    points: int = 10
    example_input: str = "Örnek girdi yok"
    example_output: str = "Örnek çıktı yok"
    test_inputs: str = "[]"
    solution_code: str = ""
    error: Optional[str] = None


@api.post("/api/generate-question", response_model=GeneratedQuestionResponse)
def generate_programming_question(difficulty_level: int = 2, db=Depends(get_db)):
    """Yapay zeka kullanarak yeni bir programlama sorusu oluşturur"""
    try:
        # Varsayılan sonuç şablonunu başlangıçta oluştur
        data = {
            "title": "",
            "description": "",
            "function_name": "",
            "difficulty": difficulty_level,
            "points": 10 + difficulty_level * 5,
            "example_input": "Örnek girdi yok",
            "example_output": "Örnek çıktı yok",
            "test_inputs": "[]",
            "solution_code": ""
        }

        # Veritabanı ayarlarını al
        settings = {}
        settings_query = text("SELECT `key`, `value` FROM settings WHERE `key` LIKE 'ai_%'")
        for row in db.execute(settings_query):
            settings[row.key] = row.value

        api_provider = settings.get('ai_api_provider', 'gemini')
        api_key = settings.get('ai_api_key', '')
        model_name = settings.get('ai_default_model', 'gemini-1.5-flash')
        enabled = settings.get('ai_enable_features', 'true').lower() == 'true'

        if not enabled:
            data["error"] = "AI özellikleri sistem ayarlarından devre dışı bırakılmış."
            return data

        # Zorluk seviyesi açıklamaları
        difficulty_desc = {
            1: "Kolay (Başlangıç seviyesi programcılar için)",
            2: "Orta (Temel Python bilgisi gerektirir)",
            3: "Zor (İleri düzey algoritmik düşünme gerektirir)",
            4: "Çok Zor (Karmaşık algoritmalar ve optimizasyon gerektirir)"
        }

        # Mevcut soru başlıklarını al
        existing_titles_query = text("SELECT title FROM programming_question")
        existing_titles = [row.title for row in db.execute(existing_titles_query)]

        # Rastgele konu seçimi
        topics = ["veri yapıları", "algoritmalar", "string işleme", "matematik",
                  "sayı teorisi", "arama", "sıralama", "dinamik programlama", "graf teorisi", "olasılık", "istatistik"]
        import random
        topic = random.choice(topics)
        selected_tags = random.sample(["python", "algoritma", "programlama", "veri yapıları"], 3)

        # AI prompt hazırla
        prompt = f"""Bir Python programlama sorusu oluştur.

Zorluk seviyesi: {difficulty_desc.get(difficulty_level, 'Orta')}
Konu: {topic}
Etiketler: {', '.join(selected_tags)}

KATI KURALLAR:
* HackerRank'e benzer sorular oluştur
* Soru parametreler almalı ve return ( yani geri dönüş değeri döndürmeli )
* Sorunun çözüm kodu ve test girdilerini ekle
* Parametre sayılarının tutarlı olmasına dikkat et
* Basit ve anlaşılır örnek girdi-çıktı ekle
* Çözüm kodu mümkün olduğunca sade olsun
* test_inputs alanında eğer ki çözüm kodunda kaç tane parametre varsa input sayısı da ona göre olmalı!
* test_inputs alanında sadece parametrelerin alacağı değerler olmalı çıktılar olmamalı!
* Yanıt kesinlikle JSON formatında olmalı öbür türlüsü kabul edilmiyor!!!

Ürettiğin soru aşağıdaki mevcut sorulardan TAMAMEN farklı olmalı:
{', '.join(existing_titles[:10])}

Yanıtını JSON formatında oluştur:

{{
  "title": "Kısa ve açıklayıcı soru başlığı",
  "description": "Markdown formatında soru açıklaması örnek girdiler ve çıktılarla destekle",
  "function_name": "python_fonksiyon_adi",
  "difficulty": {difficulty_level},
  "points": {10 + difficulty_level * 5},
  "example_input": "Örnek girdi",
  "example_output": "Örnek çıktı",
  "test_inputs": [[1, 2], [3, 4]] (2 parametreli fonksiyon için örnek) sadece parametrelerin alacağı değerler olmalı çıktılar bu kısımda olmamalı!,
  "solution_code": "def python_fonksiyon_adi(param1, param2):\\n    return sonuc"
}}"""

        # AI client oluştur ve soru iste
        client = AIClient(api_provider, api_key, model_name)
        response = client.chat_completion([
            {"role": "system",
             "content": "Sen bir Python programlama eğitmenisin. Amacın öğrenciler için özgün, çözülebilir ve öğretici programlama soruları üretmek."},
            {"role": "user", "content": prompt}
        ])

        # Yanıt içeriğini text formatına çevir
        response_text = ""
        if isinstance(response, dict):
            if "content" in response:
                response_text = response["content"]
            else:
                response_text = json.dumps(response)
        else:
            response_text = str(response)

        json_data = None

        # Debug bilgilerini topla
        debug_info = {
            "raw_response": response_text[:1000] + "..." if len(response_text) > 1000 else response_text,
            "ayrıştırma_denemeleri": []
        }

        # Strateji 1: Doğrudan JSON ayrıştırma
        try:
            json_data = json.loads(response_text)
            debug_info["ayrıştırma_denemeleri"].append("Doğrudan JSON ayrıştırma başarılı")
        except Exception as e:
            debug_info["ayrıştırma_denemeleri"].append(f"Doğrudan JSON ayrıştırma hatası: {str(e)}")

        # Strateji 2: Regex ile JSON bloklarını ara
        if not json_data:
            json_matches = re.findall(r'({[\s\S]*?})(?=\s*$|```)', response_text)
            debug_info["json_matches_count"] = len(json_matches)

            for i, match in enumerate(json_matches):
                try:
                    match_data = json.loads(match)
                    json_data = match_data
                    debug_info["ayrıştırma_denemeleri"].append(f"Regex match {i + 1} başarılı")
                    break
                except:
                    debug_info["ayrıştırma_denemeleri"].append(f"Regex match {i + 1} başarısız")

        # Strateji 3: Kod blokları içinde ara
        if not json_data:
            code_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            debug_info["code_blocks_count"] = len(code_blocks)

            for i, block in enumerate(code_blocks):
                try:
                    block_data = json.loads(block)
                    json_data = block_data
                    debug_info["ayrıştırma_denemeleri"].append(f"Kod bloğu {i + 1} başarılı")
                    break
                except:
                    debug_info["ayrıştırma_denemeleri"].append(f"Kod bloğu {i + 1} başarısız")

        # Eğer JSON ayrıştırılabildiyse verileri güncelle
        if json_data:
            # Zorluk seviyesi ve puan
            if "difficulty" in json_data:
                data["difficulty"] = int(json_data["difficulty"])
            if "points" in json_data:
                data["points"] = int(json_data["points"])

            # Temel alan kontrolü
            for field in ["title", "description", "function_name", "solution_code"]:
                if field in json_data and json_data[field]:
                    data[field] = json_data[field]

            # Örnek girdi ve çıktılar
            if "example_input" in json_data and json_data["example_input"]:
                data["example_input"] = json_data["example_input"]
            if "example_output" in json_data and json_data["example_output"]:
                data["example_output"] = json_data["example_output"]

            # Test girdileri
            if "test_inputs" in json_data:
                if isinstance(json_data["test_inputs"], list):
                    data["test_inputs"] = json.dumps(json_data["test_inputs"])
                else:
                    data["test_inputs"] = json_data["test_inputs"]
        else:
            # JSON ayrıştırılamadıysa hata döndür
            data["error"] = "JSON ayrıştırma hatası: AI yanıtı beklenen formatta değil"
            data["debug_info"] = debug_info
            return data

        # Sonuç kontrolü - temel alanlar var mı?
        required_fields = ["title", "description", "function_name", "solution_code"]
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            data["error"] = f"Eksik alanlar: {', '.join(missing_fields)}"

        return data

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()

        return {
            "error": f"Soru üretme hatası: {str(e)}",
            "debug_info": {
                "traceback": error_details,
                "response_text": response_text[:1000] + "..." if 'response_text' in locals() and len(
                    response_text) > 1000 else response_text if 'response_text' in locals() else "Yanıt alınamadı"
            },
            "title": "",
            "description": "",
            "function_name": "",
            "difficulty": difficulty_level,
            "points": 10 + difficulty_level * 5,
            "example_input": "Örnek girdi yok",
            "example_output": "Örnek çıktı yok",
            "test_inputs": "[]",
            "solution_code": ""
        }
