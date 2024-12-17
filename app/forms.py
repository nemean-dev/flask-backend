from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
from flask_babel import lazy_gettext as _l
import sqlalchemy as sa
from app import db
from app.models import User

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
