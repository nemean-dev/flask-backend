from app import app, db
import sqlalchemy as sa
from app.models import User, Post
from resources.data.users import users
from resources.data.posts import posts

def get_password_by_alignment(alignment):
    if alignment == 'good':
        return '123'
    elif alignment == 'bad':
        return '321'
    else:
        return '222'
    
def create_users(users: list[dict]):
    for user in users:
        u = User(
            username=user['username'],
            email=user['email'],
            fname=user['fname'],
            lname=user['lname'],
        )
        pwd = get_password_by_alignment(user['alignment'])
        u.set_password(pwd)
        db.session.add(u)

    try:
        db.session.commit()
        print('Users added successfully.')
    except Exception as e:
        db.session.rollback()
        print(f'Error adding users: {e}')
        raise

def follow_and_posts(users, posts):
    for user in users:
        u = db.session.scalar(sa.select(User).where(User.username == user['username']))

        if u is None:
            print(f'user with username {user['username']} not found')
        
        # follow other users
        if 'following' in user:
            for followed_username in user['following']:
                followed_user = db.session.scalar(sa.select(User).where(User.username == followed_username))
                try:
                    u.follow(followed_user)
                except Exception as e:
                    print(f'Error: {u.username} was unable to follow {followed_username}')
                    raise
        
        # create posts
        for post_info in posts:
            if post_info['author'] == u.username:
                post = Post(body=post_info['body'], author=u)
                db.session.add(post)

    try:
        db.session.commit()
        print('Followings and posts added successfully.')
    except Exception as e:
        db.session.rollback()
        print(f'Error adding followings or posts: {e}')
        raise

if __name__=='__main__':
    with app.app_context():
        create_users(users)
        follow_and_posts(users, posts)