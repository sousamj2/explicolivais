from flask_mail import Message
from .extensions import mail


def send_email(email_to: str, html_message: str) -> None:
    """Send an HTML email using the shared Mail extension.

    This is a simple helper (no blueprint). Call it from your application code
    or background jobs: `from Funhelpers import send_email`.
    """
    msg = Message(subject='Notification', recipients=[email_to])
    msg.html = html_message
    mail.send(msg)
