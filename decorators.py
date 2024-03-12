from flask import request, jsonify, make_response, Response
from database_helper import get_session_by_token

def check_token_validity() -> Response | str:
    token = request.headers.get('Authorization')
    if not token and request.method != 'GET':
        data = request.get_json()
        token = data['token'] if 'token' in data else None
    if not token and request.method == 'GET':
        data = request.args
        token = data['token'] if 'token' in data else None
    
    if token is None or not is_token_valid(token):
        res = jsonify({'message': 'Invalid token'})
        res.status_code = 401
        return res
    return token


def is_token_valid(token: str) -> bool:
    """
    Checks if the given token is valid and returns the corresponding user and password if it is.
    Returns the following tuple:
    `(success: boolean, success_message: string, user: string | None, password: string | None)`
    """
    if token is None:
        return False
    session = get_session_by_token(token)
    print(session)
    if not session:
        return False
    return session


def authorized(func):
    def wrapper(*args, **kwargs):
        check = check_token_validity()
        if type(check) is Response:
            return check
        token = check
        try:
            res = func(token, *args, **kwargs)
        except Exception:
            res = jsonify({'message', 'Server error'})
            res.status_code = 500
        return res
    
    wrapper.__name__ = func.__name__
    return wrapper
