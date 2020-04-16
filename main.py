from flask_login import LoginManager, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, TextField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email
from flask import Flask, render_template, redirect, request, abort
from data import db_session
from data.users import User
from wtforms.fields.html5 import EmailField
from flask_login import current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class EventsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')



class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


@app.route('/')
def default():
    if current_user.is_authenticated:
        events = session.query(Events).filter(
            (Events.user == current_user) | (Events.is_private != True))
    else:
        events = session.query(Events).filter(Events.is_private != True)
    return render_template('index.html', title='Главная страница')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
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


@app.route('/funkshion')
def funkshion():
    return render_template('funkshion.html', title='Функционал')


@app.route('/whoisthis')
def whoisthis():
    return render_template('whoisthis.html', title='Функционал')


@app.route('/evebts',  methods=['GET', 'POST'])
@login_required
def add_events():
    form = EventsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        events = Events()
        events.title = form.title.data
        events.content = form.content.data
        events.is_private = form.is_private.data
        current_user.events.append(events)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('events.html', title='Добавление новости',
                           form=form)


@app.route('/events/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_events(id):
    form = EventsForm()
    if request.method == "GET":
        session = db_session.create_session()
        events = session.query(Events).filter(Events.id == id,
                                          Events.user == current_user).first()
        if events:
            form.title.data = events.title
            form.content.data = events.content
            form.is_private.data = events.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        session = db_session.create_session()
        events = session.query(Events).filter(Events.id == id,
                                          Events.user == current_user).first()
        if events:
            events.title = form.title.data
            events.content = form.content.data
            events.is_private = form.is_private.data
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('events.html', title='Редактирование события', form=form)


@login_required
def news_delete(id):
    session = db_session.create_session()
    events = session.query(Events).filter(Events.id == id,
                                      Events.user == current_user).first()
    if events:
        session.delete(events)
        session.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    global session
    db_session.global_init("db/blogs.sqlite")
    session = db_session.create_session()
    app.run(port=8080, host='127.0.0.1')
