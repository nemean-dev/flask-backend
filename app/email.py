from threading import Thread
from flask_mail import Message
from app import app, mail

def send_async_email(app, msg: Message):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body = None):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()
