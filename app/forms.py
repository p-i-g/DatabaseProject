from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from flask import redirect, url_for, render_template, request, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import MySQLdb.cursors
from app import mysql, db
from app import models


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'id': 'loginEmail'})
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={'id': 'signupEmail'})
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Signup')


def login_helper(html, route, **kwargs):
    login_form = LoginForm()
    signup_form = SignupForm()
    if login_form.validate_on_submit():
        ajax = "_ajax" in request.form

        email = login_form.email.data
        password = login_form.password.data

        user = models.User.query.filter_by(email=email).first()

        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('select * from users where email = %s', (email,))
        #
        # user = cursor.fetchone()

        if user and check_password_hash(user.password, password):
            session['email'] = user.email
            session['username'] = user.username
            session['id'] = user.id
            session['logged_in'] = True

            if ajax:
                return ''

            return redirect(url_for(route))
        else:
            flash("Invalid email or password", 'danger')

            return render_template(html, login_form=login_form,
                                   signup_form=signup_form, modal='loginModal', invalid=True, page='route',
                                   session=session, **kwargs)
    return render_template(html, login_form=login_form,
                           signup_form=signup_form, modal='loginModal', page='route', session=session, **kwargs)


def signup_helper(html, route, **kwargs):
    login_form = LoginForm()
    signup_form = SignupForm()
    if signup_form.validate_on_submit():
        ajax = "_ajax" in request.form

        email = signup_form.email.data
        username = signup_form.username.data
        password = signup_form.password.data

        user = models.User.query.filter_by(email=email).first()

        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute('select * from users where email = %s', (email,))
        #
        # user = cursor.fetchone()

        if user:
            flash("User already exists!")
            return render_template(html, login_form=login_form,
                                   signup_form=signup_form, modal='signupModal', invalid=True, page='route', **kwargs)
        else:

            if ajax:
                return ''
            db.session.add(models.User(email=email, username=username, password=generate_password_hash(password)))
            db.session.commit()

            return redirect(url_for(route))

    return render_template(html, login_form=login_form,
                           signup_form=signup_form, modal='signupModal', page='route', **kwargs)
