from flask import Flask
from flask_mysqldb import MySQL
from flask_modals import Modal
import os
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/law_database'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = os.urandom(24)

# mysql = MySQL(app)
modal = Modal(app)
db = SQLAlchemy(app)


from app import routes
