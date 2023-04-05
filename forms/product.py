from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileField
from wtforms import StringField, TextAreaField
from wtforms import SubmitField, IntegerField
from wtforms.validators import DataRequired


class ProductForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    coast = IntegerField("Цена")
    submit = SubmitField('Добавить')
