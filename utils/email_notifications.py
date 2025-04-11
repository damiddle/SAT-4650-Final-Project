"""
Module for sending email notifications.

Provides a function to send email messages. Currently, this uses a local SMTP
server (e.g., a debugging SMTP server) based on configuration from the .env file.
"""

import smtplib
from email.message import EmailMessage
import validators
import os
from dotenv import load_dotenv

ENV_FILE_PATH = ".env"
load_dotenv(ENV_FILE_PATH)

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
USE_TLS = os.getenv("USE_TLS")


def send_email_notif(from_email, to_email, message, subject):
    """Sends an email notification.

    Validates sender and recipient emails before creating an email message and
    sending it via the configured SMTP server.

    Args:
        from_email (str): The sender's email address.
        to_email (str): The recipient's email address.
        message (str): The email body.
        subject (str): The email subject.

    Raises:
        TypeError: If the provided email addresses are invalid.
        SMTPException: If an SMTP error occurs.
        Exception: For any other errors during sending.
    """

    try:
        if (not validators.is_valid_email(from_email)) or (
            not validators.is_valid_email(to_email)
        ):
            raise TypeError("One or both email addresses are not valid")

        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            if USE_TLS:
                server.starttls()

            server.send_message(msg)

            print(
                f"Email sent from {from_email} to {to_email} with subject '{subject}'"
            )

    except smtplib.SMTPException as smtp_err:
        print(f"SMTP error occurred while sending email: {smtp_err}")

    except Exception as e:
        print(f"An error occurred while sending email: {e}")
