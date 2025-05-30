from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired


class BadgeForm(FlaskForm):
    """BadgeForm, bir form sınıfıdır ve genellikle kullanıcıdan belirli bilgileri
    toplamak için kullanılır.

    Bu sınıf, belirli rozet bilgilerini almak veya işlemek için oluşturulmuştur.
    Flask-WTF paketine dayanır ve çeşitli alanlardan oluşur. Her alan için belirli
    validasyon kuralları belirlenmiştir, böylece doğru ve eksiksiz bilgi girişi
    sağlanabilir.
    """
    name = StringField('Badge Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    icon = HiddenField('Icon', validators=[DataRequired()])
    color = HiddenField('Color', validators=[DataRequired()])
    criteria_type = StringField('Criteria Type', validators=[DataRequired()])
    criteria_value = StringField('Criteria Value', validators=[DataRequired()])
    submit = SubmitField('Save Badge')