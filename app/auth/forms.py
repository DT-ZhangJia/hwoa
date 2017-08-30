"""
learn flask auth
"""
# pylint: disable=invalid-name

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..models import User

class LoginForm(FlaskForm):
    """login form class"""
    email_input = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    passwd_input = PasswordField('Password', validators=[Required()])
    remember_me_box = BooleanField('Keep me logged in')
    submit_btn = SubmitField('Log In')

class RegisterForm(FlaskForm):
    """register form class"""
    email_reg_input = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username_reg_input = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores')]) # pylint: disable=C0301
    passwd_reg_input = PasswordField('Password', validators=[Required(), EqualTo('passwd2_reg_input', message='Passwords must match.')]) # pylint: disable=C0301
    passwd2_reg_input = PasswordField('Confirm password', validators=[Required()])
    submit_reg_btn = SubmitField('Register')

    def validate_email_reg_input(self, field):#pylint: disable=R0201
        """check existed email"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username_reg_input(self, field):#pylint: disable=R0201
        """check existed username"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangepwForm(FlaskForm):
    """change password form"""
    old_passwd_input = PasswordField('Old Password', validators=[Required()])
    passwd_chg_input = PasswordField('New Password', validators=[Required(), EqualTo('passwd2_chg_input', message='Passwords must match.')]) # pylint: disable=C0301
    passwd2_chg_input = PasswordField('Confirm password', validators=[Required()])
    submit_chg_btn = SubmitField('Change Password')

class ResetrequestForm(FlaskForm):
    """Reset Password Request"""
    email_request_input = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')

class PasswordResetForm(FlaskForm):
    """Reset Password Form"""
    email_resetpw_input = StringField('Email', validators=[Required(), Length(1, 64), Email()],
                                      render_kw={'readonly': True})
    passwd_reset_input = PasswordField('New Password', validators=[Required(), EqualTo('passwd2_reset_input', message='Passwords must match')]) # pylint: disable=C0301
    passwd2_reset_input = PasswordField('Confirm password', validators=[Required()])
    submit_reset_btn = SubmitField('Reset Password')

    #def validate_email(self, field):#如果令牌无法传递email的话，岂不是能够随意更改别人的密码了？
    #    if User.query.filter_by(email=field.data).first() is None:
    #        raise ValidationError('Unknown email address.')
