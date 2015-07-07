#! python
# -*- coding: utf-8 -*-

"""
"""
# ---------- Imports ----------
import os
import boto.sqs
from boto.exception import SQSError
import json
from time import strftime, gmtime
from boto.sqs.message import RawMessage


aws_access_key_id = os.environ.get('S3_KEY')
aws_secret_access_key = os.environ.get('S3_SECRET')
match_queue_name = os.environ.get('MATCH_QUEUE')


conn = boto.sqs.connect_to_region('us-east-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
q = conn.create_queue(match_queue_name, 180)
q.set_message_class(RawMessage)

def add_match(users_email, users_name, users_id, match_email, match_name, match_user_id):
    """called one for each side of match"""
    try:
        data = {
            'submitdate': strftime("%Y-%m-%dT%H:%M:%S", gmtime()),
            'user': {
                'email': users_email,
                'name': users_name,
                'user_id': users_id
            },
            'match': {
                'email': match_email,
                'name': match_name,
                'user_id': match_user_id
            }
        }
        m = RawMessage()
        m.set_body(json.dumps(data))
        # TODO: Add Logging
        status = q.write(m)
        return status
    except SQSError, e:
        #TODO ADD Logging
        return False
    except Exception, e:
        #TODO: Add Logging
        return False