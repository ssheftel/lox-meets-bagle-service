#! python
# -*- coding: utf-8 -*-

"""
"""
# ---------- Imports ----------
from flask import jsonify, request, current_app, url_for, g, abort, Response
from bson import json_util
from . import api
from ..models import User
from ..myauth import login_required
from ..photo_service import allowed_formats, upload_image
import json


@api.route('/user/<int:user_id>/photo', methods=['POST', 'PUT'])
@login_required
def upload_photo(user_id):
    if not (user_id == g.user.id or g.user.admin):
        return Response(status=403, response='requested user info for someone other then yourself')
    try:
        user = User.objects.get(id=user_id)
        if not user:
            return Response(status=400, response='no user exists with the given user_id')
        file = request.files['file']
        if not (file and allowed_formats(file.filename)):
            return Response(status=400, response='issue with photo upload make sure its a jpg file')
        (name, resp) = upload_image(user_id, file)
        if not name:
            return Response(status=500, response="image_upload call failed")
        user.has_photo = True
        user.photo_name = name
        user.save()
        photo_attributes = {'photo_name':user.photo_name, 'has_photo':user.has_photo}
        return jsonify(photo_attributes)
    except Exception, e:
        #TODO: add logging here
        return Response(status=500, response="error while uploading photo")


@api.route('/user/<int:user_id>/bio', methods=['POST', 'PUT'])
@login_required
def save_bio(user_id):
    if not (user_id == g.user.id or g.user.admin):
        return Response(status=403, response='requested user info for someone other then yourself')
    try:
        user = User.objects.get(id=user_id)
        if not user:
            return Response(status=400, response='no user exists with the given user_id')
        data = request.json
        if 'bio' not in data:
            return Response(status=400, response='payload must contain bio text in a object {bio: "bio text""}')
        bio = data.get('bio', '')
        user.bio = bio
        user.save()
        return jsonify({"bio": bio})
    except Exception:
        #TODO: add logging here
        return Response(status=500, response="error while saving bio")
