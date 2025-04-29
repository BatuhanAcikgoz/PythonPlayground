# app/routes/programming.py
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user

from api import evaluate_solution
from app.models.base import db
from app.models.programming_question import ProgrammingQuestion
from app.models.submission import Submission

programming_bp = Blueprint('programming', __name__)


@programming_bp.route('/questions')
@login_required
def questions():
    """Programlama sorularını listeler"""
    questions = ProgrammingQuestion.query.order_by(ProgrammingQuestion.difficulty).all()

    # Her soru için kullanıcının çözüp çözmediğini kontrol et
    for question in questions:
        question.solved = Submission.has_correct_submission(current_user.id, question.id)

    return render_template('questions.html', questions=questions)


def generate_starter_code(question):
    """Sorunun test girdilerine göre başlangıç kodu oluşturur"""
    import json

    function_name = question.function_name

    # Varsayılan parametreler
    parameters = []
    param_types = []
    return_type = "any"

    try:
        # Test girdilerini JSON olarak parse et
        test_inputs = json.loads(question.test_inputs)
        if test_inputs and len(test_inputs) > 0:
            # İlk test girdisini kullanarak parametre sayısını ve türlerini belirle
            first_test = test_inputs[0]

            for i, param_value in enumerate(first_test):
                param_name = f"param{i + 1}"
                param_type = type(param_value).__name__
                parameters.append(param_name)
                param_types.append(param_type)

            # Dönüş tipini belirle (admin çözümünü çalıştırarak)
            try:
                admin_namespace = {}
                exec(question.solution_code, admin_namespace)
                admin_func = admin_namespace.get(function_name)

                if admin_func:
                    result = admin_func(*first_test)
                    return_type = type(result).__name__
            except:
                # Dönüş tipini belirleyemezsek varsayılan olarak "any" kullan
                pass
    except:
        # Hata durumunda varsayılan olarak tek parametre kullan
        parameters = ["x"]
        param_types = ["any"]

    # Parametre listesi oluştur
    params_str = ", ".join(parameters)

    # Parametre açıklamalarını yorum satırları olarak ekle
    param_docs = []
    for param, typ in zip(parameters, param_types):
        param_docs.append(f"# @param {param} ({typ})")

    param_docs_str = "\n    ".join(param_docs)

    # Başlangıç kodu şablonu
    return f"""def {function_name}({params_str}):
        \"\"\"
        {question.title} için çözüm fonksiyonu

        {param_docs_str}

        @return: ({return_type})
        \"\"\"
        # Çözümünüzü buraya yazın
    """

@programming_bp.route('/questions/<int:id>')
@login_required
def question(id):
    """Belirtilen programlama sorusunu gösterir"""
    question = ProgrammingQuestion.query.get_or_404(id)

    # Kullanıcının bu soruyu daha önce doğru çözüp çözmediğini kontrol et
    if Submission.has_correct_submission(current_user.id, id):
        flash('Bu soruyu daha önce başarıyla çözdünüz!', 'info')
        return redirect(url_for('programming.questions'))

    # Kullanıcının bu soru için en son gönderimini bul
    last_submission = Submission.query.filter_by(
        user_id=current_user.id,
        question_id=id
    ).order_by(Submission.created_at.desc()).first()

    # Önceki çözüm varsa kullan, yoksa yeni başlangıç kodu oluştur
    if last_submission:
        default_code = last_submission.code
    else:
        default_code = generate_starter_code(question)

    return render_template('question.html',
                           question=question,
                           default_code=default_code)

@programming_bp.route('/questions/<int:id>/submit', methods=['POST'])
@login_required
def submit_solution(id):
    """Çözüm gönderme"""
    question = ProgrammingQuestion.query.get_or_404(id)
    code = request.form.get('code')

    if not code:
        flash('Kod boş olamaz.', 'error')
        return redirect(url_for('programming.question', id=id))

    # Çözümü değerlendir
    result = evaluate_solution(code, question)

    # Submission kaydını oluştur
    submission = Submission(
        user_id=current_user.id,
        question_id=question.id,
        code=code,
        is_correct=result['is_correct'],  # Doğru anahtarı kullan
        test_results=result,
        execution_time=result['execution_time'],
        error_message=result.get('error_message', ''),
    )

    db.session.add(submission)
    db.session.commit()

    if result['is_correct']:  # 'success' yerine 'is_correct'
        flash('Tebrikler! Tüm testleri geçen bir çözüm gönderdiniz.', 'success')
    else:
        flash('Çözümünüz bazı testlerden geçemedi. Detaylar için sonuçlara bakın.', 'warning')

    return redirect(url_for('programming.submission', id=submission.id))


@programming_bp.route('/submissions/<int:id>')
@login_required
def submission(id):
    """Belirli bir gönderimi gösterir"""
    submission = Submission.query.get_or_404(id)

    # Sadece kendi gönderimleri veya öğretmen/admin rolüne sahipse göster
    if submission.user_id != current_user.id and not (
            current_user.has_role('teacher') or current_user.has_role('admin')):
        flash('Bu gönderimi görüntüleme izniniz yok.', 'error')
        return redirect(url_for('programming.questions'))

    return render_template('submission.html', submission=submission)


@programming_bp.route('/my-submissions')
@login_required
def my_submissions():
    """Kullanıcının gönderimleri"""
    submissions = Submission.query.filter_by(user_id=current_user.id) \
        .order_by(Submission.created_at.desc()).all()

    return render_template('my_submissions.html', submissions=submissions)


@programming_bp.route('/questions/<int:id>/evaluate', methods=['POST'])
@login_required
def evaluate_code(id):
    """AJAX ile kod değerlendirme"""
    question = ProgrammingQuestion.query.get_or_404(id)
    code = request.json.get('code')

    if not code:
        return jsonify({'error': 'Kod boş olamaz.'}), 400

    # FastAPI servisine istek gönder
    try:
        evaluation_request = {
            "code": code,
            "function_name": question.function_name,
            "test_inputs": question.test_inputs,
            "solution_code": question.solution_code
        }

        response = requests.post(
            "http://127.0.0.1:8000/api/evaluate",
            json=evaluation_request,
            timeout=5
        )

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            # FastAPI hatası durumunda hata mesajı döndür
            return jsonify({
                "is_correct": False,
                "execution_time": 0,
                "errors": ["Kod değerlendirme servisi geçici olarak kullanılamıyor."]
            }), 500

    except requests.RequestException as e:
        # Bağlantı hatası durumunda hata mesajı döndür
        current_app.logger.error(f"API bağlantı hatası: {str(e)}")
        return jsonify({
            "is_correct": False,
            "execution_time": 0,
            "errors": ["Kod değerlendirme servisi geçici olarak kullanılamıyor."]
        }), 500