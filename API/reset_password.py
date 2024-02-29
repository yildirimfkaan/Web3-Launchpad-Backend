import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

# from dotenv import load_dotenv
from pydantic import AnyHttpUrl, EmailStr
import emails
from emails.template import JinjaTemplate
from jose import jwt
import secrets
import os
from sqlalchemy import true

# load_dotenv()

SMTP_TLS: bool = os.getenv("smtp_tls")
SMTP_PORT: Optional[int] = os.getenv("smtp_port")
SMTP_HOST: Optional[str] = os.getenv("smtp_host")
SMTP_USER: Optional[str] = os.getenv("smtp_user")
SMTP_PASSWORD: Optional[str] = os.getenv("smtp_password")
EMAILS_FROM_EMAIL: Optional[EmailStr] = os.getenv("emails_from_email")
EMAILS_FROM_NAME: Optional[str] = os.getenv("emails_from_name")
EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = int(os.getenv("email_reset_token_expire_hours"))
EMAIL_TEMPLATES_DIR: str = os.getcwd() + os.getenv("email_templates_dir")
SERVER_NAME: str = os.getenv("server_name")
SERVER_HOST: AnyHttpUrl = os.getenv("server_host")
PROJECT_NAME: str = os.getenv("project_name")
SECRET_KEY: str = secrets.token_urlsafe(32)


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(EMAILS_FROM_NAME, EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": SMTP_HOST, "port": SMTP_PORT}
    if SMTP_TLS:
        smtp_options["tls"] = True
    if SMTP_USER:
        smtp_options["user"] = SMTP_USER
    if SMTP_PASSWORD:
        smtp_options["password"] = SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    link = f"{SERVER_HOST}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None
