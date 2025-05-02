from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import platform
import psutil
import flask
import os
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


class Question(BaseModel):
    id: int
    title: str
    user: str
    date: str
    status: str


@api.get("/api/recent-questions", response_model=List[Question])
def recent_questions(admin: dict = Depends(get_current_admin)):
    # Örnek veri
    sample_questions = [
        {
            "id": 1,
            "title": "Python döngüleri nasıl kullanılır?",
            "user": "student1",
            "date": "02.04.2025",
            "status": "answered"
        },
        {
            "id": 2,
            "title": "Flask Blueprint nedir?",
            "user": "student3",
            "date": "01.04.2025",
            "status": "pending"
        },
        {
            "id": 3,
            "title": "React ile Flask nasıl entegre edilir?",
            "user": "student2",
            "date": "31.03.2025",
            "status": "answered"
        },
        {
            "id": 4,
            "title": "SQLAlchemy ilişkiler nasıl kurulur?",
            "user": "student4",
            "date": "30.03.2025",
            "status": "pending"
        }
    ]

    return sample_questions

# api.py dosyasına eklenecek importlar
import json
import time
import traceback
from contextlib import redirect_stdout
import io

class EvaluationRequest(BaseModel):
    code: str
    function_name: str
    test_inputs: str
    solution_code: str

class EvaluationResult(BaseModel):
    is_correct: bool
    execution_time: float
    errors: List[str]

def check_indentation(code: str):
    """Kod içindeki girinti hatalarını kontrol eder"""
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if line.strip() and line.startswith(" ") and "\t" in line:
            return False, i + 1
    return True, 0

@api.post("/api/evaluate", response_model=EvaluationResult)
def evaluate_solution(request: EvaluationRequest):
    """Kullanıcı kodunu değerlendirir ve sonuçları döndürür"""
    result = {
        "is_correct": False,
        "execution_time": 0,
        "errors": []
    }

    # Girinti kontrolü
    is_valid, line_num = check_indentation(request.code)
    if not is_valid:
        result["errors"].append(f"Girinti hatası: Satır {line_num}'de karışık tab ve boşluk kullanımı tespit edildi.")
        return result

    try:
        test_inputs = json.loads(request.test_inputs)
    except json.JSONDecodeError:
        result["errors"].append("Test girdileri geçerli JSON formatında değil")
        return result

    try:
        # Kullanıcı kodunu çalıştır
        user_namespace = {}
        exec(request.code, user_namespace)
        user_function = user_namespace.get(request.function_name)

        if not user_function:
            result["errors"].append(f"'{request.function_name}' adında bir fonksiyon bulamadık")
            return result

        # Admin çözümünü çalıştır
        admin_namespace = {}
        exec(request.solution_code, admin_namespace)
        admin_function = admin_namespace.get(request.function_name)

        # Testleri çalıştır
        start_time = time.time()

        for test_input in test_inputs:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                user_result = user_function(*test_input)

            admin_result = admin_function(*test_input)

            if user_result != admin_result:
                result["errors"].append(
                    f"Test başarısız: Girdi: {test_input}, Beklenen: {admin_result}, Çıktı: {user_result}")

        end_time = time.time()
        result["execution_time"] = (end_time - start_time) * 1000  # milisaniye

        if not result["errors"]:
            result["is_correct"] = True

    except Exception as e:
        result["errors"].append(f"Hata: {str(e)}")
        result["errors"].append(traceback.format_exc())

    return result


from typing import Optional, List
from datetime import datetime
import nbformat
import os
import time
import hashlib
import re
import requests
from fastapi import HTTPException
from pydantic import BaseModel


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
def get_notebook_summary(request: NotebookSummaryRequest, db=Depends(get_db)):
    """Notebook için özet oluşturur veya var olan özeti döndürür"""
    try:
        # Veritabanında özet var mı kontrol et
        summary_query = text("""
            SELECT notebook_path, summary, code_explanation, last_updated
            FROM notebook_summary
            WHERE notebook_path = :path
        """)

        existing = db.execute(summary_query, {"path": request.notebook_path}).first()

        if existing and existing.summary:
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

        summary_response = client.chat_completion(
            messages=[
                system_message,
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=max_tokens
        )

        # Özeti al
        summary_text = summary_response.get("content", "") if "error" not in summary_response else ""

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
                code_explanation_combined = "# Kod Hücrelerinin Analizi\n\n" + "\n\n".join(code_explanations)

            if "error" not in techniques_response:
                techniques_text = techniques_response.get("content", "")
                if techniques_text:
                    code_explanation_combined += "\n\n# Teknik Analiz\n\n" + techniques_text
        except Exception as e:
            code_explanation_combined = f"Kod açıklaması oluşturulurken hata oluştu: {str(e)}"

        # Veritabanına kaydet
        last_updated = datetime.utcnow()

        if existing:
            update_query = text("""
                UPDATE notebook_summary
                SET summary = :summary, code_explanation = :code_explanation, last_updated = :last_updated
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
        return {
            "summary": "",
            "code_explanation": "",
            "last_updated": datetime.utcnow().isoformat(),
            "error": str(e)
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