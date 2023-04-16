import setuptools.package_index
from flask import redirect, url_for, render_template, request, session, flash
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import StringField, PasswordField, SubmitField, validators, DateField, TextAreaField
from wtforms.fields import SelectField
from wtforms.validators import DataRequired, Email, ValidationError

from app import db
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
                                   signup_form=signup_form, modal='signupModal', invalid=True, page='route',
                                   session=session, **kwargs)
        else:

            if ajax:
                return ''
            db.session.add(models.User(email=email, username=username, password=generate_password_hash(password)))
            db.session.commit()

            return redirect(url_for(route))

    return render_template(html, login_form=login_form,
                           signup_form=signup_form, modal='signupModal', page='route', session=session, **kwargs)


class DatabaseSearchForm(FlaskForm):
    searchable_tables = {
        'Search for: Act': models.Act,
        'Search for: Section': models.Section,
        'Search for: Firm': models.Firm,
        'Search for: Judge': models.Judge,
        'Search for: Lawyer': models.Lawyer,
        'Search for: Court': models.Court,
        'Search for: Case': models.Case
    }
    opts = [(x, x) for x in searchable_tables.keys()]

    search_in = SelectField('search_in', choices=opts)
    kw = StringField('kw')
    submit = SubmitField('search')


class PrimaryKeyValidator:
    def __init__(self, model):
        self.model = model

    def __call__(self, form, field):
        if self.model.check_key_constraint(field.data):
            raise ValidationError("Entity already exists in database.")


class UnmodifiedValidator:
    def __init__(self, init_value):
        self.init_value = init_value

    def __call__(self, form, field):
        if field.data != self.init_value:
            raise ValidationError("Do not modify this field.")


class EditActForm(FlaskForm):
    name = StringField('Name')
    last_ammend_date = DateField('Last Amend Date', validators=[validators.DataRequired()])
    title = StringField('Title', validators=[validators.DataRequired(), validators.Length(max=1023)])
    commence_date = DateField('Commencement Date', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')

    def __init__(self, edit, act_name=None, *args, **kwargs):
        super(EditActForm, self).__init__(*args, **kwargs)

        if edit:
            self.name.validators = [validators.DataRequired(), UnmodifiedValidator(init_value=act_name),
                                    validators.Length(max=255)]
            self.name.render_kw = {'readonly': True}
        else:
            self.name.validators = [validators.DataRequired(), PrimaryKeyValidator(models.Act)]
            del self.delete

def section_pk_validator(form, field):  # noqa because wtforms wants it in this format
    if models.Section.query.filter((models.Section.name == form.name.data) &
                                   (models.Section.section_id == form.section_id.data)).first():
        raise ValidationError("Entity already exists in database.")


class EditSectionForm(FlaskForm):
    name = SelectField('Act Name')
    section_id = StringField('Section ID')
    last_ammend_date = DateField('Last Amend Date', validators=[validators.DataRequired()])
    text = TextAreaField('Text', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')
    delete = SubmitField('Delete')

    def __init__(self, edit, act_name=None, section_id_init=None, *args, **kwargs):
        super(FlaskForm, self).__init__(*args, **kwargs)
        self.name.render_kw = {'data-live-search': "true", 'data-style': 'btn-secondary btn-block', 'data-width': '100%'}
        self.name.choices = [(act.name, act.name) for act in models.Act.query.all()]

        if edit:
            self.name.render_kw.update({'readonly': True, 'disabled': True})
            self.name.validators = [validators.DataRequired(), UnmodifiedValidator(act_name)]
            self.section_id.render_kw = {'readonly': True}
            self.section_id.validators = [validators.DataRequired(), UnmodifiedValidator(section_id_init), validators.Length(max=15)]
        else:
            self.name.validators = [validators.DataRequired(), section_pk_validator]
            self.section_id.validators = [validators.DataRequired(), section_pk_validator, validators.Length(max=15)]
            del self.delete


class AddCaseForm(FlaskForm):
    old_case = SelectField('old_case', )
