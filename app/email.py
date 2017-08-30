"""
learn flask views
"""
# pylint: disable=invalid-name, too-few-public-methods


from flask import current_app, render_template
from flask_mail import Message
from . import mail


def send_email(to, subject, template, **kwargs):
    """send mail method"""
    app = current_app._get_current_object() #这个东西有什么用？# pylint: disable=W0212
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)
