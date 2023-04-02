from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_mysqldb import MySQL
from flask_modals import Modal
from werkzeug.security import check_password_hash, generate_password_hash
import MySQLdb.cursors
import os
from forms import *

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'adminadmin'
app.config['MYSQL_DB'] = 'project'

app.secret_key = os.urandom(24)

mysql = MySQL(app)
modal = Modal(app)


@app.route('/', methods=['GET', 'POST'])
def index():  # put application's code here
    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('index.html', 'index')
        elif 'Signup' in request.form.values():
            return signup_helper('index.html', 'index')
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('index.html', login_form=login_form, signup_form=signup_form, page='index', session=session)


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('feedback.html', 'feedback')
        elif 'Signup' in request.form.values():
            return signup_helper('feedback.html', 'feedback')
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('feedback.html', login_form=login_form, signup_form=signup_form, page='feedback',
                           session=session)


@app.route('/database', methods=['GET', 'POST'])
def database():
    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('database.html', 'database')
        elif 'Signup' in request.form.values():
            return signup_helper('database.html', 'database')
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('database.html', login_form=login_form, signup_form=signup_form, page='database',
                           session=session)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_helper(html, route):
    login_form = LoginForm()
    signup_form = SignupForm()
    if login_form.validate_on_submit():
        ajax = "_ajax" in request.form

        email = login_form.email.data
        password = login_form.password.data

        print(email, password)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from users where email = %s', (email,))

        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['email'] = user['email']
            session['username'] = user['username']
            session['id'] = user['id']
            session['logged_in'] = True

            if ajax:
                return ''

            return redirect(url_for(route))
        else:
            flash("Invalid email or password", 'danger')

            return render_template(html, login_form=login_form,
                                   signup_form=signup_form, modal='loginModal', invalid=True, page='route',
                                   session=session)
    return render_template(html, login_form=login_form,
                           signup_form=signup_form, modal='loginModal', page='route', session=session)


def signup_helper(html, route):
    login_form = LoginForm()
    signup_form = SignupForm()
    if signup_form.validate_on_submit():
        ajax = "_ajax" in request.form

        email = signup_form.email.data
        username = signup_form.username.data
        password = signup_form.password.data

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('select * from users where email = %s', (email,))

        user = cursor.fetchone()

        if user:
            return render_template(html, login_form=login_form,
                                   signup_form=signup_form, modal='signupModal', invalid=True, page='route')
        else:

            if ajax:
                return ''
            cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s)',
                           (email, username, generate_password_hash(password)))
            mysql.connection.commit()

            return redirect(url_for(route))

    return render_template(html, login_form=login_form,
                           signup_form=signup_form, modal='signupModal', page='route')


if __name__ == '__main__':
    app.run(debug=True)
