from flask import g
from . import auth
from . import db
from .models import User
@auth.verify_password
def verify_password(email_or_token, password):
    try:

        # first try to authenticate by token
        user = User.verify_auth_token(email_or_token)
        if not user:
            # try to authenticate with username/password
            user = User.objects.get(email=email_or_token)
            if not user or not user.verify_password(password):
                return False
        g.user = user
        return True
    except Exception:
        #TODO: add loggin statment here noting that user auth failed
        return False