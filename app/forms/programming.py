# app/forms/programming.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class ProgrammingQuestionForm(FlaskForm):
    """
    Bir form sınıfı olup, programlama soruları oluşturmak için kullanılır.

    Bu form sınıfı, bir programlama sorusuna ait temel bilgileri toplar ve doğrulama
    kontrolleri sağlar. FlaskForm'dan türetilmiştir ve Flask uygulamalarında form
    işlemlerini kolaylaştırır.

    Attributes:
        title (StringField): Sorunun başlığını belirten metin alanı.
        description (TextAreaField): Sorunun açıklamasını içeren metin alanı.
        difficulty (SelectField): Sorunun zorluk seviyesini belirtmek için seçim
            yapılabilir alan.
        points (IntegerField): Sorunun puan değerini içeren sayı alanı.
        topic (SelectField): Soruyla ilişkili konuyu belirten seçim alanı.
        example_input (TextAreaField): Sorunun örnek girdisini içeren metin alanı.
        example_output (TextAreaField): Sorunun örnek çıktısını içeren metin alanı.
        function_name (StringField): Soruda ilgili fonksiyonun adını içeren metin
            alanı.
        solution_code (TextAreaField): Sorunun çözüm kodunu içeren metin alanı.
        test_inputs (TextAreaField): Sorunun test girdilerini içeren metin alanı;
            belirtilen formatta veri girişi beklenir.
        submit (SubmitField): Formu kaydetmek için kullanılan düğme.
    """
    title = StringField('Soru Başlığı', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Soru Açıklaması', validators=[DataRequired()])
    difficulty = SelectField('Zorluk Seviyesi',
                          choices=[(1, 'Kolay'), (2, 'Orta'), (3, 'Zor'), (4, 'Çok-Zor')],
                          coerce=int,
                          validators=[DataRequired()])
    points = IntegerField('Puan', validators=[DataRequired(), NumberRange(min=1)])
    topic = SelectField('Konu',
                        validators=[DataRequired()],
                        choices=[
                            ('veri yapıları', 'Veri Yapıları'),
                            ('algoritmalar', 'Algoritmalar'),
                            ('string işleme', 'String İşleme'),
                            ('matematik', 'Matematik'),
                            ('sayı teorisi', 'Sayı Teorisi'),
                            ('arama', 'Arama'),
                            ('sıralama', 'Sıralama'),
                            ('dinamik programlama', 'Dinamik Programlama'),
                            ('graf teorisi', 'Graf Teorisi'),
                            ('olasılık', 'Olasılık'),
                            ('istatistik', 'İstatistik')
                        ])
    example_input = TextAreaField('Örnek Girdi')
    example_output = TextAreaField('Örnek Çıktı')
    function_name = StringField('Fonksiyon Adı', validators=[DataRequired(), Length(max=100)])
    solution_code = TextAreaField('Admin Çözüm Kodu', validators=[DataRequired()])
    test_inputs = TextAreaField('Test Girdileri',
                             description='[[arg1, arg2,...], [arg1, arg2,...], ...] formatında 10 test girdisini girin',
                             validators=[DataRequired()])
    submit = SubmitField('Kaydet')

class SolutionSubmitForm(FlaskForm):
    """
    SolutionSubmitForm sınıfı, bir form nesnesidir.

    Bu sınıf, FlaskForm'dan türetilmiştir ve bir kod çözümü göndermek için kullanılan
    formun tanımını içerir. Form iki ana alan içerir: 'code' ve 'submit'. Kullanıcı kod
    alanına çözümünü yazdıktan sonra 'submit' butonuna basarak gönderim sağlar.
    """
    code = TextAreaField('Kod', validators=[DataRequired()])
    submit = SubmitField('Çözümü Gönder')

class CodeEvaluationForm(FlaskForm):
    """
    Kod değerlendirme formu oluşturur.

    Bu form, bir kodu değerlendirmek ve test etmek amacıyla bir metin alanı
    ve bir gönderme düğmesi sağlar. FlaskForm sınıfından türetilmiştir ve
    validation işlemleri içerir.
    """
    code = TextAreaField('Kod', validators=[DataRequired()])
    submit = SubmitField('Test Et')