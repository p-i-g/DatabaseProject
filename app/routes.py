import requests
from flask_paginate import Pagination, get_page_parameter, get_per_page_parameter
from app.forms import *
from app import app
from flask import g


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


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('profile.html', 'profile')
        elif 'Signup' in request.form.values():
            return signup_helper('profile.html', 'profile')
    login_form = LoginForm()
    signup_form = SignupForm()
    profile_form = SignupForm()
    success = False

    if profile_form.validate_on_submit():
        email = profile_form.email.data
        username = profile_form.username.data
        password = profile_form.password.data

        user = models.User.query.filter_by(id=session['id']).first()

        user.email = email
        user.username = username
        user.password = generate_password_hash(password)

        print(user.email, user.username, user.password)

        db.session.commit()

        success = True

    return render_template('profile.html', login_form=login_form, signup_form=signup_form, page='profile',
                           session=session, profile_form=profile_form, success=success)


@app.route('/database', methods=['GET', 'POST'])
def database():
    page = request.args.get(get_page_parameter(), 1, int)
    per_page = request.args.get(get_per_page_parameter(), 20, int)

    if 'database' not in session or request.method == 'POST' and 'field' in request.form:
        field = request.form.get('field', '')
        search = request.form.get('search', '')
        session['database'] = {
            'field': field,
            'search': search
        }
    else:
        field = session['database']['field']
        search = session['database']['search']

    if field == 'Search In: Act Name':
        result = models.Section.query.filter(models.Section.name.like(f'%%{search}%%'))
    elif field == 'Search In: Section Number':
        result = models.Section.query.filter(models.Section.section_id.like(f'%%{search}%%'))
    elif field == 'Search In: Text':
        result = models.Section.query.filter(models.Section.text.like(f'%%{search}%%'))
    else:
        result = models.Section.query

    result = result.order_by(models.Section.name, models.Section.section_id)

    count = result.count()
    sections = result.paginate(page=page, per_page=per_page)

    pagination = Pagination(page=page, per_page=per_page, bs_version=5, total=count,
                            alignment='right')

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('database.html', 'database', pagination=pagination, sections=sections.items,
                                length=len(sections.items))
        elif 'Signup' in request.form.values():
            return signup_helper('database.html', 'database', pagination=pagination, sections=sections.items,
                                 length=len(sections.items))
        elif 'search' in request.form:
            print(request.form['search'], request.form['field'])

    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('database.html', login_form=login_form, signup_form=signup_form, page='database',
                           session=session, pagination=pagination, sections=sections.items, length=len(sections.items))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/database/section_content/<act_name>/<section_no>')
def section_content(act_name, section_no):
    res = models.Section.query.filter_by(name=act_name, section_id=section_no).first()

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('section_content.html', 'section_content', section=res)
        elif 'Signup' in request.form.values():
            return signup_helper('section_content.html', 'section_content', section=res)
    login_form = LoginForm()
    signup_form = SignupForm()

    print(request.path)

    return render_template('section_content.html', login_form=login_form, signup_form=signup_form, page='index',
                           session=session, section=res)
