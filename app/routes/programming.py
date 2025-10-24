# app/routes/programming.py
import json

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user

# Remove old import
# from api import evaluate_solution, EvaluationRequest
from app.services.code_execution_service import get_code_execution_service
from app.events import event_manager
from app.events.event_definitions import EventType
from app.forms.programming import SolutionSubmitForm, CodeEvaluationForm
from app.models.base import db
from app.models.programming_question import ProgrammingQuestion
from app.models.submission import Submission

programming_bp = Blueprint('programming', __name__)

@programming_bp.route('/questions')
@login_required
def questions():
    """
    Fonksiyon, "/questions" adlı bir route tanımlar ve oturum açmış kullanıcılar için
    mevcut programlama sorularını görüntüler. Sorular zorluk derecesine göre sıralanır ve
    her bir soru için kullanıcının önceki çözümlerine bakarak çözülüp çözülmediği bilgisi
    eklenir. Sonuç, bir HTML şablonuna gönderilir ve kullanıcıya soruların listesi
    görüntülenir.

    Args:
        None

    Returns:
        flask.Response: Soruların listelendiği 'questions.html' şablonunun oluşturulmuş
        yanıtını döner.

    Raises:
        None
    """
    questions = ProgrammingQuestion.query.order_by(ProgrammingQuestion.difficulty).all()

    # Her soru için kullanıcının çözüp çözmediğini kontrol et
    for question in questions:
        question.solved = Submission.has_correct_submission(current_user.id, question.id)

    return render_template('questions.html', questions=questions)


@programming_bp.route('/questions/<int:id>')
@login_required
def question(id):
    """
    Görselleştirme ve kullanıcı etkileşimleri için bir programlama sorusunun detaylarını içeren bir
    sayfanın görüntülenmesini sağlayan bir fonksiyon. Multi-language desteği ile çalışır.

    Arguments:
        id (int): Görüntülenecek programlama sorusunun kimliği.

    Returns:
        Response: Şablon render edilerek oluşturulan HTTP cevabını döner.

    Raises:
        404 Not Found: Eğer verilen id ile eşleşen bir programlama sorusu bulunamazsa hata yükselir.
    """
    question = ProgrammingQuestion.query.get_or_404(id)
    code_service = get_code_execution_service()

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
        default_code = code_service.get_starter_code(question)

    return render_template('question.html',
                           question=question,
                           default_code=default_code)


@programming_bp.route('/questions/<int:id>/submit', methods=['POST'])
@login_required
def submit_solution(id):
    """
    submit_solution fonksiyonu bir programlama sorusuna yönelik kod çözümünün gönderilmesine olanak tanır.
    Multi-language desteği ile Python, R ve MATLAB kodlarını değerlendirir.

    Args:
        id (int): Değerlendirilecek sorunun kimlik numarası.

    Raises:
        None.

    Returns:
        Werkzeug Response: Gönderme işlemini tamamladıktan sonra kullanıcıyı uygun bir sayfaya yönlendiren cevap.

    """
    question = ProgrammingQuestion.query.get_or_404(id)
    form = SolutionSubmitForm()

    if form.validate_on_submit():
        code = form.code.data
        code_service = get_code_execution_service()

        # NEW: Use multi-language execution service
        result = code_service.execute_solution(
            language=question.language,
            code=code,
            function_name=question.function_name,
            test_inputs=question.test_inputs,
            solution_code=question.solution_code
        )

        # Başarı durumu ve sonuçları kaydetme
        submission = Submission(
            user_id=current_user.id,
            question_id=question.id,
            code=code,
            is_correct=result.get('is_correct', False),
            test_results=json.dumps(result.get('test_results', [])),
            execution_time=result.get('execution_time', 0),
            error_message=json.dumps(result.get('error_message', []))
        )

        db.session.add(submission)
        db.session.commit()

        # Bildirim veya rozet kontrolleri
        if result.get('is_correct', False):
            event_manager.trigger_event(EventType.QUESTION_SOLVED, {
                'user_id': submission.user_id,
                'question_id': submission.question_id
            })
            flash('Tebrikler! Çözümünüz doğru.', 'success')
        else:
            flash('Çözümünüzde hatalar var.', 'error')

        return redirect(url_for('programming.submission', id=submission.id))

    # Form doğrulama hatası kısmı
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", 'error')

    return redirect(url_for('programming.question', id=id))


@programming_bp.route('/submissions/<int:id>')
@login_required
def submission(id):
    """
    Bu fonksiyon belirtilen bir gönderimi yükler ve doğrular. Gönderim yalnızca, ilgili
    kullanıcıya aitse veya kullanıcının 'teacher' ya da 'admin' rolü varsa görüntülenebilir.

    Arguments:
        id: int
            Görüntülenmek istenen gönderimin ID değeri.

    Returns:
        TemplateResponse
            "Gönderim detayları" sayfası için bir şablon yanıt döndürür.

    Raises:
        NotFound
            Verilen ID ile eşleşen bir gönderim bulunamazsa, bir HTTP 404 Hatası oluşturur.
    """
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
    """
    Bir kullanıcının kendi gönderimlerini listeleyen bir rota işlevi.

    Kullanıcı oturumunu kontrol eder. Kullanıcının ID'sine göre veritabanındaki
    Submission modelinden ilgili gönderimleri alır ve gönderim tarihine göre sıralar.
    Listeyi HTML şablonuna göndererek sunar.

    Args:
        None

    Returns:
        flask.Response: HTML şablonu yanıtı ile birlikte döner.
    """
    submissions = Submission.query.filter_by(user_id=current_user.id) \
        .order_by(Submission.created_at.desc()).all()

    return render_template('my_submissions.html', submissions=submissions)


@programming_bp.route('/questions/<int:id>/evaluate', methods=['POST'])
@login_required
def evaluate_code(id):
    """
    Bu işlev, belirli bir soru için kullanıcının gönderdiği kodu değerlendirmek amacıyla
    CodeExecutionService kullanır. Multi-language desteği ile Python, R ve MATLAB kodlarını değerlendirir.

    Args:
        id (int): Değerlendirilecek sorunun benzersiz kimliği.

    Returns:
        flask.Response: Kod doğruluğu ve ilişkili sonuçları içeren JSON formatındaki yanıt. Olası
        durum kodları şunlardır:
            - 200: Kod başarıyla değerlendirildi ve sonuç döndü.
            - 400: Geçersiz form verileri gönderildi.
            - 500: Kod değerlendirme servisi geçici olarak kullanılamıyor.
    """
    question = ProgrammingQuestion.query.get_or_404(id)
    form = CodeEvaluationForm()

    # AJAX isteği için özel form doğrulama
    if request.is_json:
        json_data = request.get_json()
        form.code.data = json_data.get('code')

    if form.validate():
        code = form.code.data
        code_service = get_code_execution_service()

        try:
            # NEW: Use multi-language execution service
            result = code_service.execute_solution(
                language=question.language,
                code=code,
                function_name=question.function_name,
                test_inputs=question.test_inputs,
                solution_code=question.solution_code
            )

            return jsonify(result)

        except Exception as e:
            current_app.logger.error(f"Kod değerlendirme hatası: {str(e)}")
            return jsonify({
                "is_correct": False,
                "execution_time": 0,
                "test_count": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "errors": [f"Kod değerlendirme hatası: {str(e)}"]
            }), 500

    return jsonify({
        "is_correct": False,
        "execution_time": 0,
        "test_count": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "errors": ["Geçersiz form verileri"]
    }), 400