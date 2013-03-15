from boto.ses.connection import SESConnection
from myproject.settings_local import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, TO_EMAIL, FROM_EMAIL


def send_email(subject, body):
    connection = SESConnection(aws_access_key_id=AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    connection.send_email(FROM_EMAIL, subject, body, TO_EMAIL)