import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class TradeForm(FlaskForm):
    item = StringField("Товарище", validators=[DataRequired()])
    description = TextAreaField("Содержаньеще")
    seller = StringField("Продавец", validators=[DataRequired()])
    category = SelectField("Категория", default="без категории")
    cost = IntegerField("Цена", validators=[DataRequired()])
    submit = SubmitField('Применить')
