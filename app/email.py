from flask_mail import Message
from app import mail

def send_mail(subject, sender, recipents, text_body, html_body = None):
    msg = Message(subject=subject, sender=sender, recipients=recipents)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)