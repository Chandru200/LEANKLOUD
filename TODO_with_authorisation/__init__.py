
from  LOGIN import api as login_api
from  TODO import ns as todo_api

from flask_restplus import Api
from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

api = Api(
    title='TODO wiht authorization API',
    version='1.0',
    description='A simple demo API',
)

api.add_namespace(login_api)
api.add_namespace(todo_api)

app = Flask(__name__)
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'todo_task'
mysql = MySQL(app)
app.app_context().push()
app.wsgi_app = ProxyFix(app.wsgi_app)
api.init_app(app)
if __name__ == '__main__':
    app.run()   