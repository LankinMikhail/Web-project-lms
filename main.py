import os
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
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # разрешённые форматы файлов


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    path = os.path.join("db")
    if not os.path.exists(path):
        os.mkdir(path)
    db_session.global_init("db/blogs.db")
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    trades = db_sess.query(Trade).all()
    return render_template("index.html", trades=trades)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        user = User()
        user.name = form.name.data
        user.email = form.email.data
        user.about = form.about.data
        user.address = form.address.data
        user.is_address_visible = bool(form.is_address_visible)
        user.is_email_visible = bool(form.is_email_visible)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            form.address.data = user.address
            form.email.data = user.email
            form.about.data = user.about
            form.is_email_visible.data = user.is_email_visible
            form.is_address_visible.data = user.is_address_visible
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if (db_sess.query(User).filter(User.email == form.email.data).first() and
                form.email.data != current_user.email):
            return render_template('edit.html', form=form,
                                   message="Пользователь с такой почтой уже есть")
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if user:
            user.email = form.email.data
            user.about = form.about.data
            user.address = form.address.data
            user.is_email_visible = form.is_email_visible.data
            user.is_address_visible = form.is_address_visible.data
            file = request.files["avatar"]
            if file and allowed_file(file.filename):
                path = os.path.join("static/img/avatars")
                if not os.path.exists(path):
                    os.mkdir(path)
                if os.path.exists(f"{path}/{current_user.name}"):
                    os.remove(f"{path}/{current_user.name}")
                file.save(f"{path}/{current_user.name}")
            db_sess.commit()
            return redirect(f'/profile/{current_user.name}')
        else:
            abort(404)
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
    return render_template("profile.html", user=user,
                           created_date=user.created_date.date(),
                           avatar_exists=os.path.exists(f"static/img/avatars/{user.name}"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль", form=form)
    return render_template('login.html', form=form)


@app.route('/trade/<int:id>')
def trade(id):
    db_sess = db_session.create_session()
    trade = db_sess.query(Trade).filter(Trade.id == id).first()
    return render_template('trade.html',
                           trade=trade, created_date=trade.created_date.date(),
                           image_exists=os.path.exists(f"static/img/trades/{trade.id}"))


@app.route('/add_trade', methods=['GET', 'POST'])
@login_required
def add_trade():
    form = TradeForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        trade = Trade()
        trade.item = form.item.data
        trade.description = form.description.data
        trade.seller_id = current_user.id
        trade.category = form.category.data
        trade.cost = form.cost.data
        if form.cost.data <= 0:
            return render_template('trade_bd.html', form=form,
                                   title="Добавление товара", message="Цена может быть только положительной")
        current_user.trades.append(trade)
        db_sess.merge(current_user)
        db_sess.commit()
        file = request.files["image"]
        if file and allowed_file(file.filename):
            path = os.path.join("static/img/trades")
            if not os.path.exists(path):
                os.mkdir(path)
            if os.path.exists(f"{path}/{trade.id}"):
                os.remove(f"{path}/{trade.id}")
            file.save(f"{path}/{trade.id}")
        return redirect('/')
    return render_template('trade_bd.html',
                           form=form, title="Добавление товара")


@app.route('/edit_trade/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_trade(id):
    form = TradeForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        trade = db_sess.query(Trade).filter(Trade.id == id,
                                            Trade.seller_id == current_user.id).first()
        if trade:
            form.item.data = trade.item
            form.description.data = trade.description
            form.category.data = trade.category
            form.cost.data = trade.cost
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        trade = db_sess.query(Trade).filter(Trade.id == id,
                                            Trade.seller_id == current_user.id).first()
        if trade:
            trade.item = form.item.data
            trade.description = form.description.data
            trade.seller_id = current_user.id
            trade.category = form.category.data
            trade.cost = form.cost.data
            if form.cost.data <= 0:
                return render_template('trade_bd.html', form=form,
                                       title="Добавление товара", message="Цена может быть только положительной")
            file = request.files["image"]
            if file and allowed_file(file.filename):
                path = os.path.join("static/img/trades")
                if not os.path.exists(path):
                    os.mkdir(path)
                if os.path.exists(f"{path}/{trade.id}"):
                    os.remove(f"{path}/{trade.id}")
                file.save(f"{path}/{trade.id}")
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('trade_bd.html', form=form, title="Изменение товара")


@app.route('/delete_trade/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_trade(id):
    db_sess = db_session.create_session()
    trade = db_sess.query(Trade).filter(Trade.id == id,
                                        Trade.seller_id == current_user.id).first()
    if trade:
        db_sess.delete(trade)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


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
