from flask import Flask, request, jsonify
import json, re, bcrypt

from uuid import uuid4

import database_helper

SIGNUP_KEYS = ['email', 'password', 'firstname', 'familyname', 'gender', 'city', 'country']

app = Flask(__name__)

# initialize the app
database_helper.init_db(app)

@app.teardown_appcontext
def close_connection(exception):
    database_helper.close_connection(exception)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.get('/sign_in/')
def signin():
    data = request.get_json()

    success, message = check_keys(['username', 'password'], data)
    
    auth_token = None
    if success:
        username = data['username']
        password = data['password']
        # do something if all keys are there
        success, message = login_user(username, password)
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
    data = request.get_json()
    success, message = check_keys(SIGNUP_KEYS, data)

    if success:
        # check if the data fields are valid
        success, message = validate_signup_data(data)
        if success:
            success, message = validate_password(data['password'])
    
    if success:
        # save the user and encrypt the password
        data['password'] = encrypt_password(\
                data['password'].encode('utf-8')\
            ).decode('utf-8')
        # print(data)
        success, message = save_user(data)

    response = {}
    response['success'] = success
    response['message'] = message
    return jsonify(response)

@app.get('/sign_out/')
def signout():
    data = request.get_json()
    
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

@app.put('/change_password/')
def change_password():
    data = request.get_json()

    success, message = check_keys(['token', 'oldpassword', 'newpassword'], data)

    if success:
        success, message = change_user_password(data)

    response = {}
    response['success'] = success
    response['message'] = message
    return jsonify(response)

@app.get('/get_user_messages_by_token/')
def get_user_messages_by_token():
    data = request.get_json()

    success, message = check_keys(['token'], data)
    messages = []
    if success:
        success, message, messages = get_user_messages(data['token'])
    
    response = {}
    response['success'] = success
    response['message'] = message
    response['data'] = messages
    return jsonify(response)

@app.get('/get_user_messages_by_email/')
def get_user_messages_by_email():
    data = request.get_json()

    success, message = check_keys(['token', 'email'], data)
    messages = []
    if success:
        success, message, messages = get_user_messages(data['token'], data['email'])
    
    response = {}
    response['success'] = success
    response['message'] = message
    response['data'] = messages
    return jsonify(response)

@app.post('/post_message/')
def post_message():
    data = request.get_json()
    database_helper.insert_message(data['writer'], data['message'], data['user'])
    
    response = {}
    response['success'] = True
    response['message'] = 'Message saved'
    return jsonify(response)

###########################
# HELPER FUNCTIONS
###########################
def check_keys(keys: list, data: dict) -> tuple[bool, str]:
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

def validate_signup_data(data) -> tuple[bool, str]:
    """
    Checks whether the signup data is valid (e.g. empty fields or invalid email)
    returns (False, <error message>) for invalid data, else (True, '')
    """
    for key in SIGNUP_KEYS:
        if len(data[key].strip()) == 0:
            return (False, key + ' is empty')
    if not re.match(r'.+@.+', data['email']):
        return (False, 'Email is not valid')
    if data['gender'].lower() not in ['male', 'female', 'other']:
        return (False, 'Gender is not valid')
    else:
        data['gender'] = data['gender'].upper()
    
    return (True, '')

def validate_password(password: str) -> tuple[bool, str]:
    """
    Checks if the password is of valid length
    returns (False, 'Password is not long enough') if not, (True, '') if it is
    """
    print(len(password), password)
    if len(password) < 8:
        return (False, 'Password is not long enough')
    return (True, '')

def change_user_password(data: {"token": str, "oldpassword": str, "newpassword": str}) -> tuple[bool, str]:
    """
    Changes the users password.
    The data has to be of the following type:
    `{
    token: string,
    oldpassword: string,
    newpassword: string
    }`
    Returns `(success: boolean, success_message: string)`
    """
    success, message, user, password = check_token_validity(data['token'])
    if not success:
        return (success, message)
    success, message = check_password(data['oldpassword'], password)
    if not success:
        return (success, message)
    success, message = validate_password(data['newpassword'])
    if not success:
        return (success, message)

    password = encrypt_password(data['newpassword']).decode('utf-8')
    database_helper.update_password_by_username(user, password)
    message = 'Password updated successfully'
    return (success, message)


# def login_user(username: str, password: str | bytes):
def login_user(username: str, password: str or bytes):
    """
    Tries to login the user with the given username and password.
    Returns `(success: boolean, success_message: string)`
    """
    # up = username + password
    up = database_helper.get_user_and_password_by_username(username)
    
    if up:
        username, checked_password = up
        success, message = (check_password(password, checked_password))
    else:
        success = False
        message = 'Invalid username'
    return (success, message)

def encrypt_password(password: str or bytes) -> bytes:
    """
    Encrypts the password and returns it.
    """
    if (type(password) is str):
        password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt())

def check_password(password: str or bytes, encrypted_password: str or bytes) -> tuple[bool, str]:
    """
    Checks if `password` (unencrypted) matches with `encrypted_password` (encrypted).
    Returns `(success: bool, success_message: string)`
    """
    if (type(password) is str):
        password = password.encode('utf-8')
    if type(encrypted_password) is str:
        encrypted_password = encrypted_password.encode('utf-8')
    print(password, encrypted_password)
    success = bcrypt.checkpw(password, encrypted_password)
    return (success, 'User signed in successfully' if success else 'Password invalid')

def check_token_validity(token: str) -> tuple[bool, str, str or None, str or None]:
    """
    Checks if the given token is valid and returns the corresponding user and password if it is.
    Returns the following tuple:
    `(success: boolean, success_message: string, user: string | None, password: string | None)`
    """
    up = database_helper.get_user_and_password_by_token(token)
    if not up:
        return (False, 'Invalid token', None, None)
    user, password = up
    return (True, 'Token is valid', user, password)

def get_user_messages(token: str, _user: str or None=None) -> tuple[bool, str, list]:
    """
    Retrieves all the user messages of the given user with the given token.
    If user is None (default), the messages of the user with the given token will be retrieved instead.
    Returns: `(success: bool, success_message: string, messages: list({ writer:string, message: string }))`
    """
    messages = []
    success, message, user, _ = check_token_validity(token)
    if not success:
        return (success, message, messages)
    
    if _user and not database_helper.user_exists(_user):
        return (False, 'No user with this email exists', messages)
    
    raw_messages = database_helper.get_messages_writer_and_text_by_user(_user if _user else user)
    message = 'Successfully retreived messages for user ' + user
    for m in raw_messages:
        messages.append({'writer': m[0], 'message': m[1]})

    return (success, message, messages)

def save_user(user) -> tuple[bool, str]:
    if database_helper.user_exists(user['email']):
        return (False, 'User with this email already exists')
    
    user = (user['email'], user['password'], user['firstname'], user['familyname'], user['gender'], user['city'], user['country'])
    database_helper.insert_user(user)
    return (True, 'User created successfully')
