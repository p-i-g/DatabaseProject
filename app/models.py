from app import db
from sqlalchemy.dialects.mysql import LONGTEXT


class Act(db.Model):
    __tablename__ = 'act'

    name = db.Column(db.String(255), primary_key=True)
    last_ammend_date = db.Column(db.Date)
    title = db.Column(db.String(1023))
    commence_date = db.Column(db.Date)

    @classmethod
    def search(cls, kw):
        return cls.query.filter_by(cls.name.like(f'%{kw}%') | cls.title.like(f'%{kw}%'))


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
        return cls.query.filter_by(cls.name.like(f'%{kw}%'))


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
        return cls.query.filter_by(cls.name.like(f'%{kw}%'))


class Judge(db.Model):
    __tablename__ = 'judge'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    position = db.Column(db.String(255))

    @classmethod
    def search(cls, kw):
        return cls.query.filter_by(cls.name.like(f'%{kw}%'))


class Lawyer(db.Model):
    __tablename__ = 'lawyer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(255))

    @classmethod
    def search(cls, kw):
        return cls.query.filter_by(cls.name.like(f'%{kw}%'))


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)

    @classmethod
    def search(cls, kw):
        return cls.query.filter_by(cls.username.like(f'%{kw}%'))


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


class LawyerSpec(db.Model):
    __tablename__ = 'lawyer_spec'

    id = db.Column(db.ForeignKey('lawyer.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True, nullable=False)
    specialization = db.Column(db.String(255), primary_key=True, nullable=False)

    lawyer = db.relationship('Lawyer')


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
        return cls.query.filter_by(cls.name.like(f'%{kw}%') | cls.text.like(f'%{kw}%'))


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
