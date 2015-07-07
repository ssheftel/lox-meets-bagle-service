#! python
# -*- coding: utf-8 -*-

"""
"""
# ---------- Imports ----------
from flask import jsonify, request, current_app, url_for, g, abort
from . import api
from ..models import User
from ..myauth import login_required

@api.route('/token', methods=['POST'])
def get_auth_token_from_username_and_password():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None:
            abort(400) # missing arguments
    user = User.objects.get(email=email)
    if user is None:
        abort(400)
    if user.verify_password(password):
        token = user.generate_auth_token()
        return jsonify({ 'token': token.decode('ascii'), 'id': user.id, 'gender': user.gender })
    else:
        abort(400)


@api.route('/token', methods=['GET'])
@login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii'), 'id': g.user.id, 'gender': g.user.gender })

# ----------------------------------------------------------------

@api.route('/context', methods=['POST'])
def get_new_context_from_username_and_password():
    email = request.json.get('email')
    password = request.json.get('password')
    if email is None or password is None:
            abort(400) # missing arguments
    user = User.objects.get(email=email)
    if user is None:
        abort(400)
    if user.verify_password(password):
        userContext = user.to_dict()
        token = user.generate_auth_token()
        userContext['token'] = token.decode('ascii')
        return jsonify(userContext)
    else:
        abort(400)


@api.route('/context', methods=['GET'])
@login_required
def get_context():
    token = g.user.generate_auth_token()
    userContext = g.user.to_dict()
    userContext['token'] = token.decode('ascii')
    return jsonify(userContext)