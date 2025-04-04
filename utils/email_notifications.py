import smtplib
from email.message import EmailMessage
import validators

SMTP_SERVER = "localhost"
SMTP_PORT = 1025
USE_TLS = False


# Sends email message to console right now, would update to utilize Gmail
# Console prompt: python -m smtpd -c DebuggingServer -n localhost:1025
def send_email_notif(from_email, to_email, message, subject):
    """Sends an email

    Args:
        from_email (String): Sender email
        to_email (String): Receiving email
        message (String): Message
        subject (String): Subject line

    Raises:
        TypeError: Invalid email address
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
                server.starttls()  # Secure the connection if TLS is enabled
            server.send_message(msg)
            print(
                f"Email sent from {from_email} to {to_email} with subject '{subject}'"
            )

    except smtplib.SMTPException as smtp_err:
        print(f"SMTP error occurred while sending email: {smtp_err}")
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
