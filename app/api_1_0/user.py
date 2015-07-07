#! python
# -*- coding: utf-8 -*-

"""
"""
# ---------- Imports ----------
from flask import jsonify, request, current_app, url_for, g, abort, Response
from bson import json_util
from . import api
from ..models import User, AppConfig
from ..myauth import login_required
from ..email_service import send_login_email
import json
import random
import string

#mallformed endpoint? the logged in user isnt passed
@api.route('/user', methods=['GET'])
@login_required
def get_all_user_summaries():
    """GET /user?gender=M -> []UserSummary"""
    gender_filter = request.args.get('gender', None)
    if gender_filter == 'm' or gender_filter == 'M':
        users = User.all_guys()
    elif gender_filter == 'f' or gender_filter == 'F':
        users = User.all_girls()
    else:
        users = User.all_people()
    return Response(json.dumps([user.summary() for user in users]),  mimetype='application/json')

@api.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if (user_id != g.user.id) and not g.user.admin:
        return Response(status=403, response='requested user info for someone other then yourself')
    user = User.objects.get(id=user_id)
    return Response(json.dumps(user.to_dict(), default=json_util.default),  mimetype='application/json')

@api.route('/user', methods=['POST'])
@login_required
def create_user():
    """POST /user with payload
    {
        "first_name": "Doug",
        "last_name": "*****",
        "email": "******@mailinator.com",
        "gender": "M",
        "age": 26,
    }"""
    if not g.user.admin:
        return Response(status=403, response='must be admin to create user')
    data = request.json
    if not all(k in data for k in ('first_name', 'last_name', 'email', 'gender', 'age')):
        return Response(status=400, response="a required field is missing - 'first_name', 'last_name', 'email', 'gender', 'age'")
    try:
        gender = data['gender']
        if gender != 'M' and gender != 'F':
            return Response(status=400, response="gender must be either 'M' or 'F' ")
        first_name = data['first_name'].strip().title()
        last_name = data['last_name'].strip().title()
        email = data['email'].strip()
        age = int(data['age'])
        #TODO: must fix!!!!!!!!!!
        password = data.get('password') if 'password' in  data else ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(6))
        admin = data.get('admin', False)
        user = User(first_name=first_name, last_name=last_name, email=email, age=age, gender=gender, password=password, admin=admin)
        user.save()
        #TODO: Add Logging - about to send email
        if AppConfig.get('send_invites_on_user_creation'):
            user = user.send_invite_email()
        return Response(json.dumps(user.to_dict(), default=json_util.default),  mimetype='application/json')
    except Exception:
        return Response(status=500, response="error while creating a user")

@api.route('/user/reissue', methods=['PUT'])
def reissue_password():
    """PUT /user/reissue
        {"email": "******@gmail.com"}"""
    data = request.json
    if 'email' not in data:
        return Response(status=400, response="a required field is missing - 'email'")
    user = User.objects.get(email=data['email']) or None
    if not user:
        return Response(status=400, response="no matching email address found please contact stacy miller about account setup")

    app_url = AppConfig.get('app_url') or 'http://www.*****.com'
    #TODO: could add reset password function here
    #TODO: add Logging
    send_login_email(user.email, user.full_name(), user.password, app_url)
    return Response(status=204, response='email with user name and password has be resent')

