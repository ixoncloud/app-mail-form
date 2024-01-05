from dataclasses import dataclass, field


@dataclass
class ErrorResponse:
    message: str
    status: str = field(default="error")


@dataclass
class SuccessResponse:
    status: str = field(default="success")


@dataclass
class MailConfig:
    smtp_server: str
    smtp_ssl_port: int
    smtp_user: str
    smtp_password: str
