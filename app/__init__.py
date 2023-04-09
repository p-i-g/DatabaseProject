from flask import Flask
from flask_mysqldb import MySQL
from flask_modals import Modal
import os
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'project'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/project'

app.secret_key = os.urandom(24)

mysql = MySQL(app)
modal = Modal(app)
db = SQLAlchemy(app)


from app import routes
