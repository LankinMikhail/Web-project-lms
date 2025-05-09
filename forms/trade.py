import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class TradeForm(FlaskForm):
    item = StringField("Товар", validators=[DataRequired()])
    description = TextAreaField("Описание")
    seller = StringField("Продавец", validators=[DataRequired()])
    category = SelectField("Категория", default="Другое")
    cost = IntegerField("Цена", validators=[DataRequired()])
    submit = SubmitField('Применить')
