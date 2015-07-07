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

@api.route('/user/<int:user_id>/match', methods=['GET'])
@login_required
def get_matches(user_id):
    if not (user_id == g.user.id or g.user.admin):
        return Response(status=403, response='cannot requested matches for a user other then yourself')
    if not(AppConfig.get('send_matches') or g.user.admin):
        return jsonify({})
    user = User.objects.get(id=user_id)
    users_who_like_me = user.who_like_me()
    matches = {u.id:u.contact_summary() for u in set(users_who_like_me).intersection(set(user.likes))}
    return jsonify(matches)
    #users_who_like_me = User.objects(likes__in=[user])


@api.route('/user/<int:user_id>/like', methods=['GET'])
@login_required
def get_likes(user_id):
    if not (user_id == g.user.id or g.user.admin):
        return Response(status=403, response='cannot see the likes for people other then yourself')
    try:
        #TODO: add logging
        user = User.objects.no_dereference().get(id=user_id)
        likes = [l.id for l in user.likes ]
        return Response(json.dumps(likes, default=json_util.default),  mimetype='application/json')
    except Exception, e:
        return Response(status=500, response="error while retrieving like")

@api.route('/user/<int:user_id>/like/<int:like_user_id>', methods=['POST', 'PUT'])
@login_required
def like_someone(user_id, like_user_id):
    if user_id == like_user_id:
        return Response(status=403, response='cannot like yourself!')
    if not (user_id == g.user.id or g.user.admin):
        return Response(status=403, response='cannot like for someone other then yourself')
    try:
        #user = User.objects.get(id=user_id)
        likie = User.objects.get(id=like_user_id)
        if User.objects(id=user_id, likes__in=[likie]).first():
            return Response(status=400, response='you have already liked this person')
        User.objects(id=user_id).update_one(push__likes=likie)
        user = User.objects.no_dereference().get(id=user_id)
        #Check if its a match
        if user in likie.likes:
            #TODO: add Logging
            #ITS A MATCH
            add_match(user.email, user.full_name(), user.id, likie.email, likie.full_name(), likie.id)
            add_match(likie.email, likie.full_name(), likie.id, user.email, user.full_name(), user.id)
        return Response(json.dumps([l.id for l in user.likes ], default=json_util.default),  mimetype='application/json')

    except Exception, e:
        #TODO: Add Logging
        return Response(status=500, response="error while adding like")


@api.route('/user/<int:user_id>/like/<int:unlike_user_id>', methods=['DELETE'])
@login_required
def unlike_someone(user_id, unlike_user_id):
    if not (user_id == g.user.id or g.user.admin):
        return Response(status=403, response='cannot unlike for someone other then yourself')
    try:
        unlikie = User.objects.get(id=unlike_user_id)
        User.objects(id=user_id).update_one(pull__likes=unlikie)
        user = User.objects.no_dereference().get(id=user_id)
        return Response(json.dumps([l.id for l in user.likes ], default=json_util.default),  mimetype='application/json')
    except Exception, e:
        #TODO: Add Logging
        return Response(status=500, response="error while unliking")