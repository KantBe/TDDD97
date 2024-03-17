from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS, cross_origin
from flask_sock import Sock, ConnectionClosed, Server
import re, bcrypt

from uuid import uuid4

from decorators import authorized, check_token_validity
from mailserver import send_password_reset_link
import database_helper

SIGNUP_KEYS = ['email', 'password', 'firstname', 'familyname', 'gender', 'city', 'country']

app = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
cors = CORS(app)
sock = Sock(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}

sockets = {}

# initialize the app
database_helper.init_db(app)

@sock.route('/websocket')
def websocket(socket: Server):
    check = check_token_validity()
    if type(check) is Response:
        return check
    token = check
    email = database_helper.read_username_by_token(token)
    
    # then we send an acknowledgement
    socket.send('received: ' + str(email))
    # print(token)
    
    close_socket(email, False)
    sockets[email] = socket
    
    while True:
        # we receive endlessly to keep the socket alive
        msg = socket.receive()
        if msg:
            # also sends ping pong to keep alive
            socket.send('pong')

@app.teardown_appcontext
def close_connection(exception):
    database_helper.close_connection(exception)

@app.route('/')
@app.route('/login')
@app.route('/signup')
@app.route('/profile/home')
@app.route('/profile/browse')
@app.route('/profile/account')
def send_client():
    return render_template('client.html')

@app.get('/sign_in/')
@cross_origin()
def signin():
    """
    #### status codes:
    - 200: request successful
    - 400: username or password are missing in the request data
    - 401: username or password are wrong (as per `login_user`)
    - 405: wrong method
    - 500: an error occured
    """
    data = request.args

    status_code, message = check_keys(['username', 'password'], data)

    auth_token = None
    if status_code < 400:
        username = data['username']
        password = data['password']
        # do something if all keys are there
        status_code, message = login_user(username, password)
    
    # status code is only < 400 if user is logged in
    if status_code < 400:
        auth_token = generate_token()
        database_helper.create_token(auth_token, username)

    response = {}
    response['message'] = message
    response['data'] = auth_token if auth_token else ''
    res = jsonify(response)
    res.status_code = status_code

    res.headers.set('Authorization', auth_token)
    return res

@app.get('/user_info/<username>')
@cross_origin()
def get_all_user_info(username):
    """
    #### status codes:
    - 200: request successful
    - 405: wrong method
    - 500: an error occured
    """
    response = {}
    response['info'] = database_helper.read_all_user_info(username)
    response['session'] = database_helper.read_sessions_by_user(username)
    res = jsonify(response)
    res.status_code = 200
    return res

@app.post('/sign_up/')
@cross_origin()
def signup():
    """
    #### status codes:
    - 201: request successful
    - 400: any of `SIGNUP_KEYS` are missing in the request data or are invalid
    - 405: wrong method
    - 409: user with email already exists in database
    - 500: an error occured
    """
    data = request.get_json()
    status_code, message = check_keys(SIGNUP_KEYS, data)

    if status_code < 400:
        # check if the data fields are valid
        status_code, message = validate_signup_data(data)
        if status_code < 400:
            status_code, message = validate_password(data['password'])

    if status_code < 400:
        # save the user and encrypt the password
        data['password'] = encrypt_password(\
                data['password'].encode('utf-8')\
            ).decode('utf-8')
        # print(data)
        status_code, message = save_user(data)

    response = {}
    response['message'] = message
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.get('/sign_out/')
@cross_origin()
@authorized
def signout(token):
    """
    #### status codes:
    - 200: request successful
    - 401: token not in request or invalid (as per `@authorized`)
    - 405: wrong method
    - 500: an error occured
    """
    # check if user with this token is logged in
    # and log out user
    email = database_helper.read_username_by_token(token)
    close_socket(email, True)
    
    database_helper.delete_session_by_token(token)
    message = 'Successfully logged out user'
    
    response = {}
    response['message'] = message
    # we can return jsonfiy here since default status code is 200
    return jsonify(response)

@app.get('/check_token')
@cross_origin()
@authorized
def check_token(token):
    """
    #### status codes:
    - 200: request successful
    - 401: token not in request or invalid (as per `@authorized`)
    - 405: wrong method
    - 500: an error occured
    """
    return jsonify({'message': 'Valid token'})

@app.put('/change_password/')
@cross_origin()
@authorized
def change_password(token):
    """
    #### status codes:
    - 200: request successful
    - 400: `oldpassword` or `newpassword` are missing in the request's body
    or new password is not of valid form
    - 401: token not in request or invalid (as per `@authorized`) or old password is wrong
    - 405: wrong method
    - 500: an error occured
    """
    data = request.get_json()

    status_code, message = check_keys(['oldpassword', 'newpassword'], data)

    if status_code < 400:
        status_code, message = change_user_password(token, data)

    response = {}
    response['message'] = message
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.get('/get_user_messages_by_token/')
@cross_origin()
@authorized
def get_user_messages_by_token(token):
    """
    #### status codes:
    - 200: request successful
    - 401: token not in request or invalid (as per `@authorized`)
    - 405: wrong method
    - 500: an error occured
    """
    status_code, message, messages = get_user_messages(token)
    
    response = {}
    response['message'] = message
    response['data'] = messages
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.get('/get_user_messages_by_email/')
@cross_origin()
@authorized
def get_user_messages_by_email(token):
    """
    #### status codes:
    - 200: request successful
    - 400: `email` is not in request data
    - 401: token not in request or invalid (as per `@authorized`)
    - 404: user to get messages from doesn't exist
    - 405: wrong method
    - 500: an error occured
    """
    data = request.args

    status_code, message = check_keys(['email'], data)
    messages = []
    if status_code < 400:
        status_code, message, messages = get_user_messages(token, data['email'])
    
    response = {}
    response['message'] = message
    print(messages)
    response['data'] = messages
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.get('/get_user_data_by_token/')
@cross_origin()
@authorized
def get_user_data_by_token(token):
    """
    #### status codes:
    - 200: request successful
    - 401: token not in request or invalid (as per `@authorized`)
    - 405: wrong method
    - 500: an error occured
    """
    status_code, message, user_data = get_user_data(token)
    
    response = {}
    response['message'] = message
    response['data'] = user_data
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.get('/get_user_data_by_email/')
@cross_origin()
@authorized
def get_user_data_by_email(token):
    """
    #### status codes:
    - 200: request successful
    - 400: `email` does not exist in request data
    - 401: token not in request or invalid (as per `@authorized`)
    - 404: user to get data from does not exist
    - 405: wrong method
    - 500: an error occured
    """
    data = request.args

    status_code, message = check_keys(['email'], data)
    user_data = []
    if status_code < 400:
        status_code, message, user_data = get_user_data(token, data['email'])
    
    response = {}
    response['message'] = message
    response['data'] = user_data
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.post('/post_message/')
@cross_origin()
@authorized
def post_message(token):
    """
    #### status codes:
    - 201: request successful
    - 400: 
        - `email` does not exist in data or is None
        - `message` does not exist in data or is empty
    - 401: token not in request or invalid (as per `@authorized`)
    - 404: email of the user, on whom's board the message should be posted, does not exit
    - 405: wrong method
    - 500: an error occured
    """
    data = request.get_json()

    status_code, message = check_keys(['message', 'email'], data)

    if status_code < 400 and not database_helper.user_exists(data['email']):
        status_code, message = (404, 'User to write the message to does not exist')
    if status_code < 400 and data['message'] is None or str(data['message']).strip() == '':
        status_code, message = (400, 'Message is empty')
    if status_code < 400:
        author = database_helper.read_username_by_token(token)
        database_helper.create_message(author, data['message'], data['email'], data['latitude'], data['longitude'])
        status_code = 201

    response = {}
    response['message'] = message
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.post('/reset_password/')
@cross_origin()
def reset_password():
    """
    #### status codes:
    - 200: request successful
    - 400: `user` not provided
    - 404: user does not exist
    - 405: wrong method (e.g. post, put or delete)
    - 500: an error occured
    """
    data = request.get_json()
    
    status_code, message = check_keys(['user'], data)

    if status_code < 400:
        status_code = status_code if database_helper.user_exists(data['user']) else 404
        if status_code < 400:
            database_helper.delete_password_reset_by_user(data['user'])
            token = generate_token()
            database_helper.create_password_reset(token, data['user'])
            # send email
            send_password_reset_link(data['user'], token)
            status_code = 201
            message = 'Password reset requested'
        else:
            message = 'Given user does not exist'

    response = {}
    response['message'] = message
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.post('/set_password/')
@cross_origin()
def set_password():
    data = request.get_json()
    status_code, message = check_keys(['token', 'password'], data)

    if status_code < 400:
        status_code, message = validate_password(data['password'])
    
    if status_code < 400:
        ute = database_helper.read_password_reset_by_token(data['token'])
        if not ute:
            status_code = 404
            message = 'Token is invalid'
        else:
            user = ute[0]
    
    if status_code < 400:
        password = encrypt_password(data['password']).decode('utf-8')
        database_helper.update_password_by_username(user, password)
        database_helper.delete_password_reset_by_token(data['token'])
        message = 'Password updated successfully'
    
    response = {}
    response['message'] = message
    res = jsonify(response)
    res.status_code = status_code
    return res

@app.route('/reset_password/<token>')
@cross_origin()
def reset_password_page(token):
    print(token)
    ute = database_helper.read_password_reset_by_token(token)
    if not ute:
        return render_template('invalid-token.html')
    return render_template('password-reset.html')

@app.route('/request_password_reset')
@cross_origin()
def request_password_reset():
    return render_template('request-password-reset.html')

###########################
# HELPER FUNCTIONS
###########################
def check_keys(keys: list, data: dict) -> tuple[int, str]:
    """
    Checks if data contains the given keys.
    returns `(400, <error message>)`  if there are keys missing/`NoneType`, else `(200, '')`
    """
    missing_keys = [key for key in keys if key not in data.keys() or data[key] == None]

    success = not missing_keys
    message = '' if success else 'Invalid request! Missing the following data: ' + ', '.join(missing_keys)
    return (200 if success else 400, message)

def generate_token():
    """
    Generates and returns an auth token
    """
    return str(uuid4())

def validate_signup_data(data) -> tuple[int, str]:
    """
    Checks whether the signup data is valid (e.g. empty fields or invalid email)
    returns (False, <error message>) for invalid data, else (True, '')
    """
    for key in SIGNUP_KEYS:
        if len(data[key].strip()) == 0:
            return (400, key + ' is empty')
    if not re.match(r'.+@.+', data['email']):
        return (400, 'Email is not valid')
    if data['gender'].lower() not in ['male', 'female', 'other']:
        return (400, 'Gender is not valid')
    else:
        data['gender'] = data['gender'].upper()
    
    return (200, '')

def validate_password(password: str) -> tuple[int, str]:
    """
    Checks if the password is of valid length
    returns (False, 'Password is not long enough') if not, (True, '') if it is
    """
    # print(len(password), password)
    if password is None or len(password) < 8:
        return (400, 'Password is not long enough')
    return (200, '')

def change_user_password(token, data) -> tuple[int, str]:
    """
    Changes the users password.
    The data has to be of the following type:
    `{
    oldpassword: string,
    newpassword: string
    }`
    Returns `(success: boolean, success_message: string)`
    """
    # this should always return values, as the token is valid
    user, password = database_helper.read_user_and_password_by_token(token)

    success, message = check_password(data['oldpassword'], password)
    if not success:
        return (401, message)
    status_code, message = validate_password(data['newpassword'])
    if status_code >= 400:
        return (status_code, message)

    password = encrypt_password(data['newpassword']).decode('utf-8')
    database_helper.update_password_by_username(user, password)
    message = 'Password updated successfully'
    return (200, message)


# def login_user(username: str, password: str | bytes):
def login_user(username: str, password: "str | bytes") -> tuple[int, str]:
    """
    Tries to login the user with the given username and password.
    Returns `(status_code: int, success_message: string)`
    where status_code is:
    - 200 on successful login
    - 401 when username or password are wrong
    """
    # up = username + password
    up = database_helper.read_user_and_password_by_username(username)
    
    if up:
        username, checked_password = up
        success, message = (check_password(password, checked_password))
    else:
        success = False
        message = 'Invalid username'
    return (200 if success else 401, message)

def encrypt_password(password: "str | bytes") -> bytes:
    """
    Encrypts the password and returns it.
    """
    if (type(password) is str):
        password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt())

def check_password(password: "str | bytes", encrypted_password: "str | bytes") -> tuple[bool, str]:
    """
    Checks if `password` (unencrypted) matches with `encrypted_password` (encrypted).
    Returns `(success: bool, success_message: string)`
    """
    if (type(password) is str):
        password = password.encode('utf-8')
    if type(encrypted_password) is str:
        encrypted_password = encrypted_password.encode('utf-8')
    # print(password, encrypted_password)
    success = bcrypt.checkpw(password, encrypted_password)
    return (success, 'User signed in successfully' if success else 'Password invalid')

def get_user_messages(token: str, _user=None) -> tuple[int, str, list]:
    """
    Retrieves all the user messages of the given user with the given token.
    If user is None (default), the messages of the user with the given token will be retrieved instead.
    Returns: `(status_code: int, success_message: string, messages: list({ writer:string, message: string }))`

    Status codes:
    - 200: message retrieved successfully
    - 400: user to get messages from doesn't exist
    """
    messages = []    

    if _user and not database_helper.user_exists(_user):
        return (404, 'No user with this email exists', messages)
    
    user = database_helper.read_username_by_token(token)
    raw_messages = database_helper.read_messages_writer_and_text_by_user(_user if _user else user)
    message = 'Successfully retreived messages for user ' + user
    for m in raw_messages:
        messages.append({'writer': m[0], 'message': m[1], 'latitude': m[2], 'longitude': m[3]})

    return (200, message, messages)

def get_user_data(token: str, _user=None) -> tuple[int, str, list]:
    """
    Retrieves all the user data of the given user with the given token.
    If user is None (default), the data of the user with the given token will be retrieved instead.
    Returns: `(success: bool, success_message: string, user_data: list({ writer:string, message: string }))`
    """
    user_data = []

    user = database_helper.read_username_by_token(token)

    if _user and not database_helper.user_exists(_user):
        return (404, 'No user with this email exists', user_data)
    
    raw_data = database_helper.read_all_user_info(_user if _user else user)

    message = 'Successfully retreived data for user ' + user
    user_data = raw_data[:1] + raw_data[2:]
    
    return (200, message, user_data)

def save_user(user) -> tuple[int, str]:
    """
    Checks if the user already exists and if not saves the new user in the database.
    Returns `(201, message)` if insert was successful and `(409, message)` if user already exists
    """
    if database_helper.user_exists(user['email']):
        return (409, 'User with this email already exists')
    
    user = (user['email'], user['password'], user['firstname'], user['familyname'], user['gender'], user['city'], user['country'])
    database_helper.create_user(user)
    return (201, 'User created successfully')

def close_socket(email, manual_logout):
    print('trying to close socket', email, sockets)
    if email in sockets:
        print('closing socket', email)
        try:
            if not manual_logout:
                sockets[email].send('logout')
            sockets[email].close()
        except ConnectionClosed:
            print('socket with email', email, 'already closed')
        del sockets[email]