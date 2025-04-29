# app/services/evaluation_service.py
import json
import time
import traceback
from contextlib import redirect_stdout
import io


def check_indentation(code):
    """Kod içindeki girinti hatalarını kontrol eder"""
    lines = code.splitlines()
    for i, line in enumerate(lines):
        if line.strip() and line.startswith(" ") and "\t" in line:
            return False, i + 1
    return True, 0

def evaluate_solution(user_code, question):
    """
    Kullanıcı çözümünü değerlendirir ve sonuçları döndürür

    Args:
        user_code (str): Kullanıcının gönderdiği Python kodu
        question (ProgrammingQuestion): Programlama sorusu nesnesi

    Returns:
        dict: Değerlendirme sonucunu içeren sözlük
    """
    result = {
        "is_correct": False,
        "execution_time": 0,
        "errors": []
    }

    # Girinti kontrolü ekleyin
    is_valid, line_num = check_indentation(user_code)
    if not is_valid:
        result["errors"].append(f"Girinti hatası: Satır {line_num}'de karışık tab ve boşluk kullanımı tespit edildi.")
        return result

    # Test girdilerini JSON olarak parse et
    try:
        test_inputs = json.loads(question.test_inputs)
    except json.JSONDecodeError:
        result["errors"].append("Test girdileri geçerli JSON formatında değil")
        return result

    # Kullanıcı kodunu çalıştırma işlemi
    try:
        # Kullanıcı kodunu çalıştırmak için güvenli bir namespace oluştur
        user_namespace = {}

        # Kullanıcı kodunu çalıştır
        exec(user_code, user_namespace)

        # Fonksiyon adını kullanarak fonksiyonu al
        user_function = user_namespace.get(question.function_name)

        if not user_function:
            result["errors"].append(f"'{question.function_name}' adında bir fonksiyon bulamadık")
            return result

        # Bütün test girdilerini çalıştır
        start_time = time.time()

        # Admin çözümünü çalıştırmak için namespace
        admin_namespace = {}
        exec(question.solution_code, admin_namespace)
        admin_function = admin_namespace.get(question.function_name)

        # Tüm testleri geç
        for test_input in test_inputs:
            # Kullanıcı fonksiyonunu çalıştırma
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                user_result = user_function(*test_input)

            # Admin fonksiyonunu çalıştırma
            admin_result = admin_function(*test_input)

            # Sonuçları karşılaştırma
            if user_result != admin_result:
                result["errors"].append(
                    f"Test başarısız: Girdi: {test_input}, Beklenen çıktı: {admin_result}, Alınan çıktı: {user_result}")

        end_time = time.time()
        result["execution_time"] = (end_time - start_time) * 1000  # milisaniye cinsine dönüştür

        # Hatalar yoksa, çözüm doğru
        if not result["errors"]:
            result["is_correct"] = True

    except Exception as e:
        result["errors"].append(f"Hata: {str(e)}")
        result["errors"].append(traceback.format_exc())

    return result