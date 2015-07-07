#! python
# -*- coding: utf-8 -*-

"""
"""
# ---------- Imports ----------
import os
import boto.sqs
from boto.exception import SQSError
import json
from boto.sqs.message import RawMessage
import time
import os
import boto.ses
import mongoengine
from mongoengine import connect, Document, StringField, DynamicField

import logging
level = logging.INFO
handler = logging.StreamHandler()
handler.setLevel(level)
#handler.setFormatter('%(asctime)s [%(process)d] [%(levelname)s] pathname=%(pathname)s lineno=%(lineno)s funcname=%(funcName)s %(message)s')
#handler.setFormatter('%(levelname)s: %(message)s')
logger = logging.getLogger('info')
logger.addHandler(handler)
logger.setLevel(level) #even if not required...
logger.info('logging test')

logger.info('starting up match_worker')
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

AWS_ACCESS_KEY_ID = os.environ.get('S3_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('S3_SECRET')
MATCH_QUEUE_NAME = os.environ.get('MATCH_QUEUE')
MONGODB_URL_WITH_DB = os.environ.get('MONGODB_URL_WITH_DB')
MONGODB_DB = os.environ.get('MONGODB_DB')
FROM_ADDRESS = os.environ.get('FROM_EMAIL_ADDRESS') or '**********@**********.com'

conn = boto.sqs.connect_to_region('us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
q = conn.create_queue(MATCH_QUEUE_NAME, 180)
q.set_message_class(RawMessage)
ses = boto.ses.connect_to_region('us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
connect(MONGODB_DB, host=MONGODB_URL_WITH_DB)

MATCH_NOTIFICATION_SUBJECT_TPL = "Congratulation you have matched with {name}!"
MATCH_NOTIFICATION_MESSAGE_TPL = """
Congratulation you have matched with {name}! You can contact them at the email address: {email}. It's time to setup a date so go ahead and send them a email!

Regards
Jewish Robot

---
Sent via electronic mail
"""

# MongoDB Accees setup
class memoized_ttl(object):
    """Decorator that caches a function's return value each time it is called within a TTL
    If called within the TTL and the same arguments, the cached value is returned,
    If called outside the TTL or a different value, a fresh value is returned.
    """
    def __init__(self, ttl):
        self.cache = {}
        self.ttl = ttl
    def __call__(self, f):
        def wrapped_f(*args):
            now = time.time()
            try:
                value, last_update = self.cache[args]
                if self.ttl > 0 and now - last_update > self.ttl:
                    raise AttributeError
                #print 'DEBUG: cached value'
                return value
            except (KeyError, AttributeError):
                value = f(*args)
                self.cache[args] = (value, now)
                #print 'DEBUG: fresh value'
                return value
            except TypeError:
                # uncachable -- for instance, passing a list as an argument.
                # Better to not cache than to blow up entirely.
                return f(*args)
        return wrapped_f

#send_matches, send_invites
class AppConfig(Document):
    name = StringField(required=True, unique=True)
    value = DynamicField(required=True)

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
    @memoized_ttl(5*60)
    def get(cls, name):
        logger.info('looking up AppConfig value')
        try:
            #doc = AppConfig.objects(name=name).first()
            doc = cls.objects.get(name=name)
            if doc:
                return doc.value
            else:
                logger.info('Failed to get AppConfig %s = %r' % (name, doc.value) )
                return None
        except (Exception) as e:
            logger.error('Failed to get AppConfig value', exc_info=True)
            return None

def generate_match_notification_message(userObj, matchUserObj):
    try:
        if not('email' in userObj and 'name' in matchUserObj and 'email' in matchUserObj):
            logger.error('attempt to generate {to, subject, body} dict from user and match user FAILED!')
            return None
        data = {
            'to': userObj['email'],
            'subject': MATCH_NOTIFICATION_SUBJECT_TPL.format(name=matchUserObj['name']),
            'body': MATCH_NOTIFICATION_MESSAGE_TPL.format(name=matchUserObj['name'], email=matchUserObj['email'])
        }
        return data
    except Exception, e:
        logger.error('attempt to generate {to, subject, body} dict from user and match user FAILED!', exc_info=True)
        return None

def send_match_notification_email(to, subject, body):
    return ses.send_email(FROM_ADDRESS, subject, body, [to])

def processes_q():
    try:
        if AppConfig.get('send_matches'):
            #logger.info('about check match_queue for new matches')
            #logger.info('currently there are %r match messages in the match_queue' % q.count())
            if q.count():
                logger.info('currently there are %r match messages in the match_queue' % q.count())
            for m in q.get_messages():
                try:
                    msg = json.loads(m.get_body())
                    email_props = generate_match_notification_message(msg['user'], msg['match'])
                    if not email_props:
                        logger.error('was unable to extract email properties from queue values, skiping to next queue message', exc_info=True)
                        continue
                    logger.info('about to sent match email to %r with subject of %r' % (email_props['to'], email_props['subject']))
                    send_match_notification_email(**email_props)

                    logger.info('email sent to %r' % email_props['to'])
                    q.delete_message(m)
                    logger.info('message deleted from queue')
                except Exception, e:
                    logger.error('error while trying to send a match email from match_que data', exc_info=True)
                    continue
            return True
        else:
            logger.info('match message sending is turned off')
    except Exception, e:
        logger.error('error while trying loop through match_queue', exc_info=True)
        return None

def worker(sleep_time=0.01):
    try:
        while True:
            processes_q()
            time.sleep(sleep_time)
    except Exception, e:
        logger.error('Error during execution of match worker loop', exc_info=True)

if __name__ == '__main__':
    worker()

