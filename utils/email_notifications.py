import smtplib
from email.message import EmailMessage
import validators


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
            raise TypeError("Emails are not valid")
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        s = smtplib.SMTP("localhost", 1025)
        s.send_message(msg)
        s.quit()
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
