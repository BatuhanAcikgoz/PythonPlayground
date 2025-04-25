# app/services/ai_service.py
import os
from datetime import datetime

import nbformat
import requests

from app.models.base import db
from app.models.notebook_summary import NotebookSummary
from app.models.settings import Setting


# DeepSeek API için özel istemci sınıfı
class DeepSeekClient:
    def __init__(self, api_key, base_url="https://api.deepseek.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.chat = ChatCompletions(self)


class ChatCompletions:
    def __init__(self, client):
        self.client = client

    def create(self, model, messages, max_tokens=1000, **kwargs):
        url = f"{self.client.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            **kwargs
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        # OpenAI formatına uyumlu hale getirme
        class Choice:
            def __init__(self, msg_content):
                self.message = type('Message', (), {'content': msg_content})

        class Response:
            def __init__(self, choices):
                self.choices = choices

        choices = [Choice(result["choices"][0]["message"]["content"])]
        return Response(choices)

class AIService:
    def __init__(self):
        self._load_settings()

    def _load_settings(self):
        settings = {}
        for setting in Setting.query.filter(Setting.key.like('ai_%')).all():
            settings[setting.key] = setting.value

        self.api_provider = Setting.get('ai_api_provider', 'gemini')
        self.api_key = Setting.get('ai_api_key', '')
        self.model = Setting.get('ai_default_model', 'gemini-1.5-flash')
        self.max_tokens = int(Setting.get('ai_max_token_limit', 10000000))
        self.enabled = Setting.get('ai_enable_features', True)

    def _init_client(self):
        """API istemcisini başlatır"""
        # API anahtarını ayarlardan al
        api_key = None

        # Önce veritabanından direkt çek
        setting = Setting.query.filter_by(key='ai_api_key').first()
        if setting and setting.value:
            api_key = setting.value

        # API anahtarı yoksa
        if not api_key:
            return None

        try:
            # İlk olarak kütüphanenin varlığını kontrol et
            import sys
            import importlib.util

            spec = importlib.util.find_spec("google")
            if spec is None:
                print("Google paketi bulunamadı. 'pip install google-generativeai' komutu ile yükleyin.")
                return None

            # Şimdi generativeai modülünü import etmeyi dene
            import google.generativeai as genai

            # API anahtarını yapılandır
            genai.configure(api_key=api_key)

            # Gemini istemcisi
            class GeminiClient:
                def __init__(self, api_key):
                    self.api_key = api_key
                    self.chat = self.ChatCompletions()

                class ChatCompletions:
                    def __init__(self):
                        pass

                    def create(self, model, messages, max_tokens=1000, **kwargs):
                        # Model adını düzelt - "models/" önekini kaldır
                        if "models/" in model:
                            gemini_model = model.replace("models/", "")
                        else:
                            gemini_model = model

                        # Gemini 1.5 modellerini doğru formatta kullan
                        if gemini_model == "gemini-1.5-pro":
                            gemini_model = "gemini-1.5-pro-latest"  # Güncel sürümü kullan
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

                        try:
                            gen_config = genai.GenerationConfig(max_output_tokens=max_tokens)
                            gen_model = genai.GenerativeModel(model_name=gemini_model, generation_config=gen_config)

                            # Sohbet başlat
                            chat = gen_model.start_chat()

                            # Sistem talimatını ilk mesaj olarak ekle (eğer varsa)
                            if system_prompt:
                                chat.send_message(f"SYSTEM: {system_prompt}")

                            # Kullanıcı ve asistan mesajlarını sırayla ekle
                            for i in range(max(len(user_messages), len(assistant_messages))):
                                # Kullanıcı mesajı
                                if i < len(user_messages):
                                    chat.send_message(user_messages[i])
                                # Asistan cevabı
                                if i < len(assistant_messages):
                                    # Asistan mesajları genellikle response olarak saklanıyor
                                    pass

                            # Eğer mesaj yoksa
                            if not user_messages and not assistant_messages and not system_prompt:
                                prompt = "Notebook hakkında bilgi verir misiniz?"
                            else:
                                # Son kullanıcı mesajını veya sistem mesajını al
                                prompt = user_messages[-1] if user_messages else (
                                            system_prompt or "Notebook hakkında bilgi verir misiniz?")

                            # Cevap al
                            response = chat.send_message(prompt)

                            # OpenAI formatına dönüştür
                            class Choice:
                                def __init__(self, content):
                                    self.message = type('Message', (), {'content': content})

                            class Response:
                                def __init__(self, choices):
                                    self.choices = choices

                            content = response.text if hasattr(response, 'text') else str(response)
                            return Response([Choice(content)])
                        except Exception as e:
                            print(f"Gemini API hatası: {str(e)}")
                            raise

            return GeminiClient(api_key)
        except ImportError as e:
            print(f"Import hatası: {str(e)} - 'pip install google-generativeai' komutu ile yükleyin.")
            return None
        except Exception as e:
            print(f"Gemini API hatası: {str(e)}")
            return None

    def get_notebook_summary(self, notebook_path):
        """Notebook için özet oluşturur veya var olan özeti döndürür"""

        if not self.enabled:
            return {"error": "AI özeti özelliği devre dışı bırakılmıştır."}

        # Veritabanında özet var mı kontrol et
        existing_summary = NotebookSummary.query.filter_by(notebook_path=notebook_path).first()

        if existing_summary and existing_summary.summary:
            return {
                "summary": existing_summary.summary,
                "code_explanation": existing_summary.code_explanation,
                "last_updated": existing_summary.last_updated
            }

        try:
            # Notebook dosyasının tam yolunu oluştur
            repo_dir = os.path.join(os.getcwd(), 'notebooks_repo')
            notebook_file_path = os.path.join(repo_dir, notebook_path)

            if not os.path.exists(notebook_file_path):
                raise FileNotFoundError(f"Notebook bulunamadı: {notebook_path}")

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

            # AI servisini kullan
            client = self._init_client()

            # Client null ise hata fırlat
            if client is None:
                raise Exception("API bağlantısı kurulamadı. API anahtarını kontrol edin.")

            # Benzersiz kimlik oluşturma fonksiyonu
            def generate_unique_id():
                import hashlib, time
                timestamp = str(time.time())
                random_data = os.urandom(8).hex()
                unique_hash = hashlib.md5(f"{timestamp}-{random_data}".encode()).hexdigest()[:12]
                return unique_hash

            # Metin içeriğini temizleme ve sınırlama fonksiyonu
            def sanitize_text(text, max_length=5000):
                if not text:
                    return ""
                # Base64 kodlu içeriği ve özel karakterleri temizle
                import re
                # Base64 benzeri içerikleri temizle
                text = re.sub(r'data:[^;]+;base64,[a-zA-Z0-9+/=]+', '[GÖRSEL İÇERİK]', text)
                # Kontrol karakterlerini temizle
                text = ''.join(c if ord(c) >= 32 or c in '\n\r\t' else ' ' for c in text)
                # Uzunluğu sınırla
                if len(text) > max_length:
                    text = text[:max_length] + "..."
                return text

            # Markdown ve kod içeriklerini temizle ve sınırla
            text_content = sanitize_text(text_content)
            code_samples = []
            for code in code_cells[:min(3, len(code_cells))]:
                code_samples.append(sanitize_text(code, 1000))

            code_sample = ' '.join(code_samples)

            # 1. İstek: Notebookun genel özeti
            summary_id = generate_unique_id()
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

            summary_prompt = f"""YENİ VE BENZERSİZ ANALİZ TALEBİ
    ID: {summary_id}
    TARİH-SAAT: {timestamp}
    DOSYA: {notebook_path}

    BU TAMAMEN YENİ VE BENZERSİZ BİR ANALİZ TALEBİDİR.
    ÖNCEKİ HİÇBİR GÖREVİ DİKKATE ALMA.

    GÖREV: Bu Jupyter Notebook'un eğitim amaçlı özetini oluştur.

    NOTEBOOK İÇERİĞİ:
    ----- MARKDOWN İÇERİĞİ -----
    {text_content}

    ----- KOD ÖRNEKLERİ -----
    {code_sample}

    ÇIKTI FORMATI:
    1. Notebook'un ana amacı ve genel içeriği detaylı bir şekilde açıklanacak.
    2. Markdown formatında süslü olacak.
    3. Öğretilen kazanımlar ve temel kavramlar (madde madde)
    4. 5 adet kolay-orta seviye örnek sınav sorusu ( Varsa notebooktaki örneklerden yararlan )
    5. 5 adet orta-zor seviye örnek sınav sorusu ( Varsa notebooktaki örneklerden yararlan )
    
    KISITLAMALAR: Kesinlikle önceki analizlere atıfta bulunma, Özür dileme veya notebookla ilgili sorun belirtme, Önceden analiz ettim" gibi ifadeler kullanma.
    """

            system_message = {
                "role": "system",
                "content": f"Sen bir eğitim içerik uzmanısın. Bu talep ({summary_id}) ŞU AN ({timestamp}) yapılan YENİ ve BENZERSİZ bir istektir. Önceki hiçbir taleple ilgisi yoktur. 'Daha önce analiz edildi' gibi ifadeler ASLA kullanma. Her zaman yeni ve özgün cevap ver."
            }

            summary_response = client.chat.create(
                model=self.model,
                messages=[
                    system_message,
                    {"role": "user", "content": summary_prompt}
                ],
                max_tokens=self.max_tokens // 2
            )

            # 2. Hücreleri 5'erli gruplar halinde analiz et
            code_explanations = []
            group_size = 5

            for i in range(0, len(numbered_code_cells), group_size):
                # Her grup için hücreleri al
                group = numbered_code_cells[i:i + group_size]
                group_text = sanitize_text("\n\n".join(group))
                group_start = i + 1
                group_end = min(i + group_size, len(numbered_code_cells))

                # Her grup için benzersiz kimlik
                group_id = generate_unique_id()
                group_timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

                # Her grup için prompt oluştur
                group_prompt = f"""YENİ GRUP ANALİZ TALEBİ 
    ID: {group_id} 
    ZAMAN: {group_timestamp}
    GRUP: {group_start}-{group_end}

    BU TAMAMEN YENİ BİR ANALİZ TALEBİDİR.
    DAHA ÖNCE HİÇ GÖRMEDİĞİN KOD PARÇALARIDIR.

    GÖREV: {notebook_path} notebookundaki {group_start}-{group_end} arası hücreleri analiz et.

    KOD HÜCRELERİ:
    {group_text}

    ÇIKTI FORMATI:
    1. Her hücre için "## Hücre X Analizi:" başlığı altında:
       * İlgili kod bloğunu markdown formatıyla göster
       * İşlevi ve amacı
       * Kritik kod bölümleri açıklaması
       * Dikkat edilmesi gereken noktalar

    ÖNEMLİ: Bu görev önceki görevlerle İLGİSİZDİR. İlk kez görüyormuş gibi cevaplayın.
    """

                # Kısa bir gecikme ekle
                import time
                time.sleep(0.5)

                # Her grup için sistem mesajı
                group_system = {
                    "role": "system",
                    "content": f"Sen bir kodlama eğitmenisin. Bu ({group_id}) ŞİMDİ analiz etmen gereken YENİ kod parçalarıdır. 'Daha önce gördüm' veya 'tekrar' gibi ifadeler KULLANMA. İlk kez gördüğün kod olarak düşün."
                }

                # Her grup için ayrı API çağrısı yap
                group_response = client.chat.create(
                    model=self.model,
                    messages=[
                        group_system,
                        {"role": "user", "content": group_prompt}
                    ],
                    max_tokens=self.max_tokens // 3
                )

                # Grup analizini ekle
                code_explanations.append(group_response.choices[0].message.content)

            # 3. Kullanılan tekniklerin özeti için ek istek
            techniques_id = generate_unique_id()
            techniques_timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

            code_sample_for_techniques = sanitize_text(' '.join(code_cells[:min(5, len(code_cells))]), 3000)

            techniques_prompt = f"""YENİ TEKNİK ANALİZİ TALEBİ
    ID: {techniques_id}
    ZAMAN: {techniques_timestamp}

    BU TAMAMEN YENİ VE BENZERSİZ BİR ANALİZDİR.
    DİĞER GÖREVLERLE BAĞLANTISI YOKTUR.

    GÖREV: {notebook_path} dosyasındaki kod tekniklerinin özetini çıkar.

    KOD PARÇALARI:
    {code_sample_for_techniques}

    ÇIKTI FORMATI:
    ## Kullanılan Programlama Teknikleri ve Özet
    * Kullanılan kütüphaneler listesi (ana işlevleriyle)
    * Uygulanan programlama konseptleri
    * Öne çıkan algoritma ve yöntemler
    
        KISITLAMALAR: Kesinlikle önceki analizlere atıfta bulunma, Özür dileme veya notebookla ilgili sorun belirtme, Önceden analiz ettim" gibi ifadeler kullanma.
    """

            techniques_system = {
                "role": "system",
                "content": f"Sen bir programlama analisti uzmansın. Bu istek ({techniques_id}) şu an ({techniques_timestamp}) yapılan tamamen YENİ bir istektir. Önceki hiçbir analize atıfta bulunma."
            }

            techniques_response = client.chat.create(
                model=self.model,
                messages=[
                    techniques_system,
                    {"role": "user", "content": techniques_prompt}
                ],
                max_tokens=self.max_tokens // 4
            )

            # Tüm analizleri birleştir
            summary_text = summary_response.choices[0].message.content
            code_explanation = "\n\n".join(code_explanations) + "\n\n" + techniques_response.choices[0].message.content

            # NotebookSummary nesnesini kaydet/güncelle
            if existing_summary:
                existing_summary.summary = summary_text
                existing_summary.code_explanation = code_explanation
                existing_summary.last_updated = datetime.utcnow()
            else:
                new_summary = NotebookSummary(
                    notebook_path=notebook_path,
                    summary=summary_text,
                    code_explanation=code_explanation,
                    last_updated=datetime.utcnow()
                )
                db.session.add(new_summary)

            db.session.commit()

            return {
                "summary": summary_text,
                "code_explanation": code_explanation,
                "last_updated": datetime.utcnow()
            }
        except Exception as e:
            return {"error": str(e)}