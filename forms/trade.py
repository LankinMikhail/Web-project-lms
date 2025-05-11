import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class TradeForm(FlaskForm):
    item = StringField("Товар", validators=[DataRequired()])
    description = TextAreaField("Описание")
    category = SelectField("Категория", choices=[("Другое", "Другое"), ("Услуга", "Услуга"),
                                                 ("Одежда", "Одежда"), ("Техника", "Техника"), ], default="Другое")
    cost = IntegerField("Цена", validators=[DataRequired()])
    image = FileField("Загрузите изображение")
    submit = SubmitField('Применить')
