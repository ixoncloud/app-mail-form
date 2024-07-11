import smtplib
from email.mime.text import MIMEText

from ixoncdkingress.function.context import FunctionContext

from functions.types import ErrorResponse, MailConfig, SuccessResponse


def get_user(context: FunctionContext) -> tuple[str, str] | ErrorResponse:
    """
    Return the full name and email address of the user that invokes the cloud function.
    """
    if not context.user:
        return ErrorResponse("No user specified")

    response = context.api_client.get(
        "User",
        url_args={"publicId": context.user.public_id},
        query={"fields": "name,emailAddress"},
    )

    if response["status"] == "error":
        return ErrorResponse(f'Error from API: {response["data"][0]["message"]}')

    return response["data"]["name"], response["data"]["emailAddress"]


def send_message(
    context: FunctionContext,
    config: MailConfig,
    subject: str,
    message: str,
    name: str,
    email_address: str,
) -> SuccessResponse | ErrorResponse:
    """
    Send the message that's received via an SSL enabled smtp server.
    """

    combined_message = (
        f"{message}\n\n\n"
        f"Message sent by: {name} ({email_address})\n"
    )

    if context.agent or context.asset:
        combined_message += (
            f"Device: {context.agent_or_asset.name}\n"
            f"Device public ID: {context.agent_or_asset.public_id}"
        )

    msg = MIMEText(combined_message)

    msg["Subject"] = subject
    msg["From"] = config.smtp_user
    msg["To"] = config.smtp_user

    try:
        with smtplib.SMTP_SSL(config.smtp_server, config.smtp_ssl_port) as server:
            server.login(config.smtp_user, config.smtp_password)
            server.send_message(msg)
    except Exception as e:
        return ErrorResponse(str(e))

    return SuccessResponse()


def validate_config(context: FunctionContext) -> MailConfig | ErrorResponse:
    """
    Load and validate the config of the cloud function.
    """

    if not all(
        [
            context.config.get("smtp_server"),
            context.config.get("smtp_ssl_port"),
            context.config.get("smtp_user"),
            context.config.get("smtp_password"),
        ]
    ):
        return ErrorResponse("Not all configuration options are filled in")

    return MailConfig(
        context.config["smtp_server"],
        int(context.config["smtp_ssl_port"]),
        context.config["smtp_user"],
        context.config["smtp_password"],
    )
