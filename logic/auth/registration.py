from itsdangerous.url_safe import URLSafeTimedSerializer
from sendgrid.helpers.mail.content import Content
from sendgrid.helpers.mail.email import Email
from sendgrid.helpers.mail.mail import Mail
from sendgrid.helpers.mail.to_email import To
from sendgrid.sendgrid import SendGridAPIClient
from config import default_log
import config


def send_verification_mail(to):
    serializer = URLSafeTimedSerializer(config.secret_key)
    email_token = serializer.dumps(to, salt=config.security_password_salt)

    url_for_request = config.new_user_verification_url + f"?email_token={email_token}"

    config.default_log.debug(f"Sending verification mail to {to}. "
                             f"URL = {config.new_user_verification_url}")

    html = f"""
        Click here to verify<b/>
        {url_for_request}
        """

    #TODO: use send_mail function
    sg = SendGridAPIClient(api_key=config.sendgrid_api_key)
    from_email = Email(config.sendgrid_email_address)
    to_email = To(to)
    subject = "Verify email"
    content = Content("text/plain", html)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    default_log.debug(response.status_code)
    default_log.debug(response.body)
    default_log.debug(response.headers)


