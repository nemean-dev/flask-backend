from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_babel import lazy_gettext as _l
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    fname = StringField(_l('First Name'), validators=[Length(max=128)])
    lname = StringField(_l('Last Name'), validators=[Length(max=128)])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = StringField(_l('Password'), validators=[DataRequired()])
    password2 = StringField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    # methods that match the pattern 'validate_<field_name>' are invoked automatically by wtforms
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))

class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(max=64)])
    fname = StringField(_l('First Name'), validators=[Length(max=128)])
    lname = StringField(_l('Last Name'), validators=[Length(max=128)])
    about_me = TextAreaField(_l('About Me: '), validators=[Length(max=140)])
    submit = SubmitField(_l('Update Details'))

    def validate_username(self, username):
        if username.data != current_user.username:
            #TODO: increase modularity: make forms module independent 
            # of the login implementation so that forms is not dependent on other components.
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user is not None:
                raise ValidationError(_l('Please use a different username.'))
            
class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
    post = TextAreaField(_l('Post something!'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Your email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Reset Password'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))