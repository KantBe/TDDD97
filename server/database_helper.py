import sqlite3
from flask import g
import bcrypt
import datetime

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def query_db(query, args=(), one=False, commit=False):
    print(query, args, type(args))
    cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    if commit:
        get_db().commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def save_user(user):
    existing_user = get_user_by_username(user['email'])
    if existing_user:
        return (False, 'User with this email already exists')
    
    user = (user['email'], user['password'], user['firstname'], user['familyname'], user['gender'], user['city'], user['country'])
    sql = "INSERT INTO user VALUES(?, ?, ?, ?, ?, ?, ?)"
    cur = get_db().cursor()
    cur.execute(sql, user)
    get_db().commit()
    return (True, 'User created successfully')

def login_user(username, password):
    # up = username + password
    up = get_user_and_password_by_username(username)
    
    if up:
        username, checked_password = up
        success = (check_password(password, checked_password))
        message = 'User signed in successfully'
        if not success:
            message = 'Invalid password'
    else:
        success = False
        message = 'Invalid username'
    return (success, message)

def store_token(token, user):
    """
    This method is called if the login was successfully, so the token is stored successfully.
    
    To keep the stored data minimal, we also delete the token at the very beginning.
    """
    delete_session_by_user(user)
    sql = "INSERT INTO user_session(token, user, expires) VALUES(?, ?, ?)"
    data = (token, user, datetime.datetime.now() + datetime.timedelta(days=1))
    query_db(sql, args=data, commit=True)
    return (True, 'Token stored in database')

def get_user_by_username(username):
    return query_db("SELECT username FROM user WHERE username LIKE '%s'" % (username), one=True)

def get_user_and_password_by_username(username):
    return query_db("SELECT username, password FROM user WHERE username LIKE '%s'" % (username), one=True)

def get_all_user_info(username):
    return query_db("SELECT * FROM user WHERE username LIKE '%s'" % (username), one=True)

def get_sessions_by_user(username):
    return query_db("SELECT * FROM user_session WHERE user LIKE '%s'" % username, one=False)

def get_session_by_token(token):
    return query_db("SELECT * FROM user_session WHERE token LIKE '%s'" % token, one=True)

def delete_session_by_user(username):
    sql = "DELETE FROM user_session WHERE user LIKE '%s' AND expires <= datetime('now')" % (username)
    ret = query_db(sql, commit=True)
    print(ret)

def delete_session_by_token(token):
    query_db("DELETE FROM user_session WHERE token = '%s'" % (token), commit=True)

def encrypt_password(password):
    if (type(password) is str):
        password = password.encode('utf-8')
    return bcrypt.hashpw(password, bcrypt.gensalt())

def check_password(password, encrypted_password):
    if (type(password) is str):
        password = password.encode('utf-8')
    if type(encrypted_password is str):
        encrypted_password = encrypted_password.encode('utf-8')
    return bcrypt.checkpw(password, encrypted_password)