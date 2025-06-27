from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

import os
import json
import time
import re
import shutil
import flask
import hashlib
import traceback
import platform
import psutil
import nbformat
import ast
import codecs

from datetime import datetime, timedelta

import requests
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.events import event_manager
from app.events.event_definitions import EventType
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# BaseModeller

class ServerStatus(BaseModel):
    """ServerStatus sınıfı, sunucunun durum bilgilerini depolamak ve yönetmek
    amacıyla tasarlanmıştır.

    Bu sınıf, belirli bir sunucunun Python, Flask ve MySQL gibi yazılım
    sürümleri ile ilgili bilgilerini, RAM kullanımı, CPU kullanımı ve süreçlerin
    RAM tüketimini takip etmek amacıyla kullanılır. Sunucunun güncel durumu
    hakkında bilgi sağlamak için yapılandırılmıştır.

    Attributes:
        python_version (str): Kullanılan Python sürümünü belirtir.
        flask_version (str): Kullanılan Flask sürümünü belirtir.
        mysql_version (str): Kullanılan MySQL sürümünü belirtir.
        ram_used (float): Kullanılan RAM miktarını belirtir (GB cinsinden).
        ram_total (float): Toplam RAM kapasitesini belirtir (GB cinsinden).
        cpu_usage (float): CPU kullanım yüzdesini belirtir.
        process_ram_used (float): Süreç tarafından kullanılan RAM miktarını belirtir
        (GB cinsinden).
        process_ram_allocated (float): Süreç tarafından tahsis edilen RAM miktarını
        belirtir (GB cinsinden).
    """
    python_version: str
    flask_version: str
    mysql_version: str
    ram_used: float
    ram_total: float
    cpu_usage: float
    process_ram_used: float
    process_ram_allocated: float

# User model - sadece API amaçlı
class UserRole(BaseModel):
    """
    UserRole sınıfı, bir kullanıcı rolünü temsil eder.

    Bu sınıf, kullanıcıların bağlı oldukları rollerin kimliğini ve adını saklamak
    için bir model sunar. Özellikle, kullanıcı rolü ile ilgili işlem ve sorgulamalar
    için temel bir veri yapısı olarak kullanılır.

    Attributes:
        id (int): Kullanıcı rolüne atanmış tekil kimlik numarasıdır.
        name (str): Kullanıcı rolünün adını tutar.
    """
    id: int
    name: str

class UserData(BaseModel):
    """
    Kullanıcı verilerini temsil eden bir model sınıfı.

    Bu sınıf bir kullanıcının bilgilerinin saklanması ve işlenmesi için kullanılır. Kullanıcı
    kendine ait bir kimlik numarası, kullanıcı adı, e-posta adresi, kayıt tarihi
    ve rol listesi gibi bilgileri içerir. Bu model kullanıcılarla ilgili operasyonlarda
    merkezi bir veri taşıma nesnesi olarak kullanılabilir.
    """
    id: int
    username: str
    email: str
    registered: str
    roles: List[str]

class EvaluationRequest(BaseModel):
    """
    EvaluationRequest sınıfı, kullanıcı kodunun belirli bir işlev için test edilmesi
    için gerekli olan verileri temsil eder.

    Bu sınıf, bir fonksiyonun adı, kodu, test girdileri ve çözüm kodu gibi bilgileri
    depolamak ve değerlendirme süreçlerinde kullanılmak üzere yapılandırılmıştır.
    Kullanıcı kodunu test etmek ve doğrulamak için gerekli olan tüm bilgileri içerir.
    """
    code: str
    function_name: str
    test_inputs: str
    solution_code: str

class EvaluationResult(BaseModel):
    """
    EvaluationResult, yapılan bir değerlendirmenin sonuçlarını tutmak
    için kullanılan bir veri modelini temsil eder.

    Bu sınıf, bir değerlendirme işleminde toplanan verilerin detaylarını
    ve sonuçlarını saklamak amacıyla kullanılır. Test sonuçları, geçen
    ve kalan testlerin sayısı, hata detayları ve genel doğruluk durumu gibi
    bilgiler içerir. Bu model, değerlendirme sonuçlarının yapılandırılmış
    bir formatta sunulması için tasarlanmıştır.
    """
    is_correct: bool
    execution_time: float
    errors: List[str]
    test_count: int
    passed_tests: int
    failed_tests: int
    test_results: Optional[dict] = None

# --- AI Notebook Summary Modelleri ---
class NotebookSummaryRequest(BaseModel):
    """
    NotebookSummaryRequest sınıfı bir deftere ait özet bilgilerini tutmak
    ve işlemler sırasında kullanılabilmek amacıyla oluşturulmuştur.

    Bu sınıf, bir deftere ait yolu tanımlamak için kullanılan bir veri modelini
    temsil eder. Model, doğrulama ve yapılandırma işlemlerinde yardımcı olması
    için BaseModel'den türetilmiştir.
    """
    notebook_path: str


class NotebookSummaryResponse(BaseModel):
    """
    NotebookSummaryResponse sınıfı, bir not defterinin özet içeriğini, kod açıklamasını,
    son güncelleme tarihini ve isteğe bağlı olarak bir hata mesajını temsil eder.

    Bu sınıf, not defteri içeriğinin hızlı bir şekilde özetlenmesini ve açıklanmasını sağlamak
    için kullanılır. Ayrıca, güncel olmayan veya hata içeren içerikleri takip edebilmek için
    isteğe bağlı bir hata mesajı alanı içerir. Veriler Pydantic tabanlı, güçlü tip kontrolü
    ile modelleme yapılmıştır.

    Attributes:
        summary (str): Not defteri özetini açıklayan metin.
        code_explanation (str): Kodun işleyişini veya amacını açıklayan metin.
        last_updated (str): Not defterinin en son güncellenme tarihi.
        error (Optional[str]): (Varsayılan: Yok) Mevcutsa hata mesajını içeren metin.
    """
    summary: str
    code_explanation: str
    last_updated: str
    error: Optional[str] = None

class DetailedQuestion(BaseModel):
    """
    Bir soruyu temsil eden sınıf.

    DetailedQuestion sınıfı, bir soru ile ilgili ayrıntılı bilgileri
    tutmak amacıyla kullanılır. Sorunun kimlik bilgisi, başlık, açıklama,
    zorluk seviyesi, puanı ve oluşturulma ile güncellenme zamanlarını
    saklar. Bu sınıf BaseModel sınıfından türetilmiştir.
    """
    id: int
    title: str
    description: str
    difficulty: int
    points: int
    updated_at: str
    created_at: str

class LeaderboardEntry(BaseModel):
    """
    LeaderboardEntry, kullanıcıların sıralamalarını, puanlarını ve kullanıcı adlarını
    temsili bir model olarak tutar.

    Bu sınıf, belirli bir liderlik tablosunda bir kullanıcı sıralaması ile ilgili bilgileri
    erişmek ve temsil etmek için kullanılır. Kullanıcı adına, sıralamasına ve kazandığı
    puanlara dair verileri depolar.
    """
    username: str
    points: int
    rank: int

class LeaderboardResponse(BaseModel):
    """
    LeaderboardResponse sınıfı, liderlik tablosu verilerini temsil eder ve
    ilgili özellikleri içerir.

    Bu sınıf, kullanıcıların liderlik tablosundaki verileri depolamak için
    kullanılır. Kullanıcı bilgilerini, toplam kullanıcı sayısını ve bir
    sayfada gösterilen maksimum kullanıcı sayısını tutar.

    Attributes:
        users (List[LeaderboardEntry]): Liderlik tablosunda yer alan kullanıcı
        girişlerini tutan bir liste.

        total (int): Liderlik tablosundaki toplam kullanıcı sayısı.

        limit (int): Liderlik tablosunda bir sayfada gösterilecek maksimum
        kullanıcı sayısı.
    """
    users: List[LeaderboardEntry]
    total: int
    limit: int

class SubmissionDetail(BaseModel):
    """
    SubmissionDetail sınıfı, bir kullanıcı gönderim detaylarını temsil eder.

    Bu sınıf, bir kullanıcının soru çözme aktiviteleri ve sonuçları ile ilgili verileri
    yönetmek için kullanılır. Bir gönderimin doğru olup olmadığı, hangi soruya ait olduğu
    ve ne zaman yapıldığı gibi bilgileri içerir.
    """
    id: int
    user_id: int
    username: str
    question_id: int
    question_title: str
    is_correct: bool
    execution_time: float
    created_at: str

class Badge(BaseModel):
    """
    Badge sınıfını temsil eder.

    Kullanıcıların sahip olabileceği rozeti tanımlayan bir sınıftır. Bu rozetler,
    belirli bir kimlik numarası, ad, simge ve açıklama bilgilerini içerir. Rozetler,
    sistemde kullanıcılara ait belirli bir başarıyı ya da özelliği göstermek için
    kullanılabilir.
    """
    id: int
    name: str
    icon: str
    description: str

class Activity(BaseModel):
    """
    Bir etkinliği temsil eder.

    Activity sınıfı, etkinliklerin bilgilerini saklamak için tasarlanmış
    bir veri modelidir. Bu sınıf, etkinlik kimliği, türü, içeriği ve tarih
    bilgilerini içerir. Etkinliklerin farklı özelliklerini ve içeriklerini
    yapılandırılmış bir şekilde saklamak için kullanılabilir.
    """
    id: int
    type: str
    content: dict
    date: str

class UserStats(BaseModel):
    """
    Kullanıcı istatistiklerini temsil eden sınıf.

    Bu sınıf, bir kullanıcının çözdüğü sorunların sayısını, kod yazdığı günlerin
    sayısını, aktif günlerin ardışık serisini ve çözülen sorunların yüzdesini
    içeren istatistiksel bilgileri depolamak için kullanılır.

    Attributes:
        solvedProblems (int): Kullanıcının çözdüğü toplam sorun sayısı.
        codingDays (int): Kullanıcının kod yazdığı toplam gün sayısı.
        activeDaysStreak (int): Kullanıcının ardışık aktif olduğu gün sayısı.
        solutedProblemsPercentage (float): Çözülen sorunların yüzdesi.
    """
    solvedProblems: int
    codingDays: int
    activeDaysStreak: int
    solutedProblemsPercentage: float

class UserProfileData(BaseModel):
    """
    Temel olarak bir kullanıcı profili verilerini temsil eder.

    UserProfileData sınıfı, bir kullanıcının profil bilgilerini ve buna ilişkin
    çeşitli verileri tutar. Bu sınıf, pyydantic'in BaseModel sınıfından türetilmiştir
    ve kullanıcı bilgileri, rozetler, aktiviteler gibi verilerin bir arada yönetilmesini
    sağlar. Kullanıcı hakkındaki istatistiksel bilgileri ve günlük aktiviteleri de
    barındırır.
    """
    username: str
    email: str
    joinDate: Optional[str]
    isCurrentUser: bool = False
    badges: List[Badge]
    stats: UserStats
    activities: List[Activity]
    dailyActivity: List[dict]

class GeneratedQuestionResponse(BaseModel):
    """
    GeneratedQuestionResponse sınıfı, bir sorunun özelliklerini temsil eden bir veri modelidir.

    Bu sınıf, bir programlama sorusunun çeşitli özelliklerini tutmak için kullanılır. Özellikle
    başlık, açıklama, ilgili işlev adı, zorluk derecesi, konu, puan ve örnek giriş/çıkış gibi
    özellikleri içerir. Ayrıca, çözüm kodu, test girdileri ve hata ile debug bilgilerini tutmak
    için de kullanılabilir. Bu sınıf, genellikle veri taşımak amacıyla kullanılır ve BaseModel
    türetilmiştir.

    Attributes:
        title (str): Sorunun başlığı. Varsayılan olarak boş bir dize.
        description (str): Sorunun açıklaması. Varsayılan olarak boş bir dize.
        function_name (str): Sorunun çözümüne ait işlevin adı. Varsayılan olarak boş bir dize.
        difficulty (int): Sorunun zorluk derecesi. Varsayılan olarak 1.
        topic (str): Sorunun ait olduğu konu. Varsayılan olarak boş bir dize.
        points (int): Sorudan kazanılabilecek puan. Varsayılan olarak 10.
        example_input (str): Örnek giriş verisi. Varsayılan olarak "Örnek girdi yok".
        example_output (str): Örnek çıktı verisi. Varsayılan olarak "Örnek çıktı yok".
        test_inputs (str): Sorunun test edilmesi için kullanılacak giriş verileri. Varsayılan olarak "[]".
        solution_code (str): Sorunun ilgili çözüm kodu. Varsayılan olarak boş bir dize.
        error (Optional[str]): Çözümden kaynaklanabilecek hata mesajı. Varsayılan olarak None.
        debug_info (Optional[str]): Debugging sürecinde kullanılabilecek ek bilgiler. Varsayılan olarak None.
    """
    title: str = ""
    description: str = ""
    function_name: str = ""
    difficulty: int = 1
    topic: str = ""
    points: int = 10
    example_input: str = "Örnek girdi yok"
    example_output: str = "Örnek çıktı yok"
    test_inputs: str = "[]"
    solution_code: str = ""
    error: Optional[str] = None
    debug_info: Optional[str] = None

class QuestionGenerationRequest(BaseModel):
    """
    Soru oluşturma isteğini temsil eden bir sınıf.

    Bu sınıf, belirli bir konuda ve belirli bir zorluk seviyesinde soru oluşturma
    isteğini tanımlar. Kullanıcının sağladığı açıklamalar veya öneriler,
    soru oluşturma sürecini daha verimli hale getirmek için kullanılabilir.
    """
    difficulty_level: int = 1
    topic: str = "genel"
    description_hint: str = ""  # Kullanıcının açıkladığı soru ipucu
    function_name_hint: str = ""  # Fonksiyon adı önerisi (opsiyonel)
    tags: list = []

class EventRequest(BaseModel):
    event_type: str
    data: Dict[str, Any]

class ProgrammingQuestionCreate(BaseModel):
    """
    Programlama sorusu oluşturma isteğini temsil eden bir sınıf.

    Bu sınıf, programlama sorularının oluşturulması için gerekli olan
    başlık, açıklama, zorluk seviyesi, puan, konu, örnek giriş/çıktı ve
    çözüm kodu gibi bilgileri içerir.
    """
    id: Optional[int] = None
    title: str
    description: str
    difficulty: int = 1
    points: int = 10
    topic: str = "genel"
    example_input: str = ""
    example_output: str = ""
    function_name: str = ""
    solution_code: str = ""
    test_inputs: str = "[]"

# Instagram post yanıt modelini tanımlayalım
class InstagramPostResponse(BaseModel):
    """Bir Instagram gönderisini temsil eden yanıt model sınıfı.

    Bu sınıf, bir Instagram gönderisinin bilgilerini depolamak ve
    işlemek için kullanılır. İçerdiği nitelikler, bir gönderinin
    temel bilgilerini kapsar ve bu model, genellikle bir API'den
    alınan verilere karşılık gelir.

    Attributes:
        id (int): Gönderinin benzersiz kimliği.
        image_url (str): Gönderiye ait görselin URL adresi.
        caption (str): Gönderi açıklaması.
        likes (int): Gönderiye verilen beğeni sayısı.
        post_date (str): Gönderinin paylaşıldığı tarih.
        post_url (str): Gönderinin URL adresi.
    """
    id: int
    image_url: str
    caption: str
    likes: int
    post_date: str
    post_url: str


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

# Veritabanı oturumu dependency
def get_db():
    """
    Bu fonksiyon, bir veritabanı oturumu oluşturup bu oturumu sağlayarak işlem
    tamamlandığında oturumu düzgün bir şekilde kapatmayı garanti eder. Veritabanı
    oturumlarının güvenli bir şekilde oluşturulmasını ve sonunda serbest
    bırakılmasını sağlar. Bu yöntem, veritabanı işlemleri sırasında kaynak
    yönetimini optimize eder.

    Yields:
        sqlalchemy.orm.Session: Oluşturulmuş veritabanı oturumu.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Admin yetkilendirme (basit)
def get_current_admin():
    """
    Fonksiyonun özeti:
    Bu fonksiyon, varsayılan olarak bir yöneticinin kimliğinin elde edilmesinde kullanılır.
    Gerçek bir uygulamada, bu işlem genellikle bir JWT tokeni ya da farklı bir
    yetkilendirme mekanizması aracılığıyla yapılmalıdır. Burada yalnızca örnek bir
    sözlük döndürülmektedir.

    Returns:
        dict: Kullanıcının yönetici olup olmadığını belirten bir sözlük.
    """
    # Gerçek bir uygulamada JWT token vb. ile yetkilendirme yapılmalı
    return {"is_admin": True}


@api.get("/api/server-status", response_model=ServerStatus)
def server_status(admin: dict = Depends(get_current_admin), db=Depends(get_db)):
    """
    Hizmetin sağlıklı çalışırlığını göstermek için sunucu durum bilgilerini döndüren bir API fonksiyonu.
    Bu yöntem, sistemin güncel durumunu ve performansını değerlendirmek için kullanılır.

    Args:
        admin (dict, optional): Geçerli yöneticiyi döndüren bir bağımlılık.
        db: Veritabanı bağlantısını sağlayan bağımlılık.

    Returns:
        dict: Sunucu ve süreç bilgilerini içeren bir sözlük. Dönen anahtarlar şunlardır:
            - python_version (str): Python'un mevcut sürümü.
            - flask_version (str): Flask framework'ünün sürümü.
            - mysql_version (str): MySQL veritabanının mevcut sürümü.
            - ram_used (float): Toplam sistemde kullanılan RAM miktarı (GB cinsinden).
            - ram_total (float): Sistemdeki toplam RAM miktarı (GB cinsinden).
            - cpu_usage (float): Yüzdesel olarak sistem CPU kullanım oranı.
            - process_ram_used (float): Çalışmakta olan sürecin kullandığı RAM miktarı (GB cinsinden).
            - process_ram_allocated (float): Çalışmakta olan sürecin tahsis edilen RAM miktarı (GB cinsinden).
    """
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

def check_indentation(code: str):
    """Kod içindeki girinti hatalarını ve sözdizimi hatalarını kontrol eder"""
    lines = code.splitlines()

    # Tab ve boşluk karışımını kontrol et
    for i, line in enumerate(lines):
        if line.strip() and line.startswith(" ") and "\t" in line:
            return False, i + 1, "Bu satırda hem tab hem de boşluk karakteri var, bu tutarsız girintiye neden olur", "indentation"

    # Girinti tutarlılığını ve sözdizimi hatalarını kontrol et
    try:
        # Gerçek Python derleyicisiyle girinti ve sözdizimi hatalarını tespit et
        compile(code, "<string>", "exec")
        return True, None, None, None
    except IndentationError as e:
        # IndentationError, satır numarasını ve hata mesajını içerir
        return False, e.lineno, str(e), "indentation"
    except SyntaxError as e:
        # SyntaxError hatalarını da yakala
        return False, e.lineno, str(e), "syntax"
    except Exception as e:
        # Diğer hatalar için
        return False, None, str(e), "other"

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
    """
    Kullanıcı kodunu değerlendirir ve sonuçları döndürür.

    Bu API endpoint'i kullanıcının gönderdiği kodu çalıştırır, çözüm ile karşılaştırır
    ve test sonuçlarını döndürür.
    """
    # Sonuç nesnesi başlangıç değerleri
    result = {
        "is_correct": False,
        "execution_time": 0,
        "test_count": 0,
        "test_results": {},
        "errors": [],
        "passed_tests": 0,  # Zorunlu alan
        "failed_tests": 0  # Zorunlu alan
    }

    try:
        # 1. Kod ön işleme ve kontrol
        normalized_code = normalize_indentation(request.code)

        # Geliştirilmiş girinti kontrolü
        is_valid, line_num, error_msg, error_type = check_indentation(normalized_code)
        if not is_valid:
            if error_type == "syntax":
                result["errors"].append(f"Satır {line_num}'de sözdizimi hatası: {error_msg}")
            elif error_type == "indentation":
                result["errors"].append(f"Satır {line_num}'de girinti hatası: {error_msg}")
            else:
                result["errors"].append(f"Kodda hata: {error_msg}")
            return result

        # 2. Random kullanım kontrolü ve seed enjeksiyonu
        normalized_code = inject_random_seed(normalized_code, request.function_name)
        modified_solution_code = inject_random_seed(request.solution_code, request.function_name)

        # 3. Test girdilerini yükle
        try:
            test_inputs = json.loads(request.test_inputs)
            result["test_count"] = len(test_inputs)
        except json.JSONDecodeError:
            result["errors"].append("Test girdileri geçerli JSON formatında değil")
            return result

        # 4. Kullanıcı fonksiyonunu çalıştırma
        user_namespace = {}
        exec(normalized_code, user_namespace)
        user_function = user_namespace.get(request.function_name)

        if user_function is None:
            result["errors"].append(f"'{request.function_name}' adında bir fonksiyon bulunamadı")
            return result

        if not callable(user_function):
            result["errors"].append(f"'{request.function_name}' çağrılabilir bir fonksiyon değil")
            return result

        # 5. Çözüm fonksiyonunu çalıştırma
        solution_namespace = {}
        exec(modified_solution_code, solution_namespace)
        solution_function = solution_namespace.get(request.function_name)

        if not solution_function:
            result["errors"].append("Çözüm fonksiyonu bulunamadı")
            return result

        # 6. Testleri çalıştır ve değerlendir
        start_time = time.time()
        test_results, passed, failed, is_all_correct, error_messages = run_tests(
            user_function, solution_function, test_inputs
        )
        end_time = time.time()

        # 7. Sonuçları hazırla
        result["is_correct"] = is_all_correct
        result["execution_time"] = round((end_time - start_time) * 1000, 2)  # milisaniye
        result["test_results"] = test_results
        result["passed_tests"] = passed
        result["failed_tests"] = failed
        result["errors"].extend(error_messages)

        return result

    except Exception as e:
        # Genel hata durumu
        import traceback
        error_trace = traceback.format_exc()
        result["errors"].append(f"Değerlendirme hatası: {str(e)}")
        result["error_details"] = error_trace
        return result


def inject_random_seed(code, function_name):
    """Random modülü kullanıldığında seed ekler"""
    if not code:
        return code

    # Random kullanım kontrolü
    uses_random = re.search(r'import\s+random|from\s+random\s+import', code) is not None

    if uses_random:
        # Fonksiyon tanımını bul
        function_pattern = re.compile(f"def\\s+{re.escape(function_name)}\\s*\\([^)]*\\)\\s*:")
        match = function_pattern.search(code)
        if match:
            insertion_point = match.end()
            # Fonksiyonun ilk satırına seed enjekte et
            code = code[:insertion_point] + "\n    random.seed(67)" + code[insertion_point:]

    return code


def run_tests(user_function, solution_function, test_inputs):
    """Test girişlerine göre fonksiyonu çalıştırır ve sonuçları değerlendirir"""
    all_correct = True
    passed_tests = 0
    failed_tests = 0
    test_results = {}
    error_messages = []

    for i, test_input in enumerate(test_inputs):
        # Test girişlerinin liste olduğundan emin ol
        if not isinstance(test_input, list):
            test_input = [test_input]

        test_key = f"test_{i + 1}"
        test_results[test_key] = {"input": test_input, "passed": False}

        try:
            # Her iki fonksiyonu da aynı girdilerle çalıştır
            user_result = user_function(*test_input)
            expected_result = solution_function(*test_input)

            # Sonuçları karşılaştır
            if user_result != expected_result:
                all_correct = False
                failed_tests += 1
                test_results[test_key]["passed"] = False
                test_results[test_key]["expected"] = expected_result
                test_results[test_key]["actual"] = user_result
                error_messages.append(
                    f"Test başarısız: Girdi: {test_input}, Beklenen: {expected_result}, Alınan: {user_result}")
            else:
                passed_tests += 1
                test_results[test_key]["passed"] = True

        except TypeError as e:
            error_msg = str(e)
            failed_tests += 1
            test_results[test_key]["passed"] = False
            test_results[test_key]["error"] = error_msg

            if "'builtin_function_or_method' object is not subscriptable" in error_msg:
                # Hata konumunu bul
                import traceback
                tb = traceback.extract_tb(e.__traceback__)
                line_number = None

                for frame in tb:
                    if frame.filename == "<string>":
                        line_number = frame.lineno
                        break

                line_info = f"Satır {line_number}: " if line_number else ""
                error_messages.append(
                    f"{line_info}Yerleşik fonksiyon/metot indeks notasyonu ile kullanılamaz. "
                    "Örnek: 'max[0]' yerine 'max(liste)' kullanmalısınız."
                )
            else:
                error_messages.append(f"Tip hatası: {error_msg}")
            all_correct = False

        except Exception as e:
            failed_tests += 1
            test_results[test_key]["passed"] = False
            test_results[test_key]["error"] = str(e)
            error_messages.append(f"Çalışma zamanı hatası: {str(e)}")
            all_correct = False

    return test_results, passed_tests, failed_tests, all_correct, error_messages


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
        model_name = settings.get('ai_default_model', 'gemini-2.0-flash-lite')
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

@api.get("/api/last-submissions", response_model=List[SubmissionDetail])
def get_last_submissions(limit: Optional[int] = 10, db=Depends(get_db)):
    """
    API'ye yapılan son gönderimlerin bir listesini döndürür. Gönderimler, kullanıcı bilgileri,
    soru başlığı ve diğer detaylarla birlikte en son tarihe göre sıralanmıştır ve belirtilen
    limit kadar alınır. SQL sorgusu doğrudan veritabanında yürütülür ve veriler yapısal bir
    liste olarak geri döndürülür.

    Args:
        limit (Optional[int], default=10): Döndürülmesi istenen en fazla gönderim sayısını belirler.
        db: Veritabanı bağlantısı için bağımlılık fonksiyonu.

    Returns:
        List[Dict]: Her biri gönderim bilgilerini içeren sözlüklerden oluşan bir liste.

    Raises:
        HTTPException: Sunucu kaynaklı bir hata meydana geldiğinde, ayrıntılı hata mesajıyla birlikte
        500 durumu döner.
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
    """
    Fonksiyona dair detaylı açıklama ve işlev hakkında bilgi sağlar. Bu fonksiyon, belirli bir tarih aralığında yapılan kullanıcı
    kayıtlarının günlük dağılımını veritabanından sorgular ve formatlanmış bir biçimde geri döner.

    Args:
        days (Optional[int]): Son X günü belirtir. Varsayılan değer 30'dur.
        db: Veritabanı bağlantısı için gerekli bağımlılık (Depends(get_db)).

    Return:
        list[dict]:
            Her bir tarih için kayıtlı kullanıcı sayısını içeren bir liste döner. Liste,
            {"date": "yyyy-mm-dd", "count": int} yapısında sözlüklerden oluşur.

    Raises:
        HTTPException: Bir hatayla karşılaşıldığında, hata kodu 500 ve hata detayı fırlatılır.
    """
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
    """
    Handle API endpoint to fetch solved questions chart data.

    This endpoint retrieves the count of correctly solved questions grouped
    by date for the specified number of recent days. If no number of days is
    provided, the default value of 30 days is used. The data is fetched from the
    database and returned as a list of dictionaries where each dictionary contains
    a date and the corresponding count.

    Parameters:
        days (Optional[int]): The number of recent days to include in the query.
                             Defaults to 30 days if not specified. Must be a
                             positive integer.
        db: The database connection dependency injected via FastAPI's Dependency
            Injection mechanism.

    Returns:
        list[dict]: A list of dictionaries where each dictionary contains a 'date'
                    as a string formatted as YYYY-MM-DD and a 'count' as an integer
                    representing the number of solved questions for that date.

    Raises:
        HTTPException: Raised when there is any error while executing the database
                       query or processing the results.
    """
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
    """
    Bu fonksiyon, belirli bir zaman dilimi için kullanıcı aktivitesine ait istatistiksel bilgileri
    sorgular ve döner. Yeni kullanıcı sayısı, toplam çözüm sayısı, doğru çözüm sayısı ve aktif
    kullanıcı sayısını içerir.

    Parameters:
        days (Optional[int]): İstatistiklerin hesaplanacağı gün sayısı. Varsayılan değer 30'dur.
        db: Veritabanı oturumu, get_db bağımlılığı ile elde edilir.

    Returns:
        dict: İstatistik verilerini içeren bir sözlük döner. Dönen sözlük:
            - "new_users" (int): Belirtilen süre içinde kaydolmuş yeni kullanıcıların sayısı
            - "total_submissions" (int): Belirtilen süre içinde yapılan toplam çözüm sayısı
            - "correct_submissions" (int): Belirtilen süre içinde doğru çözülen soru sayısı
            - "active_users" (int): Belirtilen süre içinde aktif olarak işlem yapmış kullanıcı sayısı

    Raises:
        HTTPException: Bir hata oluştuğunda 500 durum koduyla hata mesajı döner.
    """
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

@api.get("/api/user-profile/{username}", response_model=UserProfileData)
def get_user_profile(username: str, current_user_id: Optional[int] = "0", db=Depends(get_db)):
    """
    get_user_profile fonksiyonu, kullanıcı adına göre kullanıcı bilgilerini, istatistiklerini,
    rozetlerini ve aktivitelerini döndüren bir API endpoint'idir. Bunun yanı sıra, son 7 günlük
    aktivite verilerini gün bazında kullanıcıya detaylı bir şekilde sunar ve mevcut oturumdaki
    kullanıcı ile sorgulanan profilin eşleşip eşleşmediğini kontrol eder.

    Arguments:
        username (str): Sorgulanan kullanıcı adı.
        current_user_id (Optional[int]): Oturum açmış kullanıcının kimlik bilgisi.
                                          Varsayılan olarak "0" değeri kullanılır.
        db: Veritabanı bağlantısını sağlayan bağımlılık.

    Return:
        dict: Kullanıcı profili, istatistikler, aktiviteler, rozetler ve günlük aktiviteleri
              içeren bir sözlük.

    Raises:
        HTTPException: Eğer kullanıcı bulunamazsa veya herhangi bir dahili sunucu hatası
                       oluşursa bu hata fırlatılır.
    """
    try:
        # Eğer current_user_id null olarak gelirse None olarak ayarla
        if current_user_id is None:
            current_user_id = None
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

        # Kullanıcı rozetlerini al
        badges_query = text("""
                            SELECT b.id, b.name, b.icon, b.description
                            FROM badges b
                                     JOIN user_badges ub ON b.id = ub.badge_id
                            WHERE ub.user_id = :user_id
                            ORDER BY ub.awarded_at DESC
                            """)

        badges_result = db.execute(badges_query, {"user_id": user.id})

        badges = []
        for badge in badges_result:
            badges.append({
                "id": badge.id,
                "name": badge.name,
                "icon": badge.icon,
                "description": badge.description
            })

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
            "isCurrentUser": current_user_id == user.id if current_user_id else False,
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

@api.post("/api/generate-question", response_model=GeneratedQuestionResponse)
def generate_programming_question(request: QuestionGenerationRequest, db=Depends(get_db)):
    """
    Bir Python FastAPI endpointi olarak, bu fonksiyon gelen istek üzerine yapay zeka yardımıyla yeni bir
    programlama sorusu üretmek görevini üstlenir. Fonksiyon, kullanıcının verdiği talimatlar ve zorluk
    seviyesine göre bir soru hazırlar ve bu soruda gereken veri gibi çeşitli bileşenleri ayarlar.

    Attributes:
        @api.post("/api/generate-question"): Bu fonksiyonun bir REST API endpointi olarak tanımlandığını ve
        POST metodunu kullandığını belirtir.
        response_model (GeneratedQuestionResponse): Yanıt modelinin türü. Üretilecek sonucun bu modele uygun
        olması beklenir.

    Args:
        request (QuestionGenerationRequest): API çağrısı sırasında gelen ve kullanılacak veri. Bu model,
        soru oluşturma isteğini tanımlar ve kullanıcıdan gelen bilgileri içerir.
        db: Veritabanı bağlantısı (SQLAlchemy Depends tipi). Sistemde yapılan sorgular için kullanılır.

    Returns:
        dict: Üretilen programlama sorusunu temsil eden (veya hata durumunda hata mesajını içeren) bir JSON nesnesi döner.

    Raises:
        Bu metod herhangi bir özel tipte hata fırlatmaz. Ancak yapay zeka API'sine yapılan gönderim sırasında bir hata
        yaşanırsa JSON ayrıştırma hataları oluşabilir ya da veritabanı bağlantı sorunları doğabilir.

    Functions:
        Bu endpoint, talep edilen parametrelere uygun bir programlama sorusu üretmek için aşağıdaki başlıca adımları izler:
        1. Varsayılan soru alanlarının doldurulması.
        2. Veritabanından ayar bilgileri alınması ve AI API sağlayıcısının başlatılması.
        3. Kullanıcının belirttiği zorluk seviyesi ve konuya göre bir yapay zeka istemcisi oluşturulması.
        4. Belirli kriterlere uygun bir prompt oluşturulması.
        5. Yapay zeka istemcisinden gelen yanıtın JSON formatında işlenmesi.
        6. Uygun formatta bir soru döndürülmesi veya hata mesajı sağlanması.
    """
    try:
        # Varsayılan sonuç şablonunu başlangıçta oluştur
        data = {
            "title": "",
            "description": "",
            "function_name": "",
            "difficulty": request.difficulty_level,
            "topic": request.topic,
            "points": 10 + request.difficulty_level * 5,
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
        model_name = settings.get('ai_default_model', 'gemini-2.0-flash-lite')
        enabled = settings.get('ai_enable_features', 'true').lower() == 'true'

        if not enabled:
            return {"error": "Yapay zeka özellikleri şu anda devre dışı.", **data}

        # Zorluk seviyesi açıklamaları
        difficulty_desc = {
            1: "Kolay",
            2: "Orta",
            3: "Zor",
            4: "Çok Zor"
        }

        # Mevcut soru başlıklarını al
        existing_titles_query = text("SELECT title FROM programming_question")
        existing_titles = [row.title for row in db.execute(existing_titles_query)]

        # Konu kontrolü - eğer boş veya "genel" ise rastgele konu seç
        topic = request.topic
        import random
        if not topic or topic == "genel":
            topics = ["veri yapıları", "algoritmalar", "string işleme", "matematik",
                      "sayı teorisi", "arama", "sıralama", "dinamik programlama",
                      "graf teorisi", "olasılık", "istatistik"]
            topic = random.choice(topics)
            data["topic"] = topic

        # Etiketler kontrolü
        selected_tags = request.tags
        if not selected_tags:
            selected_tags = random.sample(["python", "algoritma", "programlama", "veri yapıları"], 3)

        # Kullanıcının verdiği ipuçlarını prompt'a ekle
        description_hint = ""
        if request.description_hint:
            description_hint = f"\nSoru İpucu: {request.description_hint}"

        function_name_hint = ""
        if request.function_name_hint:
            function_name_hint = f"\nFonksiyon Adı Önerisi: {request.function_name_hint}"

        # AI prompt hazırla
        prompt = f"""Bir Python programlama sorusu oluştur.

Zorluk seviyesi: {difficulty_desc.get(request.difficulty_level, 'Orta')}
Konu: {topic}
Etiketler: {', '.join(selected_tags)}{description_hint}{function_name_hint}

KATI KURALLAR:
* HackerRank'e veya LeetCode'dakine benzer sorular oluştur
* Soru parametreler almalı ve return ( yani geri dönüş değeri döndürmeli )
* Sorunun çözüm kodu ve test girdilerini ekle
* Parametre sayılarının tutarlı olmasına dikkat et
* Basit ve anlaşılır örnek girdi-çıktı ekle
* Çözüm kodu mümkün olduğunca sade olsun
* test_inputs alanında eğer ki çözüm kodunda kaç tane parametre varsa input sayısı da ona göre olmalı!
* test_inputs alanında sadece parametrelerin alacağı değerler olmalı çıktılar olmamalı!
* Olabildiğince özgün ve yaratıcı ol
* Olabildiğince az kütüphane bilgisi isteyen sorular hazırla
* Yanıt kesinlikle JSON formatında olmalı öbür türlüsü kabul edilmiyor!!!

YANIT FORMATLAMASI:
* Yanıtını SADECE geçerli bir JSON nesnesi olarak formatla
* Başka açıklama veya metin EKLEME, SADECE JSON nesnesini döndür
* JSON anahtarlarını çift tırnak içinde yaz: "title", "description" vb.
* JSON'un ilk ve son satırında sadece açılış ve kapanış süslü parantezleri olmalı
* JSON alanlarında Türkçe karakterleri düzgün kullan
* Tüm string değerler çift tırnak içinde olmalı
* JSON değerlerinde kaçış karakterlerini doğru kullan (\\n, \\t, \\" vb.)

Ürettiğin soru aşağıdaki mevcut sorulardan TAMAMEN farklı olmalı:
{', '.join(existing_titles[:10])}

Yanıtını JSON formatında oluştur:

{{
  "title": "Kısa ve açıklayıcı soru başlığı",
  "description": "Markdown formatında soru açıklaması örnek girdiler ve çıktılarla destekle",
  "function_name": "{request.function_name_hint if request.function_name_hint else "python_fonksiyon_adi"}",
  "difficulty": {request.difficulty_level},
  "topic": "{topic}",
  "points": {10 + request.difficulty_level * 5},
  "example_input": "Örnek girdi",
  "example_output": "Örnek çıktı",
  "test_inputs": [[1, 2], [3, 4]] (2 parametreli fonksiyon için örnek) parametre sayısı ve her bir testin içindeki girdi sayısı aynı olmalı, sadece parametrelerin alacağı değerler olmalı çıktılar bu kısımda olmamalı!,
  "solution_code": "def {request.function_name_hint if request.function_name_hint else "python_fonksiyon_adi"}(param1, param2):\\n    return sonuc"
}}"""

        # AI client oluştur ve soru iste
        client = AIClient(api_provider, api_key, model_name)
        response = client.chat_completion([
            {"role": "system", "content": "Sen bir Python programlama eğitmenisin ve öğrencilere programlama soruları hazırlıyorsun. SADECE JSON formatında yanıt ver, başka hiçbir açıklama veya metin ekleme. Cevabın geçerli bir JSON nesnesi olmalı."},
            {"role": "user", "content": prompt}
        ])

        # Kalan kod aynı şekilde kalacak (JSON işleme ve hata yönetimi)
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
            "raw_response": response_text,
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
                    json_data = json.loads(match)
                    debug_info["ayrıştırma_denemeleri"].append(f"JSON bloğu {i+1} başarılı")
                    break
                except Exception as e:
                    debug_info["ayrıştırma_denemeleri"].append(f"JSON bloğu {i+1} hatası: {str(e)}")

        # Strateji 3: Kod blokları içinde ara - TAMAMEN YENİ VERSİYON
        if not json_data:
            code_blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)```', response_text)
            debug_info["code_blocks_count"] = len(code_blocks)

            for i, block in enumerate(code_blocks):
                try:
                    cleaned_block = block.strip()

                    # Unicode escape karakterlerini çöz
                    try:
                        # Önce raw string olarak decode et
                        decoded_block = codecs.decode(cleaned_block, 'unicode_escape')
                        json_data = json.loads(decoded_block)
                        debug_info["ayrıştırma_denemeleri"].append(f"Unicode decode başarılı - blok {i + 1}")
                        break
                    except:
                        pass

                    # Manuel Unicode replacement
                    unicode_replacements = {
                        '\\u00c7': 'Ç', '\\u0131': 'ı', '\\u011f': 'ğ', '\\u015f': 'ş',
                        '\\u00fc': 'ü', '\\u00f6': 'ö', '\\u00e7': 'ç', '\\u011e': 'Ğ',
                        '\\u015e': 'Ş', '\\u00dc': 'Ü', '\\u00d6': 'Ö', '\\u0130': 'İ',
                        '\\u00f6n': 'ön', '\\u00fcnde': 'ünde', '\\u00e7\u0131kt\u0131': 'çıktı'
                    }

                    unicode_fixed = cleaned_block
                    for unicode_char, turkish_char in unicode_replacements.items():
                        unicode_fixed = unicode_fixed.replace(unicode_char, turkish_char)

                    try:
                        json_data = json.loads(unicode_fixed)
                        debug_info["ayrıştırma_denemeleri"].append(f"Manuel Unicode düzeltme başarılı - blok {i + 1}")
                        break
                    except json.JSONDecodeError as e:
                        # Regex ile temel alanları çıkart (son çare)
                        parsed_json = {}

                        # Başlık
                        title_match = re.search(r'"title":\s*"([^"]*(?:\\.[^"]*)*)"', unicode_fixed)
                        if title_match:
                            parsed_json["title"] = title_match.group(1).replace('\\"', '"')

                        # Açıklama - özel karakterler için daha güçlü regex
                        desc_match = re.search(r'"description":\s*"((?:[^"\\]|\\.)*)"\s*,', unicode_fixed, re.DOTALL)
                        if desc_match:
                            desc = desc_match.group(1)
                            desc = desc.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                            parsed_json["description"] = desc

                        # Diğer alanlar
                        for field, pattern in [
                            ("function_name", r'"function_name":\s*"([^"]*)"'),
                            ("topic", r'"topic":\s*"([^"]*)"'),
                            ("example_input", r'"example_input":\s*"([^"]*(?:\\.[^"]*)*)"'),
                            ("example_output", r'"example_output":\s*"([^"]*(?:\\.[^"]*)*)"'),
                        ]:
                            match = re.search(pattern, unicode_fixed)
                            if match:
                                parsed_json[field] = match.group(1).replace('\\"', '"').replace('\\n', '\n')

                        # Sayısal alanlar
                        for field, pattern in [
                            ("difficulty", r'"difficulty":\s*(\d+)'),
                            ("points", r'"points":\s*(\d+)')
                        ]:
                            match = re.search(pattern, unicode_fixed)
                            if match:
                                parsed_json[field] = int(match.group(1))

                        # Test inputs - liste olarak parse et
                        test_match = re.search(r'"test_inputs":\s*(\[[\s\S]*?\])', unicode_fixed)
                        if test_match:
                            try:
                                parsed_json["test_inputs"] = ast.literal_eval(test_match.group(1))
                            except:
                                parsed_json["test_inputs"] = []

                        # Solution code
                        solution_match = re.search(r'"solution_code":\s*"((?:[^"\\]|\\.)*)"', unicode_fixed, re.DOTALL)
                        if solution_match:
                            solution = solution_match.group(1)
                            solution = solution.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')
                            parsed_json["solution_code"] = solution

                        # En az temel alanlar varsa kabul et
                        if len(parsed_json) >= 4 and "title" in parsed_json and "description" in parsed_json:
                            json_data = parsed_json
                            debug_info["ayrıştırma_denemeleri"].append(f"Regex ayrıştırma başarılı - blok {i + 1}")
                            break

                except Exception as e:
                    debug_info["ayrıştırma_denemeleri"].append(f"Blok {i + 1} genel hatası: {str(e)}")

        # Eğer JSON ayrıştırılabildiyse verileri güncelle
        if json_data:
            # Zorluk seviyesi ve puan
            if "difficulty" in json_data:
                data["difficulty"] = json_data["difficulty"]
            if "points" in json_data:
                data["points"] = json_data["points"]

            # Temel alan kontrolü
            for field in ["title", "description", "function_name", "solution_code"]:
                if field in json_data and json_data[field]:
                    data[field] = json_data[field]

            # Topic değeri boş ise rastgele seçilen topic değerini kullan
            if not data["topic"]:
                data["topic"] = topic

            # Örnek girdi ve çıktılar
            if "example_input" in json_data and json_data["example_input"]:
                data["example_input"] = json_data["example_input"]
            if "example_output" in json_data and json_data["example_output"]:
                data["example_output"] = json_data["example_output"]

            # Test girdileri
            if "test_inputs" in json_data:
                try:
                    # Test girdilerini string olarak sakla
                    if isinstance(json_data["test_inputs"], str):
                        data["test_inputs"] = json_data["test_inputs"]
                    else:
                        data["test_inputs"] = json.dumps(json_data["test_inputs"])
                except Exception as e:
                    data["test_inputs"] = "[]"
                    data["error"] = f"Test girdileri ayrıştırma hatası: {str(e)}"
        else:
            # JSON ayrıştırılamadıysa hata döndür
            data["error"] = "JSON ayrıştırma hatası: AI yanıtı beklenen formatta değil"
            data["debug_info"] = json.dumps(debug_info)
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
                "response_text": response_text if 'response_text' in locals() else "Yanıt alınamadı"
            },
            "title": "",
            "description": "",
            "function_name": "",
            "description_hint": "",
            "difficulty": request.difficulty_level,
            "topic": request.topic,
            "points": 10 + request.difficulty_level * 5,
            "example_input": "Örnek girdi yok",
            "example_output": "Örnek çıktı yok",
            "test_inputs": "[]",
            "solution_code": ""
        }

@api.post("/api/trigger-event")
def trigger_event(request: EventRequest):
    """
    Bir HTTP POST isteği alarak bir olay türü tetikleyen fonksiyon.

    Parametreler:
        request (EventRequest): Tetiklenmek istenilen olay türü ve
        olayla ilgili veri içeren nesne.

    Dönen:
        dict: İşlem sonucunu ve ilgili mesajı içeren bir sözlük.
    """
    try:
        # String olarak gelen event türünü EventType'a çevir
        event_type = EventType[request.event_type]
        event_manager.trigger_event(event_type, request.data)
        return {"success": True, "message": f"{request.event_type} olayı başarıyla tetiklendi"}
    except KeyError:
        return {"success": False, "message": f"Geçersiz olay türü: {request.event_type}"}
    except Exception as e:
        return {"success": False, "message": f"Olay tetiklenirken hata oluştu: {str(e)}"}

@api.get("/health")
def health_check():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok"}
    )

@api.post("/api/save-question")
def save_question(question: ProgrammingQuestionCreate, db=Depends(get_db)):
    """
    Oluşturulan veya düzenlenen programlama sorusunu veritabanına kaydeder.
    """
    try:
        # Eğer soru ID'si varsa güncelleme, yoksa yeni ekleme
        if question.id:
            # Mevcut soruyu güncelle
            update_query = text("""
                                UPDATE programming_question
                                SET title          = :title,
                                    description    = :description,
                                    function_name  = :function_name,
                                    difficulty     = :difficulty,
                                    points         = :points,
                                    topic          = :topic,
                                    example_input  = :example_input,
                                    example_output = :example_output,
                                    test_inputs    = :test_inputs,
                                    solution_code  = :solution_code,
                                    updated_at     = NOW()
                                WHERE id = :id
                                """)

            db.execute(update_query, {
                "id": question.id,
                "title": question.title,
                "description": question.description,
                "function_name": question.function_name,
                "difficulty": question.difficulty,
                "points": question.points,
                "topic": question.topic,
                "example_input": question.example_input,
                "example_output": question.example_output,
                "test_inputs": question.test_inputs,
                "solution_code": question.solution_code
            })

            question_id = question.id
            message = "Soru başarıyla güncellendi"
        else:
            # Son eklenen ID'yi al
            last_id_query = text("SELECT MAX(id) as last_id FROM programming_question")
            result = db.execute(last_id_query).first()
            last_id = result.last_id if result and result.last_id else 0
            new_id = last_id + 1

            # Yeni soru ekle
            insert_query = text("""
                                INSERT INTO programming_question (id, title, description, function_name, difficulty,
                                                                  points, topic,
                                                                  example_input, example_output, test_inputs,
                                                                  solution_code, created_at, updated_at)
                                VALUES (:id, :title, :description, :function_name, :difficulty, :points, :topic,
                                        :example_input, :example_output, :test_inputs, :solution_code, NOW(), NOW())
                                """)

            db.execute(insert_query, {
                "id": new_id,
                "title": question.title,
                "description": question.description,
                "function_name": question.function_name,
                "difficulty": question.difficulty,
                "points": question.points,
                "topic": question.topic,
                "example_input": question.example_input,
                "example_output": question.example_output,
                "test_inputs": question.test_inputs,
                "solution_code": question.solution_code
            })

            question_id = new_id
            message = "Yeni soru başarıyla eklendi"

        db.commit()
        return {"success": True, "message": message, "id": question_id}

    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Soru kaydedilirken hata oluştu: {str(e)}"}


@api.get("/api/instagram-posts", response_model=List[InstagramPostResponse])
def get_instagram_posts(
        instagram_username: str,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
):
    """
    Belirtilen Instagram kullanıcısının postlarını HTTP isteği ile JSON verisi olarak çeker.
    """
    try:
        import requests
        import json
        import time
        import random
        import re
        import traceback
        from datetime import datetime
        from bs4 import BeautifulSoup

        # Boş posts listesi oluştur
        posts = []

        # Kullanıcı ajanları listesi
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
        ]

        # İsteği hazırla
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }

        print(f"Instagram verisi çekiliyor: {instagram_username}")

        # Instagram kullanıcı profil sayfasına istek yap
        profile_url = f'https://www.instagram.com/{instagram_username}/'

        try:
            response = requests.get(profile_url, headers=headers, timeout=15)
            print(f"Instagram yanıt kodu: {response.status_code}")

            if response.status_code == 200:
                # Hiç veri bulunamadıysa API deneme
                if not posts:
                    api_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={instagram_username}"
                    api_headers = headers.copy()
                    api_headers['X-IG-App-ID'] = '936619743392459'  # Instagram web uygulaması ID'si

                    try:
                        api_response = requests.get(api_url, headers=api_headers, timeout=15)
                        if api_response.status_code == 200:
                            api_data = api_response.json()
                            user_data = api_data.get('data', {}).get('user', {})
                            media_items = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])

                            for i, edge in enumerate(media_items):
                                node = edge.get('node', {})
                                if node:
                                    post_id = node.get('id', i)
                                    image_url = node.get('display_url', '')
                                    caption_edges = node.get('edge_media_to_caption', {}).get('edges', [])
                                    caption = caption_edges[0].get('node', {}).get('text', '') if caption_edges else ''
                                    likes = node.get('edge_liked_by', {}).get('count', 0) or node.get(
                                        'edge_media_preview_like', {}).get('count', 0)
                                    timestamp = node.get('taken_at_timestamp', 0)
                                    post_date = datetime.fromtimestamp(timestamp).strftime(
                                        '%Y-%m-%d') if timestamp else 'Bilinmiyor'
                                    shortcode = node.get('shortcode', '')
                                    post_url = f'https://www.instagram.com/p/{shortcode}/'

                                    posts.append({
                                        'id': post_id,
                                        'image_url': image_url,
                                        'caption': caption,
                                        'likes': likes,
                                        'post_date': post_date,
                                        'post_url': post_url
                                    })
                    except Exception as api_err:
                        print(f"API hatası: {str(api_err)}")

            else:
                print(f"Instagram yanıtı başarısız: {response.status_code}")

        except requests.RequestException as req_err:
            print(f"İstek hatası: {str(req_err)}")

        # Veri varsa limit ve offset ile döndür
        return posts[offset:offset + limit]

    except Exception as e:
        print(f"Instagram postları alınırken hata: {str(e)}")
        traceback.print_exc()
        return []

@api.get('/api/proxy-image')
async def proxy_image(request: Request):
    """Instagram görsellerini proxy üzerinden sunmak için kullanılır"""
    try:
        url = request.query_params.get('url')
        if not url:
            return Response("URL parametresi gerekli", status_code=400)

        response = requests.get(url, timeout=10)
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get('Content-Type', 'image/jpeg')
        )
    except Exception as e:
        return Response(f"Görsel yüklenirken hata: {str(e)}", status_code=404)
