from flask_restplus import Namespace, Resource, fields
api = Namespace('LOGIN', description='Enter password edit and delete todos')

login_user = api.model('LOGIN', {
    'Password': fields.String(required=True, description='Enter password to edit and delete'),
})

class Login(object):
    def __init__(self):
        self.login = False
Log = Login()


@api.route('/<string:Password>')
@api.param('Password', 'Password')

class Dog(Resource):
    @api.doc('get_password')
    @api.marshal_with(login_user)
    def post(self, Password):
        '''Enter password to update and delete the todos'''
        if Password == 'admin' or Password == 'Admin' or Password == 'user':
            Log.login = True
        