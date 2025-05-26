# app/forms/programming.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length

class ProgrammingQuestionForm(FlaskForm):
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
    code = TextAreaField('Kod', validators=[DataRequired()])
    submit = SubmitField('Çözümü Gönder')

class CodeEvaluationForm(FlaskForm):
    code = TextAreaField('Kod', validators=[DataRequired()])
    submit = SubmitField('Test Et')