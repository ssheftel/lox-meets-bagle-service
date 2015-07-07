#! python
# -*- coding: utf-8 -*-

"""
"""
# ---------- Imports ----------
from . import db
from mongoengine import DoesNotExist, PULL
import random
import datetime
import time
import string
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from .lox_utils import memoize_with_timeout
from .email_service import send_login_email, mock_address

# TODO: Move to config.py or envvar
SECRET_KEY = '************'

#send_matches
# send_invites
# app_url
# send_invites_on_user_creation,
# mock_email_address (either suffix str or '' implying no mocking)
# vip_mids array of ids (vip men ids will select one of them to add to each recommendation)
# vip_gids array of ids
class AppConfig(db.Document):
    name = db.StringField(required=True, unique=True)
    value = db.DynamicField(required=True)

    meta = {
        'indexes': ['name']
    }

    def __repr__(self):
        return "AppConfig(name=%r, value=%r)" % (self.name, self.value)

    def to_dict(self):
        return {
            'name': self.name,
            'value': self.value
        }

    @classmethod
    @memoize_with_timeout(timeout=5 * 60)
    def get(cls, name):
        try:
            doc = cls.objects.get(name=name)
            if doc:
                return doc.value
            else:
                return None
        except (DoesNotExist, Exception) as e:
            return None


class User(db.Document):
    id = db.SequenceField(primary_key=True)
    first_name = db.StringField(min_length=2, max_length=60, required=True)
    last_name = db.StringField(min_length=1, max_length=60, required=True)
    email = db.EmailField(required=True, unique=True)
    #password = db.StringField(max_length=50,required=True, default=lambda : ''.join(random.choice(string.ascii_lowercase+string.digits) for _ in range(6)))
    password = db.StringField(max_length=50, required=True)
    sent_login_email = db.BooleanField(default=False)
    gender = db.StringField(required=True, choices=('M', 'F'))
    bio = db.StringField(max_length=500, default='')
    likes = db.ListField(db.ReferenceField('self', reverse_delete_rule=PULL))
    dislikes = db.ListField(db.ReferenceField('self', reverse_delete_rule=PULL))
    suggested_matches = db.ListField(db.ReferenceField('self', reverse_delete_rule=PULL))
    age = db.IntField()
    admin = db.BooleanField(default=False)
    date_added = db.DateTimeField(default=datetime.datetime.now)
    has_photo = db.BooleanField(default=False)
    photo_name = db.StringField(default='default_face')
    questions = db.DictField()
    meta = {
        'indexes': ['email', 'gender', 'age', 'date_added', 'likes', 'first_name']
    }

    def __repr__(self):
        return "User(id=%r, first_name=%r, last_name=%r, email=%r, password=%r, sent_login_email=%r, gender=%r, photo_name=%r)" % (
        self.id, self.first_name, self.last_initial,
        self.email, self.password, self.sent_login_email,
        self.gender, self.photo_name)

    @property
    def attracted_to(self):
        return 'F' if self.gender == 'M' else 'M'

    @property
    def last_initial(self):
        initial = ''
        if self.last_name and len(self.last_name) > 0:
            initial = self.last_name[0]
            initial = initial.upper()
        return initial

    def full_name(self):
        return '%s %s' % (self.first_name, self.last_initial)


    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_initial,
            'email': self.email,
            'password': self.password,
            'sent_login_email': self.sent_login_email,
            'gender': self.gender,
            'attracted_to': self.attracted_to,
            'questions': self.questions,
            'bio': self.bio,
            'likes': [like.id for like in self.likes],
            'dislikes': [dislike.id for dislike in self.dislikes],
            'suggested_matches': [suggested_match.id for suggested_match in self.suggested_matches],
            'age': self.age,
            'admin': self.admin,
            'date_added': self.date_added,
            'has_photo': self.has_photo,
            'photo_name': self.photo_name
        }

    def summary(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_initial,
            'gender': self.gender,
            'attracted_to': self.attracted_to,
            'bio': self.bio,
            'has_photo': self.has_photo,
            'questions': self.questions,
            'photo_name': self.photo_name
        }

    def contact_summary(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_initial,
            'gender': self.gender,
            'attracted_to': self.attracted_to,
            'email': self.email,
            'bio': self.bio,
            'has_photo': self.has_photo,
            'photo_name': self.photo_name,
            'questions': self.questions
        }

    def who_like_me(self):
        return User.objects(likes__in=[self])

    def send_invite_email(self):
        if AppConfig.get('send_invites'):
            app_url = AppConfig.get('app_url')
            email = self.email
            if AppConfig.get('mock_email_address'):
                email = mock_address(email, AppConfig.get('mock_email_address'))
            send_login_email(email, self.full_name(), self.password, app_url)
            self.sent_login_email = True
            self.save()
            return self
        return self

    def generate_suggested_matches(self):
        """
        populates the suggested matches by randomly pick others user of the
        opposite gender who are within given age bounds. also if vip users are
        defined it will add one of them to the suggested matches

        :param max_suggestions:
        :return:
        """
        if self.gender == 'M': # if user is a guy
            lower_diff = -4
            upper_diff = 3
            vips = AppConfig.get('vip_gids')# show guys the vip girls
        else: # its a girl
            lower_diff = -2
            upper_diff = 6
            vips = AppConfig.get('vip_mids') # show girls the vip guys
        lower_bound = self.age + lower_diff
        upper_bound = self.age + upper_diff
        in_age_range = list(User.objects.no_dereference().filter(gender=self.attracted_to, age__gte=lower_bound, age__lte=upper_bound)[:35])
        random.shuffle(in_age_range)
        suggested_matches = in_age_range[:3] # select up to three randomly
        for suggested_match in suggested_matches:
            self.suggested_matches.append(suggested_match)
        if vips:
            vip_id = random.choice(vips)
            vip_user = User.objects.no_dereference().get(id=vip_id)
            if vip_user and vip_user not in suggested_matches:
                self.suggested_matches.append(vip_user)
        self.save()
        return self


    @classmethod
    def generate_all_suggested_matches(cls):
        for user in User.objects().no_dereference():
            if len(user.suggested_matches) == 0:
                user.generate_suggested_matches()
        return True

    @classmethod
    def all_guys(cls, all_fields=False):
        if all_fields:
            return cls.objects.filter(gender='M').order_by('+id')
        else:
            return cls.objects.filter(gender='M').only('id', 'first_name', 'last_name', 'bio', 'has_photo',
                                                       'photo_name', 'questions').order_by('+id')


    @classmethod
    def all_girls(cls, all_fields=False):
        if all_fields:
            return cls.objects.filter(gender='F').order_by('+id')
        else:
            return cls.objects.filter(gender='F').only('id', 'first_name', 'last_name', 'bio', 'has_photo',
                                                       'photo_name', 'questions').order_by('+id')

    @classmethod
    def all_people(cls, all_fields=False):
        if all_fields:
            return cls.objects.order_by('+id')
        else:
            return cls.objects.only('id', 'first_name', 'last_name', 'bio', 'has_photo', 'photo_name',
                                    'questions').order_by('+id')

    @classmethod
    def send_all_invite_emails(cls):
        for user in User.objects.filter(sent_login_email=False):
            user.send_invite_email()
        return True

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def verify_password(self, password):
        #TODO: store password hash not raw value and use pwd_context.verify(password, self.password)
        return password == self.password

    def generate_auth_token(self, expiration=10800):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user = User.objects.get(id=data['id'])
        return user


# ----------------------------------------------------------------------------


