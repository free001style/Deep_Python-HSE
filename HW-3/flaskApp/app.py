import sqlite3
import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

AUTH_DATABASE = '/tmp/auth.db'
DEBUG = True
SECRET_KEY = 'gnreinoircnoidsmcoewfo9089kfenwkocn'

# db_lp = sqlite3.connect('auth.db')
# cursor_db = db_lp.cursor()
# sql_create = '''CREATE TABLE passwords(
# login TEXT PRIMARY KEY,
# password TEXT NOT NULL);'''
#
# cursor_db.execute(sql_create)
# db_lp.commit()
#
# cursor_db.close()
# db_lp.close()


app.config.update(dict(
    AUTH_DATABASE=os.path.join(app.root_path, 'auth.db'),
    DEBUG=True,
    SECRET_KEY='gnreinoircnoidsmcoewfo9089kfenwkocn'))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# def connect_db(db: str):
#     """Соединяет с указанной базой данных."""
#     rv = sqlite3.connect(
#         app.config[db])  # внутри конфигураций надо будет указать БД, в которую мы будем все хранить
#     rv.row_factory = sqlite3.Row  # инстанс для итерации по строчкам (может брать по строке и выдавать)
#     return rv
#
#
# def get_db(db: str):
#     """Если ещё нет соединения с базой данных, открыть новое - для текущего контекста приложения"""
#     if not hasattr(g, 'sqlite_db'):  # g - это наша глобальная переменная, являющасяс объектом отрисовки
#         g.sqlite_db = connect_db('AUTH_DATABASE')
#     return g.sqlite_db
#
#
# @app.teardown_appcontext  # декоратор при разрыве connection
# def close_db(error):  # закрытие может проходить как нормально, так и с ошибкой, которую можно обрабатывать
#     """Закрываем БД при разрыве"""
#     if hasattr(g, 'sqlite_db'):
#         g.sqlite_db.close()
#
#
# def init_db(db: str):
#     """Инициализируем наше БД"""
#     with app.app_context():  # внутри app_context app и g связаны
#         db = get_db('AUTH_DATABASE')
#         with app.open_resource('schema.sql', mode='r') as f:
#             db.cursor().executescript(f.read())
#         db.commit()


@app.route('/')
def hello_page():
    return render_template("layout.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        Login = request.form.get('Login')
        Password = request.form.get('Password')

        db_lp = sqlite3.connect('auth.db')
        cursor_db = db_lp.cursor()
        cursor_db.execute(('''SELECT password FROM passwords WHERE login = '{}';''').format(Login))
        pas = cursor_db.fetchall()

        cursor_db.close()
        try:
            if pas[0][0] != Password:
                return render_template('auth_bad.html')
        except:
            return render_template('auth_bad.html')

        db_lp.close()
        session['logged_in'] = True
        return render_template('successful_auth.html')

    return render_template('authorization.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        Login = request.form.get('Login')
        Password = request.form.get('Password')

        db_lp = sqlite3.connect('auth.db')
        cursor_db = db_lp.cursor()
        sql_insert = '''INSERT INTO passwords VALUES('{}','{}');'''.format(Login, Password)
        cursor_db.execute(sql_insert)

        cursor_db.close()

        db_lp.commit()
        db_lp.close()

        return render_template('successful_regis.html')

    return render_template('registration.html')


if __name__ == "__main__":
    # init_db('AUTH_DATABASE')
    app.run()
