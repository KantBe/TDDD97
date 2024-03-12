import sqlite3
from flask import g
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
    # print(query, args)
    cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    if commit:
        get_db().commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv


###########
#   USER
###########
def create_user(user: tuple[str, str, str, str, str, str, str]):
    return query_db("INSERT INTO user VALUES(?, ?, ?, ?, ?, ?, ?)", args=user, commit=True)

def get_user_by_username(username):
    return query_db("SELECT username FROM user WHERE username LIKE '%s'" % (username), one=True)

def user_exists(username):
    return True if get_user_by_username(username) else False

def get_user_and_password_by_username(username):
    return query_db("SELECT username, password FROM user WHERE username LIKE '%s'" % (username), one=True)

def get_user_and_password_by_token(token):
    return query_db("SELECT u.username, u.password FROM user u "\
        + "JOIN user_session us ON us.user = u.username WHERE us.token LIKE '%s'" % (token), one=True)

def get_username_by_token(token):
    return query_db("SELECT u.username FROM user u "\
        + "JOIN user_session us ON us.user = u.username WHERE us.token LIKE '%s'" % (token), one=True)[0]

def update_password_by_username(username, password):
    return query_db("UPDATE user SET password = '%s' WHERE username LIKE '%s'" % (password, username), commit=True)

def get_all_user_info(username):
    return query_db("SELECT * FROM user WHERE username LIKE '%s'" % (username), one=True)

#############
#   SESSION
#############

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

def get_sessions_by_user(username):
    return query_db("SELECT * FROM user_session WHERE user LIKE '%s'" % username, one=False)

def get_session_by_token(token):
    return query_db("SELECT * FROM user_session WHERE token LIKE '%s'" % token, one=True)#

def delete_session_by_user(username):
    # sql = "DELETE FROM user_session WHERE user LIKE '%s' AND expires <= datetime('now')" % (username)
    # we remove all sessions
    sql = "DELETE FROM user_session WHERE user LIKE '%s'" % (username)
    ret = query_db(sql, commit=True)
    print(ret)

def delete_session_by_token(token):
    query_db("DELETE FROM user_session WHERE token = '%s'" % (token), commit=True)
    return

###########
#   POSTS
###########

def get_messages_writer_and_text_by_user(user):
    return query_db("SELECT writer, posttext FROM post WHERE user LIKE '%s' ORDER BY id ASC" % (user))

def insert_message(writer, message, user):
    return query_db("INSERT INTO post(writer, posttext, user) VALUES(?, ?, ?)", args=(writer, message, user), commit=True)