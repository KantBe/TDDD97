from flask import request, jsonify

def authorized(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token and request.method != 'GET':
            data = request.get_json()
            token = data['token'] if 'token' in data else None
        if not token and request.method == 'GET':
            data = request.args
            token = data['token'] if 'token' in data else None
        print(request.method, token)
        
        if not token or token is None:
            return jsonify({'success': False, 'message': 'Invalid token'})
        return func(token, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
