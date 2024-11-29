from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin # properties/methods flask_login expects in the user model
from app import db, login

class User(UserMixin, db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: orm.Mapped[str] = orm.mapped_column(sa.String(256), index=True,
                                             unique=True)
    fname: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(128))
    lname: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(128))
    password_hash: orm.Mapped[str] = orm.mapped_column(sa.String(256))
    about_me: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(140))
    last_seen: orm.Mapped[Optional[datetime]] = orm.mapped_column(
        default=lambda: datetime.now(timezone.utc))

    posts: orm.WriteOnlyMapped['Post'] = orm.relationship(
        back_populates='author')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        '''
        Returns svg with dimensions size height x size width.
        TODO: future implementation should return URL of their avatar/profile pic.
        Not using gravatar due to privacy concerns.
        '''
        if not isinstance(size, (int, float)) or size < 0:
            raise ValueError("Size must be a positive number.")

        return f'<svg fill="#081759" height="{size}px" width="{size}px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512" xml:space="preserve" stroke="#081759"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <g> <g> <circle cx="256" cy="114.526" r="114.526"></circle> </g> </g> <g> <g> <path d="M256,256c-111.619,0-202.105,90.487-202.105,202.105c0,29.765,24.13,53.895,53.895,53.895h296.421 c29.765,0,53.895-24.13,53.895-53.895C458.105,346.487,367.619,256,256,256z"></path> </g> </g> </g></svg>'

   
class Post(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sa.String(600))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(index= True, 
                                                        default= lambda: datetime.now(timezone.utc))
    user_id: orm.Mapped[int] = orm.mapped_column(sa.ForeignKey(User.id),
                                                 index=True)
    
    author: orm.Mapped[User] = orm.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    
# flask-login expects that the application will configure a user loader 
# function, that can be called to load a user given the ID
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))