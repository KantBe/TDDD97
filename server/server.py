from flask import Flask, request, jsonify
import json, re

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
    return jsonify(response)

@app.get('/user_info/<username>')
def get_all_user_info(username):
    response = {}
    response['info'] = database_helper.get_all_user_info(username)
    response['session'] = database_helper.get_sessions_by_user(username)
    return jsonify(response)

@app.post('/sign_up/')
def signup():
    # print(request.data)
    if request.data:
        data = json.loads(request.data)
    else:
        data = {}
    success, message = check_keys(SIGNUP_KEYS, data)

    if success:
        # check if the data fields are valid
        success, message = validate_signup_data(data)
        if success:
            success, message = validate_password(data['password'])
    
    if success:
        # save the user and encrypt the password
        data['password'] = database_helper.encrypt_password(\
                data['password'].encode('utf-8')\
            ).decode('utf-8')
        # print(data)
        success, message = database_helper.save_user(data)

    response = {}
    response['success'] = success
    response['message'] = message
    return jsonify(response)

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
    return jsonify(response)

@app.get('/change_password/')
def change_password():
    if request.data:
        data = json.loads(request.data)
    else:
        data = {}

    success, message = check_keys(['token', 'oldpassword', 'newpassword'], data)

    if success:
        up = database_helper.get_user_and_password_by_token(data['token'])
        if up:
            user, password = up
            success = database_helper.check_password(data['oldpassword'], password)
            
            if success:
                success, message = validate_password(data['newpassword'])
                if success:
                    password = database_helper.encrypt_password(password).decode('utf-8')
                    database_helper.update_password_by_username(user, password)
                    message = 'Password updated successfully'
            else:
                message = 'Wrong password provided'
        else:
            success = False
            message = 'Invalid token'

    response = {}
    response['success'] = success
    response['message'] = message
    return jsonify(response)
    

###########################
# HELPER FUNCTIONS
###########################
def check_keys(keys, data):
    """
    Checks if data contains the given keys.
    returns (False, <error message>) if there are keys missing, else (True, '')
    """
    missing_keys = [key for key in keys if (key not in data.keys())]

    success = not missing_keys
    message = '' if success else 'Invalid request! Missing the following data: ' + ', '.join(missing_keys)
    return (success, message)

def generate_token():
    """
    Generates and returns an auth token
    """
    return str(uuid4())

def validate_signup_data(data):
    """
    Checks whether the signup data is valid (e.g. empty fields or invalid email)
    returns (False, <error message>) for invalid data, else (True, '')
    """
    for key in SIGNUP_KEYS:
        if len(data[key].trim()) == 0:
            return (False, key + ' is empty')
    if not re.match(r'.+@.+', data['email']):
        return (False, 'Email is not valid')
    if data['gender'].lower() not in ['male', 'female', 'other']:
        return (False, 'Gender is not valid')
    else:
        data['gender'] = data['gender'].upper()
    
    return (True, '')

def validate_password(password):
    """
    Checks if the password is of valid length
    returns (False, 'Password is not long enough') if not, (True, '') if it is
    """
    print(len(password), password)
    if len(password) < 8:
        return (False, 'Password is not long enough')
    return (True, '')