#! python
# -*- coding: utf-8 -*-

"""
"""
# ---------- Imports ----------
from flask import jsonify, request, current_app, url_for, g, abort, Response
from . import api
from ..models import User, AppConfig
from ..myauth import login_required
from ..match_queue_service import add_match
import json
from bson import json_util

@api.route('/admin/data_setup/suggested_matches', methods=['PUT'])
@login_required
def generate_suggested_matches():
    if not g.user.admin:
        return Response(status=403, response='Must Be Admin')
    for u in User.objects():
        u.suggested_matches = []
        u.save()
    User.generate_all_suggested_matches()
    return jsonify({'msg':'suggested matches have been generate'})

# -------------------------------------------------------------------

@api.route('/admin/all_users', methods=['GET'])
@login_required
def get_all_user_data():
    if not g.user.admin:
        return Response(status=403, response='Must Be Admin')
    users = [user.to_dict() for user in  User.objects.no_dereference()]
    return Response(json.dumps(users, default=json_util.default), mimetype='application/json')