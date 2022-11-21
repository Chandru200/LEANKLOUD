import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
import datetime

from flask import Flask
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
 
app = Flask(__name__)
 
app.secret_key = 'your secret key'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'todo_task'
mysql = MySQL(app)
 


app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='TodoMVC API',
    description='A simple TodoMVC API',
)

ns = api.namespace('todos', description='TODO operations')

todo = api.model('Todo', {
    'id': fields.Integer(readonly=True, description='The task unique identifier'),
    'title': fields.String(required=True, description='The task details'),
    'description': fields.String(required=True, description='The task description'),
    'Due_by': fields.Date(required=True, descriptions='Due Date'),
    'Status': fields.String(required=True, description='Current Status'),
})


class TodoDAO(object):
    def __init__(self):
        self.todos = []

    def get(self, id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        input_query="SELECT * FROM todo WHERE id =" + str(id) 
        cursor.execute(input_query)
        todo = cursor.fetchone()
        return todo

    def update_todo(self):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from todo")
        todos_from_db = cursor.fetchall()
        self.todos=[]
        for i in todos_from_db:
            self.todos.append(i)

    def get_task_ondue(self, due_date):
        self.update_todo()
        filtered_list = []
        ENTERED_DUE_DATE = datetime.datetime.strptime(str(due_date),"%Y-%m-%d")
        for todo in self.todos:
            TODO_DUE_DATE = datetime.datetime.strptime(str(todo['Due_by']),"%Y-%m-%d")
            if( TODO_DUE_DATE <= ENTERED_DUE_DATE):
                if not (todo['Status'] == 'Finished' or todo['Status'] == 'finished'):
                    filtered_list.append(todo)
        return filtered_list

    def get_status_list(self, status):
        self.update_todo()
        filtered_list = []
        for todo in self.todos:
            if todo['Status'] == status:
                filtered_list.append(todo)
        return filtered_list
    
    def get_status_list_finished(self, status):
        self.update_todo()
        filtered_list = []
        for todo in self.todos:
            if todo['Status'] == "Finished"  or  todo['Status'] == "finished" :
                filtered_list.append(todo)
        return filtered_list

    def create(self, data):
        title = data.get('title')
        description = data.get('description')
        Due_by = data.get('Due_by')
        try:
            datetime.datetime.strptime(str(Due_by),"%Y-%m-%d")
        except:
            return "error"
       
        Status = data.get('Status')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO todo(title, description,Due_by,Status) VALUES(%s,%s,%s,%s)",[title ,description,Due_by,Status])
        mysql.connection.commit()
        return data

    def update(self, id, data):
        todo = self.get(id)
        todo.update(data)
        title = data.get('title')
        description = data.get('description')
        Due_by = data.get('Due_by')
        try:
            datetime.datetime.strptime(str(Due_by),"%Y-%m-%d")
        except:
            return "error"
        Status = data.get('Status')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE todo SET  title =% s, description =% s, Status =% s, Due_by =% s WHERE id =% s', (title, description, Status, Due_by, id ))
        mysql.connection.commit()
        return todo

    def delete(self, id):
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        input_query="DELETE FROM todo WHERE id =" + str(id) 
        cursor.execute(input_query)
        mysql.connection.commit()
        todo = self.get(id)    
        
    def get_all_finished(self):
        self.update_todo()
        filtered_list = []
        for todo in self.todos:
            if todo['Status'] == "Finished" or todo['Status'] == "finished":
                filtered_list.append(todo)
        return filtered_list

DAO = TodoDAO()

@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from todo")
        todos_from_db = cursor.fetchall()
        self.todos=[]
        for i in todos_from_db:
            self.todos.append(i)
        return self.todos

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        response  =  DAO.create(api.payload)
        if response== "error":
            return {
            "description": "Please enter date in yyyy-mm-dd",
            } 
        else:
            return response
            

@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        response  =  DAO.update(id, api.payload)
        if response== "error":
            return {
            "description": "Please enter date in yyyy-mm-dd",
            } 
        else:
            return response


@ns.route('/<string:due_date>')
class TodoListByDueDate(Resource):
    '''Shows a list of all todos By Due Date'''

    @ns.doc('list_todos_by_due')
    @ns.marshal_list_with(todo)
    def get(self, due_date):
        '''List all tasks which are due to be ﬁnished on that speciﬁed date'''
        try:
            ENTERED_DUE_DATE = datetime.datetime.strptime(str(due_date),"%Y-%m-%d")
            return DAO.get_task_ondue(due_date)
        except:
            print("called")
            return {
            "description": "Please enter date in yyyy-mm-dd",
            } 

@ns.route('/overduedate')
class TodoListByOverDueDate(Resource):
    '''Shows a list of all todos By Over Due Date'''

    @ns.doc('list_todos_by_over_due')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks which are past their due date'''
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("select * from todo")
        todos_from_db = cursor.fetchall()
        self.todos=[]
        for i in todos_from_db:
            self.todos.append(i)
        filtered_list = []
        over_due_date = str(datetime.datetime.today()).split()[0]
        for todo in self.todos:
            if datetime.datetime.strptime(str(todo['Due_by']),"%Y-%m-%d") < datetime.datetime.strptime(over_due_date,"%Y-%m-%d"):
                filtered_list.append(todo)
        return filtered_list


@ns.route('/status/<string:status>')
class TodoListByStatus(Resource):
    '''Shows a list of all todos By Status (Progress,)'''

    @ns.doc('list_todos_by_status')
    @ns.marshal_list_with(todo)
    def get(self, status):
        '''List all tasks'''
        return DAO.get_status_list(status)



@ns.route('/Finished')
class TodoListByOverDueDate(Resource):
    '''Shows a list of all todos By Over Due Date'''

    @ns.doc('list_todos_by_over_due')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks which are FINISHED'''
        return DAO.get_all_finished()
        


if __name__ == '__main__':
    app.run(debug=True)