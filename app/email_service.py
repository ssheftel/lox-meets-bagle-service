import os
import boto.ses

aws_access_key_id = os.environ.get('S3_KEY')
aws_secret_access_key = os.environ.get('S3_SECRET')
FROM_ADDRESS = os.environ.get('FROM_EMAIL_ADDRESS') or 'jewish_robot@loxmeetsbagel.com'
conn = boto.ses.connect_to_region('us-east-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

def send_email(to, subject, body):
    return conn.send_email(FROM_ADDRESS, subject, body, [to])


USER_LOGIN_EMAIL_SUBJECT = "Lox Meets Bagel Speed Dating App Login Info"
USER_LOGIN_EMAIL_MESSAGE = """
Hi {name}! We are very exited that you will be participating in the Lox Meets Bagel Speed Dating event this Wednesday February 4th.
Before the event please sign into the Lox Meets Bagel web app ({app_url}) and upload your photo.
Your Login is as follows:
Email: {to}
Password: {password}

Regards
Jewish Robot

---
Sent via electronic mail
"""
def send_login_email(to, name, password, app_url):
    subject = USER_LOGIN_EMAIL_SUBJECT
    body = USER_LOGIN_EMAIL_MESSAGE.format(name=name, app_url=app_url, to=to, password=password)
    #TODO: Add Logging Here
    return send_email(to, subject, body)

def mock_address(real_address, mock_domain):
    return real_address[:real_address.find('@')] + mock_domain