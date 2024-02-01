from flask import Flask, request
import json

from uuid import uuid4

import database_helper

SIGNUP_KEYS = ['email', 'password', 'firstname', 'familyname', 'gender', 'city', 'country']
app = Flask(__name__)

database_helper.init_db(app)

@app.teardown_appcontext
def close_connection(exception):
    database_helper.close_connection(exception)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get('/sign_in/')
def signin():
    if request.data:
        data = json.loads(request.data)
    else:
        data = {}

    success, message = check_keys(['username', 'password'], data)
    
    auth_token = None
    if success:
        username = data['username']
        password = data['password']
        # do something if all keys are there
        success, message = database_helper.login_user(username, password)
        if success:
            auth_token = generate_token()
            database_helper.store_token(auth_token, username)

    response = {}
    response['success'] = success
    response['message'] = message
    response['data'] = auth_token if auth_token else ''
    return json.dumps(response)

@app.get('/user_info/<username>')
def get_all_user_info(username):
    response = {}
    response['info'] = database_helper.get_all_user_info(username)
    response['session'] = database_helper.get_sessions_by_user(username)
    return json.dumps(response)

@app.post('/sign_up/')
def signup():
    # print(request.data)
    if request.data:
        data = json.loads(request.data)
    else:
        data = {}
    success, message = check_keys(SIGNUP_KEYS, data)
    
    if (success):
        # TODO: check if all field's values are correct
        data['password'] = database_helper.encrypt_password(data['password'].encode('utf-8')).decode('utf-8')
        # print(data)
        success, message = database_helper.save_user(data)

    response = {}
    response['success'] = success
    response['message'] = message
    return json.dumps(response)

@app.get('/sign_out/')
def signout():
    if request.data:
        data = json.loads(request.data)
    else:
        data = {}
    
    success, message = check_keys(['token'], data)
    
    if success:
        token = data['token']
        # check if user with this token is logged in
        # and log out user
        session = database_helper.get_session_by_token(token)
        print(session)
        if not session:
            success = False
            message = 'No session with the given token exists'
        else:
            res = database_helper.delete_session_by_token(token)
            print(res)
            message = 'Successfully logged out user'
        pass
    
    response = {}
    response['success'] = success
    response['message'] = message
    return json.dumps(response)

def check_keys(keys, data):
    missing_keys = [key for key in keys if key not in data.keys()]

    success = not missing_keys
    message = '' if success else 'Invalid request! Missing the following data: ' + ', '.join(missing_keys)
    return (success, message)

def generate_token():
    return str(uuid4())
