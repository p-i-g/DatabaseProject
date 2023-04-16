from flask import url_for
from sqlalchemy import tuple_, inspect

from app import db
from sqlalchemy.dialects.mysql import LONGTEXT
from markupsafe import Markup

from app.fulltext_search import Match


def _render_table(query_results, classes, headings, link_fn=None):
    html = ['''
    <table class="table my-2 table-hover">
        <thead>
        <tr>
    ''']
    for i in range(len(headings)):
        html.append(f'<th scope="col" class="{classes[i]}">{headings[i]}</th>')

    html.append('</tr></thead>')

    for r in query_results:
        style = 'style="cursor:pointer"' if link_fn is not None else ''
        onclick = f'onclick="location.href=\'{link_fn(r)}\'"' if link_fn is not None else ''  # spaghetti code
        html.append(f'<tr {style} {onclick}>')
        for i in range(len(headings)):
            html.append(f'<td class="{classes[i]}">{r[headings[i]]}</td>')

        html.append('</tr>')

    html.append('</table>')

    return Markup(''.join(html))


class Act(db.Model):
    __tablename__ = 'act'

    name = db.Column(db.String(255), primary_key=True)
    last_ammend_date = db.Column(db.Date)
    title = db.Column(db.String(1023))
    commence_date = db.Column(db.Date)

    # these two functions are repeated for every class. idt making a superclass will make it better.
    @classmethod
    def search(cls, kw):
        if not kw:
            return cls.query
        return cls.query.filter(
            Match(cls.name, kw)
        ).order_by(
            Match(cls.name, kw).desc()
        )

    @classmethod
    def render_table(cls, query_results):
        classes = [
            'col-12 col-md-6 col-lg-8',
            'd-none d-md-table-cell col-md-3 col-lg-2',
            'd-none d-lg-table-cell col-md-3 col-lg-2'
        ]

        headings = [
            'Act Name',
            'Last Amend Date',
            'Commencement Date'
        ]

        results_list = []
        for act in query_results:
            results_list.append({
                'Act Name': act.name,
                'Last Amend Date': act.last_ammend_date,
                'Commencement Date': act.commence_date
            })

        def link_fn(r):
            return url_for('act_details', act_name=r['Act Name'])

        return _render_table(results_list, classes, headings, link_fn)

    @classmethod
    def get_details(cls, act_name):
        act = cls.query.filter_by(name=act_name).first_or_404()

        sections = Section.query.filter_by(name=act_name)

        return act, sections

    @classmethod
    def check_key_constraint(cls, key):
        return cls.query.filter(cls.name == key).first()


class Court(db.Model):
    __tablename__ = 'court'

    court_id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    website = db.Column(db.String(255))
    address = db.Column(db.String(255))

    judges = db.relationship('Judge', secondary='current_judges')

    @classmethod
    def search(cls, kw):
        if not kw:
            return cls.query
        return cls.query.filter(
            Match(cls.name, kw)
        ).order_by(
            Match(cls.name, kw).desc(),
            cls.court_id
        )

    @classmethod
    def render_table(cls, query_results):
        classes = [
            'd-none d-md-table-cell col-md-4 col-lg-2 col-xl-1',
            'col-12 col-md-8 col-lg-6 col-xl-4',
            'd-none d-lg-table-cell col-lg-2 col-xl-2',
            'd-none d-lg-table-cell col-lg-4 col-xl-2',
            'd-none d-xl-table-cell col-xl-3'
        ]

        headings = [
            'ID',
            'Court Name',
            'Phone Number',
            'Website',
            'Address'
        ]

        results_list = []
        for court in query_results:
            results_list.append({
                'ID': court.court_id,
                'Court Name': court.name,
                'Phone Number': court.phone,
                'Website': court.website,
                'Address': court.address
            })

        def link_fn(r):
            return url_for('court_details', court_id=r['ID'])

        return _render_table(results_list, classes, headings, link_fn)

    @classmethod
    def get_details(cls, court_id):
        court = cls.query.filter(cls.court_id == court_id).first_or_404()

        cases = Case.query.filter(Case.court_id == court_id)

        return court, cases


class Firm(db.Model):
    __tablename__ = 'firm'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    address = db.Column(db.String(255))
    email = db.Column(db.String(255))

    lawyers = db.relationship('Lawyer', secondary='works_for')

    @classmethod
    def search(cls, kw):
        if not kw:
            return cls.query
        return cls.query.filter(
            Match(cls.name, kw)
        ).order_by(
            Match(cls.name, kw).desc(),
            cls.id
        )

    @classmethod
    def render_table(cls, query_results):
        classes = [
            'col-12 col-md-8 col-lg-6',
            'd-none d-md-table-cell col-md-4 col-lg-2',
            'd-none d-lg-table-cell col-lg-4',
            'd-none d-lg-table-cell col-lg-2'
        ]

        headings = [
            'Name',
            'Phone Number',
            'Address',
            'Email',
        ]

        results_list = []
        for firm in query_results:
            results_list.append({
                'Name': firm.name,
                'Phone Number': firm.phone,
                'Address': firm.address,
                'Email': firm.email,
                'id': firm.id
            })

        def link_fn(f):
            return url_for('firm_details', firm_id=f["id"])

        return _render_table(results_list, classes, headings, link_fn)

    @classmethod
    def render_list(cls, query_results):
        html = []
        for firm in query_results:
            html.append(f'<a href="{url_for("firm_details", firm_id=firm.id)}">{firm.name}</a>&emsp;')
        return Markup(''.join(html))

    @classmethod
    def get_details(cls, firm_id):
        firm = cls.query.filter_by(id=firm_id).first_or_404()

        specs = FirmSpec.query.filter(FirmSpec.id == firm_id)

        lawyers = db.session.query(t_works_for) \
            .filter(t_works_for.c.firm_id == firm_id).with_entities(t_works_for.c.lawyer_id)
        lawyers = Lawyer.query.filter(Lawyer.id.in_(lawyers))

        return firm, specs, lawyers


class Judge(db.Model):
    __tablename__ = 'judge'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    position = db.Column(db.String(255))

    @classmethod
    def search(cls, kw):
        if not kw:
            return cls.query
        return cls.query.filter(
            Match(cls.name, kw) * 10 + Match(cls.position, kw)
        ).order_by(
            Match(cls.name, kw) * 10 + Match(cls.position, kw).desc()
        )

    @classmethod
    def render_table(cls, query_results):
        classes = [
            'col-12 col-md-6',
            'd-none d-md-table-cell col-md-6',
        ]

        headings = [
            'Name',
            'Position',
        ]

        results_list = []
        for judge in query_results:
            results_list.append({
                'Name': judge.name,
                'Position': judge.position,
                'id': judge.id
            })

        def link_fn(r):
            return url_for('judge_details', judge_id=r['id'])

        return _render_table(results_list, classes, headings, link_fn)

    @classmethod
    def render_list(cls, query_results):
        html = []
        for judge in query_results:
            html.append(f'<a href="{url_for("judge_details", judge_id=judge.id)}">{judge.name}</a>&emsp;')
        return Markup(''.join(html))

    @classmethod
    def get_details(cls, judge_id):
        judge = cls.query.filter(cls.id == judge_id).first_or_404()

        cases = db.session.query(t_presides).filter(t_presides.c.judge_id == judge_id).with_entities(
            t_presides.c.case_id)
        cases = Case.query.filter(Case.case_id.in_(cases))

        return judge, cases


class Lawyer(db.Model):
    __tablename__ = 'lawyer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(255))

    @classmethod
    def search(cls, kw):
        if not kw:
            return cls.query
        return cls.query.filter(
            Match(cls.name, kw)
        ).order_by(
            Match(cls.name, kw).desc(),
            cls.id
        )

    @classmethod
    def render_table(cls, query_results):
        classes = [
            'col-12 col-md-6',
            'd-none d-md-table-cell col-md-3',
            'd-none d-md-table-cell col-md-3',
        ]

        headings = [
            'Name',
            'Phone Number',
            'Email',
        ]

        results_list = []
        for lawyer in query_results:
            results_list.append({
                'Name': lawyer.name,
                'Phone Number': lawyer.phone,
                'Email': lawyer.email,
                'id': lawyer.id
            })

        def link_fn(r):
            return url_for('lawyer_details', lawyer_id=r['id'])

        return _render_table(results_list, classes, headings, link_fn)

    @classmethod
    def get_details(cls, lawyer_id):
        lawyer = cls.query.filter(cls.id == lawyer_id).first_or_404()

        cases = db.session.query(t_litigates).filter(t_litigates.c.id == lawyer_id).with_entities(
            t_litigates.c.case_id)
        cases = Case.query.filter(Case.case_id.in_(cases))

        firms = db.session.query(t_works_for) \
            .filter(t_works_for.c.lawyer_id == lawyer_id).with_entities(t_works_for.c.firm_id)
        firms = Firm.query.filter(Firm.id.in_(firms))

        return lawyer, cases, firms


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    @classmethod
    def search(cls, kw):
        return cls.query.filter(cls.username.like(f'%{kw}%'))


class Case(db.Model):
    __tablename__ = 'cases'

    case_id = db.Column(db.String(127), primary_key=True)
    court_id = db.Column(db.ForeignKey('court.court_id', ondelete='SET NULL', onupdate='CASCADE'), index=True)
    date = db.Column(db.Date)

    court = db.relationship('Court')
    old_cases = db.relationship(
        'Case',
        secondary='case_reference',
        primaryjoin='Case.case_id == case_reference.c.case_id',
        secondaryjoin='Case.case_id == case_reference.c.old_case_id'
    )
    lawyer = db.relationship('Lawyer', secondary='litigates')
    judges = db.relationship('Judge', secondary='presides')
    section = db.relationship('Section', secondary='section_reference')

    @classmethod
    def search(cls, kw):
        if not kw:
            return cls.query
        return cls.query.filter(
            Match(cls.case_id, kw)
        ).order_by(
            Match(cls.case_id, kw).desc()
        )

    @classmethod
    def render_table(cls, query_results):
        classes = [
            'col-6',
            'col-6'
        ]

        headings = [
            'Case ID',
            'Court ID',
        ]

        results_list = []
        for case in query_results:
            results_list.append({
                'Case ID': case.case_id,
                'Court ID': case.court_id
            })

        def link_fn(r):
            return url_for('case_details', case_id=r['Case ID'])

        return _render_table(results_list, classes, headings, link_fn)

    @classmethod
    def render_list(cls, query_results):
        html = ['<ul class="list-group">']

        for case in query_results:
            html.append(
                f'<li class="list-group-item"><a href="'
                f'{url_for("case_details", case_id=case.case_id)}">{case.case_id}</a></li>')
        html.append('</ul>')

        # def link_fn(r):
        #     return url_for('section_details', act_name=r['Act'], section_no=r['Section Number'])

        return Markup(''.join(html))

    @classmethod
    def get_details(cls, case_id):
        case = cls.query.filter(cls.case_id == case_id).first_or_404()

        sections = db.session.query(t_section_reference).filter(
            t_section_reference.c.case_id == case_id).with_entities(
            t_section_reference.c.name, t_section_reference.c.section_id)
        sections = Section.query.filter(tuple_(Section.name, Section.section_id).in_(sections))

        lawyers = db.session.query(t_litigates) \
            .filter(t_litigates.c.case_id == case_id).with_entities(t_litigates.c.id)
        lawyers = Lawyer.query.filter(Lawyer.id.in_(lawyers))

        judges = db.session.query(t_presides) \
            .filter(t_presides.c.case_id == case_id).with_entities(t_presides.c.judge_id)
        judges = Judge.query.filter(Judge.id.in_(judges))

        fields = CaseField.query.filter(CaseField.case_id == case_id)

        cases = db.session.query(t_case_reference).filter(
            t_case_reference.c.case_id == case_id).with_entities(
            t_case_reference.c.old_case_id)
        cases = cls.query.filter(cls.case_id.in_(cases))

        return case, sections, lawyers, judges, fields, cases


t_current_judges = db.Table(
    'current_judges', db.metadata,
    db.Column('court_id', db.ForeignKey('court.court_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False),
    db.Column('judge_id', db.ForeignKey('judge.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False, index=True)
)


class FirmSpec(db.Model):
    __tablename__ = 'firm_spec'

    id = db.Column(db.ForeignKey('firm.id'), primary_key=True, nullable=False)
    specialization = db.Column(db.String(255), primary_key=True, nullable=False)

    firm = db.relationship('Firm')

    @classmethod
    def search(cls, kw):
        return cls.query.filter(
            Match(cls.specialization, kw)
        ).order_by(
            Match(cls.specialization, kw).desc()
        )

    @classmethod
    def render_list(cls, query_results):
        html = ['<ul class="list-group">']

        for spec in query_results:
            html.append(f'<li class="list-group-item">{spec.specialization}</li>')
        html.append('</ul>')

        return Markup(''.join(html))


class LawyerSpec(db.Model):
    __tablename__ = 'lawyer_spec'

    id = db.Column(db.ForeignKey('lawyer.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    specialization = db.Column(db.String(255), primary_key=True, nullable=False)

    lawyer = db.relationship('Lawyer')

    @classmethod
    def search(cls, kw):
        return cls.query.filter(
            Match(cls.specialization, kw)
        ).order_by(
            Match(cls.specialization, kw).desc()
        )


class Section(db.Model):
    __tablename__ = 'section'

    name = db.Column(db.ForeignKey('act.name', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                     nullable=False)
    section_id = db.Column(db.String(15), primary_key=True, nullable=False)
    last_ammend_date = db.Column(db.Date)
    text = db.Column(LONGTEXT)

    act = db.relationship('Act')

    @classmethod
    def search(cls, kw):
        return (
            cls.query

            .filter((Match(cls.name, kw) * 10 +
                     Match(cls.section_id, kw) * 1 +
                     Match(cls.text, kw) * 0.5))

            .order_by((Match(cls.name, kw) * 10 +
                       Match(cls.section_id, kw) * 5 +
                       Match(cls.text, kw) * 1).desc(),

                      cls.name, cls.section_id)) \
            if kw != '' and kw is not None else cls.query.order_by(cls.name, cls.section_id)

    @classmethod
    def render_table(cls, query_results):
        classes = [
            'col-12 col-md-7 col-lg-8',
            'd-none d-md-table-cell col-md-5 col-lg-2',
            'd-none d-lg-table-cell col-lg-2'
        ]

        headings = [
            'Act',
            'Section Number',
            'Last Amend Date'
        ]

        results_list = []
        for section in query_results:
            results_list.append({
                'Act': section.name,
                'Section Number': section.section_id,
                'Last Amend Date': section.last_ammend_date
            })

        def link_fn(r):
            return url_for('section_details', act_name=r['Act'], section_no=r['Section Number'])

        return _render_table(results_list, classes, headings, link_fn)


t_works_for = db.Table(
    'works_for', db.metadata,
    db.Column('firm_id', db.ForeignKey('firm.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False),
    db.Column('lawyer_id', db.ForeignKey('lawyer.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False, index=True)
)


class CaseField(db.Model):
    __tablename__ = 'case_field'

    case_id = db.Column(db.ForeignKey('cases.case_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
                        nullable=False)
    field = db.Column(db.String(255), primary_key=True, nullable=False)

    case = db.relationship('Case')

    @classmethod
    def search(cls, kw):
        return cls.query.filter(
            Match(cls.field, kw)
        ).order_by(
            Match(cls.field, kw).desc()
        )

    @classmethod
    def render_list(cls, query_results):
        html = ['<ul class="list-group">']

        for field in query_results:
            html.append(f'<li class="list-group-item">{field.field}</li>')
        html.append('</ul>')

        return Markup(''.join(html))


t_case_reference = db.Table(
    'case_reference', db.metadata,
    db.Column('case_id', db.ForeignKey('cases.case_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False),
    db.Column('old_case_id', db.ForeignKey('cases.case_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False, index=True)
)

t_litigates = db.Table(
    'litigates', db.metadata,
    db.Column('id', db.ForeignKey('lawyer.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False),
    db.Column('case_id', db.ForeignKey('cases.case_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False, index=True)
)

t_presides = db.Table(
    'presides', db.metadata,
    db.Column('case_id', db.ForeignKey('cases.case_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False),
    db.Column('judge_id', db.ForeignKey('judge.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True,
              nullable=False, index=True)
)

t_section_reference = db.Table(
    'section_reference', db.metadata,
    db.Column('name', db.String(255), primary_key=True, nullable=False),
    db.Column('section_id', db.String(15), primary_key=True, nullable=False),
    db.Column('case_id', db.ForeignKey('cases.case_id'), primary_key=True, nullable=False, index=True),
    db.ForeignKeyConstraint(['name', 'section_id'], ['section.name', 'section.section_id'])
)
