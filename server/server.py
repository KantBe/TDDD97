from flask import Flask, request
import json

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

@app.post('/sign_in')
def signin():
    print(request.data)
    data = json.loads(request.data)
    print(data)
    return '<p>Working</p>'

@app.put('/sign_up')
def signup():
    print(request.data)
    data = json.loads(request.data)
    success = True
    missing_keys = [key for key in SIGNUP_KEYS if key not in data.keys()]
    if (missing_keys):
        success = False
        message = 'Invalid request! Missing the following data: ' + ', '.join(missing_keys)
        
    if (success):
        pass

    response = {}
    response['success'] = success
    response['message'] = message
    return json.dumps(response)