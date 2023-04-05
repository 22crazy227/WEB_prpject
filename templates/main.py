import os

from flask import Flask, render_template, redirect, request, make_response, session, abort, jsonify, Blueprint
from flask_uploads import UploadSet, IMAGES
from werkzeug.utils import secure_filename

from data.products import Products
from data.users import User
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from forms.product import ProductForm
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

def main():
    db_session.global_init("db/shop.db")
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    products = db_sess.query(Products).all()
    return render_template("index.html", products=products, title="Главное Меню")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/product',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = ProductForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = Products()
        product.title = form.title.data
        product.content = form.content.data
        product.coast = form.coast.data
        current_user.product.append(product)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('product.html', title='Добавление товар',
                           form=form)


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Products).filter(Products.id == id,
                                      Products.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = ProductForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        product = db_sess.query(Products).filter(Products.id == id,
                                          Products.user == current_user
                                          ).first()
        if product:
            form.title.data = product.title
            form.content.data = product.content
            form.coast.data = product.coast
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        product = db_sess.query(Products).filter(Products.id == id,
                                          Products.user == current_user
                                          ).first()
        if product:
            product.title = form.title.data
            product.content = form.content.data
            product.coast = form.coast.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('product.html',
                           title='Редактирование новости',
                           form=form
                           )


if __name__ == '__main__':
    main()
