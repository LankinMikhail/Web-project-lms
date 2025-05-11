from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, FileField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    is_email_visible = BooleanField('Всем видно почту')
    address = StringField("Адрес")
    is_address_visible = BooleanField('Всем видно адрес')
    about = TextAreaField("Немного о себе")
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EditForm(FlaskForm):
    address = StringField("Адрес")
    is_address_visible = BooleanField('Всем видно адрес')
    email = EmailField('Почта', validators=[DataRequired()])
    is_email_visible = BooleanField('Всем видно почту')
    about = TextAreaField("Немного о себе")
    avatar = FileField("Загрузите аватар")
    submit = SubmitField('Изменить')
