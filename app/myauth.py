"""
"""
from flask import g, request, Response
from . import db
from .models import User
from functools import wraps
def valid_credentials(email_and_password_or_token):
    if ':' in email_and_password_or_token:
        (email, password) = email_and_password_or_token.split(':')
        token = None
        user = User.objects.get(email=email)
        if user and user.verify_password(password):
            return user

    else:
        email = None
        password = None
        token = email_and_password_or_token
        user = User.verify_auth_token(token)
        if user:
            return user
    return False


    return username == app.config['USER'] and password == app.config['PASS']

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('TOKEN')
        if not token or not valid_credentials(token):
            return Response('Login!', 401, {'TOKEN': 'Login!'})
        g.user = valid_credentials(token)
        return f(*args, **kwargs)
    return wrapper
