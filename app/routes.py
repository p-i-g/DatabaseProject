from flask import g, jsonify
from flask_paginate import Pagination, get_page_parameter, get_per_page_parameter

from app import app
from app.forms import *


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

        db.session.commit()

        success = True

    return render_template('profile.html', login_form=login_form, signup_form=signup_form, page='profile',
                           session=session, profile_form=profile_form, success=success)


@app.route('/database', methods=['GET', 'POST'])
def database():
    edit_urls = {
        'Search for: Act': 'edit_act',
        'Search for: Section': 'edit_section',
    }
    page = request.args.get(get_page_parameter(), 1, int)
    per_page = request.args.get(get_per_page_parameter(), 20, int)
    database_form = DatabaseSearchForm()

    if 'database' not in session or request.method == 'POST':

        cls = database_form.search_in.data or 'Search for: Act'

        kw = database_form.kw.data
        kw = kw if kw else ''
        session['database'] = {
            'cls': cls,
            'kw': kw
        }
    else:
        cls = session['database']['cls']
        kw = session['database']['kw']

    edit_url = edit_urls.get(cls, '')
    cls = database_form.searchable_tables[cls]

    result = cls.search(kw)

    # result = result.order_by(models.Section.name, models.Section.section_id)

    count = result.count()
    sections = result.paginate(page=page, per_page=per_page)

    pagination = Pagination(page=page, per_page=per_page, bs_version=5, total=count,
                            alignment='right')

    table = cls.render_table(sections)

    g.pop('details', None)

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('database.html', 'database', pagination=pagination, sections=sections.items,
                                length=len(sections.items))
        elif 'Signup' in request.form.values():
            return signup_helper('database.html', 'database', pagination=pagination, sections=sections.items,
                                 length=len(sections.items))

    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('database.html', login_form=login_form, signup_form=signup_form, page='database',
                           session=session, pagination=pagination, sections=sections.items, length=len(sections.items),
                           database_form=database_form, table=table, edit_url=edit_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/database/section_details/<act_name>/<section_no>')
def section_details(act_name, section_no):
    res = models.Section.query.filter_by(name=act_name, section_id=section_no).first()

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('section_details.html', 'section_details', section=res)
        elif 'Signup' in request.form.values():
            return signup_helper('section_details.html', 'section_details', section=res)
    login_form = LoginForm()
    signup_form = SignupForm()

    return render_template('section_details.html', login_form=login_form, signup_form=signup_form,
                           session=session, section=res)


@app.route('/database/act_details/<act_name>')
def act_details(act_name):
    act, sections = models.Act.get_details(act_name)

    page = request.args.get(get_page_parameter(), 1, int)
    per_page = request.args.get(get_per_page_parameter(), 20, int)
    count = sections.count()
    sections = sections.paginate(page=page, per_page=per_page)

    pagination = Pagination(page=page, per_page=per_page, bs_version=5, total=count,
                            alignment='right')

    table = models.Section.render_table(sections)

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('act_details.html', 'act_details', act=act, section_table=table, pagination=pagination)
        elif 'Signup' in request.form.values():
            return signup_helper('act_details.html', 'act_details', act=act, section_table=table, pagination=pagination)
    login_form = LoginForm()
    signup_form = SignupForm()

    return render_template('act_details.html', login_form=login_form, signup_form=signup_form, act=act,
                           section_table=table, pagination=pagination)


@app.route('/database/firm_details/<firm_id>')
def firm_details(firm_id):
    firm, specs, lawyers = models.Firm.get_details(firm_id)

    specs_table = models.FirmSpec.render_list(specs)
    lawyers_table = models.Lawyer.render_table(lawyers)

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('firm_details.html', 'firm_details', specs_table=specs_table, firm=firm,
                                lawyers_table=lawyers_table)
        elif 'Signup' in request.form.values():
            return signup_helper('firm_details.html', 'firm_details', specs_table=specs_table, firm=firm,
                                 lawyers_table=lawyers_table)
    login_form = LoginForm()
    signup_form = SignupForm()

    return render_template('firm_details.html', login_form=login_form, signup_form=signup_form, specs_table=specs_table,
                           firm=firm, lawyers_table=lawyers_table, session=session)


@app.route('/database/judge_details/<judge_id>')
def judge_details(judge_id):
    judge, cases = models.Judge.get_details(judge_id)

    case_table = models.Case.render_list(cases)

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('judge_details.html', 'judge_details', judge=judge, cases_table=case_table)
        elif 'Signup' in request.form.values():
            return signup_helper('judge_details.html', 'judge_details', judge=judge, cases_table=case_table)
    login_form = LoginForm()
    signup_form = SignupForm()

    return render_template('judge_details.html', login_form=login_form, signup_form=signup_form, judge=judge,
                           cases_table=case_table, session=session)


@app.route('/database/court_details/<court_id>')
def court_details(court_id):
    court, cases = models.Court.get_details(court_id)

    case_table = models.Case.render_list(cases)

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('court_details.html', 'court_details', court=court, cases_table=case_table)
        elif 'Signup' in request.form.values():
            return signup_helper('court_details.html', 'court_details', court=court, cases_table=case_table)
    login_form = LoginForm()
    signup_form = SignupForm()

    return render_template('court_details.html', login_form=login_form, signup_form=signup_form, court=court,
                           cases_table=case_table, session=session)


@app.route('/database/lawyer_details/<lawyer_id>')
def lawyer_details(lawyer_id):
    lawyer, cases, firms = models.Lawyer.get_details(lawyer_id)

    case_table = models.Case.render_list(cases)
    firms_list = models.Firm.render_list(firms)

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('lawyer_details.html', 'lawyer_details', lawyer=lawyer, cases_table=case_table,
                                firms_list=firms_list)
        elif 'Signup' in request.form.values():
            return signup_helper('lawyer_details.html', 'lawyer_details', lawyer=lawyer, cases_table=case_table,
                                 firms_list=firms_list)
    login_form = LoginForm()
    signup_form = SignupForm()

    return render_template('lawyer_details.html', login_form=login_form, signup_form=signup_form, lawyer=lawyer,
                           cases_table=case_table, firms_list=firms_list, session=session)


@app.route('/database/case_details/<case_id>')
def case_details(case_id):
    case, sections, lawyers, judges, fields, cases = models.Case.get_details(case_id)

    sections_table = models.Section.render_table(sections)
    lawyers_table = models.Lawyer.render_table(lawyers)
    judges_list = models.Judge.render_list(judges)
    fields_list = models.CaseField.render_list(fields)
    case_table = models.Case.render_list(cases)

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('case_details.html', 'case_details', case=case, cases_table=case_table,
                                lawyers_table=lawyers_table, sections_table=sections_table, judges_list=judges_list,
                                fields_list=fields_list)
        elif 'Signup' in request.form.values():
            return signup_helper('case_details.html', 'case_details', case=case, cases_table=case_table,
                                 lawyers_table=lawyers_table, sections_table=sections_table, judges_list=judges_list,
                                 fields_list=fields_list)
    login_form = LoginForm()
    signup_form = SignupForm()

    return render_template('case_details.html', login_form=login_form, signup_form=signup_form, case=case,
                           cases_table=case_table, lawyers_table=lawyers_table, sections_table=sections_table,
                           judges_list=judges_list, fields_list=fields_list, session=session)


@app.route('/edit_act', methods=['GET', 'POST'])
@app.route('/edit_act/<act_name>', methods=['GET', 'POST'])
def edit_act(act_name=None):
    edit = act_name is not None

    if edit:
        act, _ = models.Act.get_details(act_name)
        edit_act_form = EditActForm(
            edit=edit,
            act_name=act.name,
            formdata=request.form,
            name=act.name,
            last_ammend_date=act.last_ammend_date,
            title=act.title,
            commence_date=act.commence_date,
        )

    else:
        edit_act_form = EditActForm(edit=edit, formdata=request.form)

    if edit_act_form.validate_on_submit():
        if 'delete' in request.form and request.form['delete']:
            db.session.delete(act)  # noqa the linter is not smart enough
            db.session.commit()
        elif edit:
            act.last_ammend_date = edit_act_form.last_ammend_date.data  # noqa the linter is not smart enough
            act.title = edit_act_form.title.data
            act.commence_date = edit_act_form.commence_date.data

            db.session.commit()
        else:
            act = models.Act(name=edit_act_form.name.data,
                             last_ammend_date=edit_act_form.last_ammend_date.data,
                             title=edit_act_form.title.data,
                             commence_date=edit_act_form.commence_date.data)
            db.session.add(act)
            db.session.commit()

        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('edit_act.html', 'edit_act')
        elif 'Signup' in request.form.values():
            return signup_helper('edit_act.html', 'edit_act')
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('edit_act.html', login_form=login_form, signup_form=signup_form, page='index',
                           edit_act_form=edit_act_form, session=session, act_name=act_name)


@app.route('/edit_section', methods=['GET', 'POST'])
@app.route('/edit_section/<act_name>/<section_id>', methods=['GET', 'POST'])
def edit_section(act_name=None, section_id=None):
    edit = act_name is not None

    if edit:
        section = models.Section.query.filter(models.Section.section_id == section_id,
                                              models.Section.name == act_name).first_or_404()
        edit_section_form = EditSectionForm(
            edit=edit,
            act_name=section.name,
            section_id_init=section.section_id,
            formdata=request.form,
            name=section.name,
            section_id=section_id,
            last_ammend_date=section.last_ammend_date,
            text=section.text
        )

    else:
        print(request.form)
        edit_section_form = EditSectionForm(edit=edit, formdata=request.form)

    # acts = models.Act.query.all()
    # choices = [(act.name, act.name) for act in acts]
    # edit_section_form.name.choices = choices

    # if request.method == 'POST' and 'text' in request.form:
    #     print(request.form)
    #     edit_section_form = EditSectionForm(edit=edit, act_name=act_name, section_id_init=section_id, **request.form)
    #
    #     edit_section_form.name.choices = choices

    if edit_section_form.validate_on_submit():
        print("test")
        print(request.form)
        if 'delete' in request.form and request.form['delete']:
            db.session.delete(section)  # noqa the linter is not smart enough
            db.session.commit()
        elif edit:
            print("test")
            section.last_ammend_date = edit_section_form.last_ammend_date.data  # noqa the linter is not smart enough
            section.text = edit_section_form.text.data
            db.session.commit()
        else:
            section = models.Section(name=edit_section_form.name.data,
                                     section_id=edit_section_form.section_id.data,
                                     last_ammend_date=edit_section_form.last_ammend_date.data,
                                     text=edit_section_form.text.data)
            db.session.add(section)
            db.session.commit()

        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('edit_section.html', 'edit_section')
        elif 'Signup' in request.form.values():
            return signup_helper('edit_section.html', 'edit_section')
    login_form = LoginForm()
    signup_form = SignupForm()
    return render_template('edit_section.html', login_form=login_form, signup_form=signup_form, page='index',
                           edit_section_form=edit_section_form, session=session, act_name=act_name,
                           section_id=section_id)


@app.route('/get_act_name', methods=['POST'])
def get_act_name():
    if request.method == 'POST':
        ajax = '_ajax' in request.form
        if ajax:
            act_name_kw = request.form['act_name']
            acts = models.Act.search(act_name_kw).limit(5).all()

            json_out = [{'act_name': act.name} for act in acts]
            # choices = [(act.name, act.name) for act in acts]
            # edit_section_form.name.choices = choices

            return jsonify(json_out)


@app.route('/add_case')
def add_case():
    if request.method == 'POST':
        if 'Login' in request.form.values():
            return login_helper('add_case.html', 'add_case')
        elif 'Signup' in request.form.values():
            return signup_helper('add_case.html', 'add_case')
    login_form = LoginForm()
    signup_form = SignupForm()

    return render_template('add_case.html', login_form=login_form, signup_form=signup_form)
