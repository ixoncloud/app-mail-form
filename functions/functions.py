import smtplib
from email.mime.text import MIMEText

from ixoncdkingress.cbc.context import CbcContext


@CbcContext.expose
def send_email(context: CbcContext, subject: str, message: str):
    smtp_server = context.config.get('smtp_server')
    smtp_ssl_port = context.config.get('smtp_ssl_port')
    smtp_user = context.config.get('smtp_user')
    smtp_password = context.config.get('smtp_password')

    ixon_user = _get_user(context)

    combined_message = f"{message} \n\nThis message was sent by {ixon_user['name']} ({ixon_user['emailAddress']}) \nFrom device: {context.agent_or_asset.name}, with publicId: {context.agent_or_asset.public_id}"

    msg = MIMEText(combined_message)

    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = smtp_user

    server = smtplib.SMTP_SSL(smtp_server, smtp_ssl_port)

    try:
        # using SMTP_SSL here, with the default port for SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_ssl_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    return {'status': 'success'}


def _get_user(context: CbcContext):
    response = context.api_client.get(
        'User', url_args={'publicId': context.user.public_id},
        query={"fields": "name,emailAddress,memberships.group"})
    return response['data']
