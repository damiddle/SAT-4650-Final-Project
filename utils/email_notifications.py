import smtplib
from email.message import EmailMessage


def send_email_notif(from_email, to_email, message, subject):
    """
    Sends email notification for expiring drugs or low stock

    Args:
        from_email (String): Email connected to management system
        to_email (String): User sending email to
        message (String): Description of what is expiring or low stock
        subject (String): Specify expiring or low stock
    """

    msg = EmailMessage()
    msg.set_content(message)

    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Sends email message to console right now, would update to utilize Gmail
    # Console prompt: python -m smtpd -c DebuggingServer -n localhost:1025
    s = smtplib.SMTP("localhost", 1025)
    s.send_message(msg)
    s.quit()
