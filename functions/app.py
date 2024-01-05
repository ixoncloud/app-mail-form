from dataclasses import asdict

from ixoncdkingress.function.context import FunctionContext

from functions.types import ErrorResponse
from functions.utils import validate_config, get_user, send_message


@FunctionContext.expose
def send_email(context: FunctionContext, subject: str, message: str) -> dict[str, str]:
    """
    Send an email to the configured user.
    """
    config = validate_config(context)
    if isinstance(config, ErrorResponse):
        return asdict(config)

    user = get_user(context)
    if isinstance(user, ErrorResponse):
        return asdict(user)

    name, email_address = user

    return asdict(send_message(context, config, subject, message, name, email_address))
