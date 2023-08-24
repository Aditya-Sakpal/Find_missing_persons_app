from fastapi.routing import APIRouter
from itsdangerous import URLSafeSerializer
import secrets

from itsdangerous.exc import BadSignature
from sendgrid.helpers.mail.content import Content
from sendgrid.helpers.mail.email import Email
from sendgrid.helpers.mail.mail import Mail
from sendgrid.helpers.mail.to_email import To

from config import default_log
from itsdangerous.url_safe import URLSafeTimedSerializer

import config
from data.db.init_db import get_db
from data.dbapi.user_dbapi import read_queries
from data.dbapi.user_dbapi.read_queries import find_by_email
from data.models.users import Users
from decorators.handle_generic_exception import frontend_api_generic_exception
from logic.auth.token_management import create_access_token

import sendgrid
import os
from sendgrid.helpers.mail import *


@frontend_api_generic_exception
def add_new_otp(user):
    """Add a new one-time password to enable password reset

    """
    db = next(get_db())

    default_log.debug("Adding new one time password for " + user.email)
    user.one_time_password = secrets.token_hex(3)
    serializer = URLSafeSerializer(config.secret_key)
    hashed_one_time_password = serializer.dumps(user.one_time_password,
                                                salt=config.security_password_salt)
    db.add(user)
    db.commit()
    return hashed_one_time_password


@frontend_api_generic_exception
def generate_reset_pwd_token(user):
    '''
    '''
    serializer = URLSafeTimedSerializer(config.secret_key)
    email = user.email
    hashed_one_time_password = add_new_otp(user)

    email_token = serializer.dumps(
        email, salt=config.security_password_salt)

    return email_token, hashed_one_time_password


#TODO: Use FastAPI-Users library
@frontend_api_generic_exception
def send_reset_password_email(to: str) -> object:
    user = find_by_email(to)

    email_token, hashed_one_time_password = generate_reset_pwd_token(user)

    url_for_request = config.reset_password_url + f"?email_token={email_token}&" \
                                        f"hashed_one_time_password={hashed_one_time_password}"

    config.default_log.debug(f"Sending reset password mail to {to}. URL = {config.reset_password_url}")

    html = f"""
    Click here to reset password<b/>
    {url_for_request}
    """

    default_log.debug(html)


    #TODO: use send_mail function()
    sg = sendgrid.SendGridAPIClient(api_key=config.sendgrid_api_key)
    from_email = Email(config.sendgrid_email_address)
    to_email = To(to)
    subject = "Reset password"
    content = Content("text/plain", html)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    default_log.debug(response.status_code)
    default_log.debug(response.body)
    default_log.debug(response.headers)


@frontend_api_generic_exception
def validate_email_token(token, expiration=300):
    serializer = URLSafeTimedSerializer(config.secret_key)
    try:
        email = serializer.loads(
            token,
            salt=config.security_password_salt,
            max_age=expiration
        )
    except:
        return False
    return email


def validate_otp(user, hashed_one_time_password):
    one_time_password = user.one_time_password
    serializer = URLSafeSerializer(config.secret_key)
    try:
        deserialized_otp = serializer.loads(
            hashed_one_time_password, salt=config.security_password_salt)
    except BadSignature as ex:
        default_log.exception(ex)
        return False
    if deserialized_otp != one_time_password:
        raise ValueError('Token has Expired.')
    add_new_otp(user)
    return True


def get_email_from_reset_password_request(email_token, hashed_one_time_password):
    default_log.debug("Processing reset password")
    email = validate_email_token(email_token)
    if email:
        user = read_queries.find_by_email(email)
        if validate_otp(user, hashed_one_time_password):
            return email

    return False

