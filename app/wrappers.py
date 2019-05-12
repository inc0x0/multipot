from functools import wraps
from flask import request, jsonify
from config import Config


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')
        if token is None or token != Config.ANALYSIS_TOKEN:
            response = jsonify({'message': 'Missing authentication'})
            return response, 403
        return f(*args, **kwargs)
    return decorated_function
