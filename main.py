from flask import *
from data import db_session
from data.users import User
from data.trades import Trade
from forms.user import RegisterForm, LoginForm, EditForm
from forms.trade import TradeForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    trades = db_sess.query(Trade).all()
    return render_template("index.html", trades=trades)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form,
                                   message="Пользователь с такой почтой уже есть")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', form=form,
                                   message="Пользователь с таким именем уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first() and form.email.data != current_user.email:
            return render_template('edit.html', form=form,
                                   message="Пользователь с такой почтой уже есть")
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        user.email = form.email.data
        user.about = form.about.data
        user.address = form.address.data
        db_sess.commit()
        return redirect(f'/profile/{current_user.name}')
    return render_template("edit.html", form=form)


@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    logout_user()
    db_sess.delete(user)
    db_sess.commit()
    return redirect("/")


@app.route("/profile/<name>")
def profile(name):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == name).first()
    return render_template("profile.html", user=user, created_date=user.created_date.date())


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', form=form)


@app.route('/trade/<int:id>')
def trades(id):
    db_sess = db_session.create_session()
    trade = db_sess.query(Trade).filter(Trade.id == id).first()
    return render_template('trade.html', trade=trade, created_date=trade.created_date.date())


@app.route('/add_trade', methods=['GET', 'POST'])
@login_required
def add_trade():
    form = TradeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        trade = Trade(
            item=form.item.data,
            description=form.description.data,
            seller_id=current_user.id,
            category=form.category.data,
            cost=form.cost.data
        )
        current_user.trades.append(trade)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('trade_bd.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    main()
