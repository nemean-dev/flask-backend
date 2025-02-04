from datetime import datetime, timezone
from time import time
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from flask_login import UserMixin # properties/methods flask_login expects in the user model
import jwt
from app import db, login
from app.search import add_to_index, remove_from_index, query_index

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        """
        returns matches, total
        returns ordered results (e.g. posts) ordered by match score and the 
        total number of results.
        """
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

# association table. Since it is just an auxiliary table, it is not declared as a model.
follower_followed = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
    # the way to create a compound primary key is to declare both cols as primary keys
)

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
    
    following: orm.WriteOnlyMapped['User'] = orm.relationship(
        secondary=follower_followed,
        primaryjoin=(follower_followed.c.follower_id == id),
        secondaryjoin=(follower_followed.c.followed_id == id),
        back_populates='followers'
    )
    followers: orm.WriteOnlyMapped['User'] = orm.relationship(
        secondary=follower_followed,
        primaryjoin=(follower_followed.c.followed_id == id),
        secondaryjoin=(follower_followed.c.follower_id == id),
        back_populates='following'
    )

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

    def follow(self, user):
        '''self will follow the given user'''
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        '''self will unfollow the given user'''
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        '''is self following the given user?'''
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        '''how many users follow self?'''
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        '''how many users does self follow?'''
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    
    def following_posts(self):
        '''
        Returns query representing posts by the users that self is following 
        or that self authored, in descending order by most recent.
        '''
        Author = orm.aliased(User)
        Follower = orm.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token) -> 'User | None':
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)
   
class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    body: orm.Mapped[str] = orm.mapped_column(sa.String(600))
    timestamp: orm.Mapped[datetime] = orm.mapped_column(
        index= True, 
        default= lambda: datetime.now(timezone.utc))
    language: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(5))
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