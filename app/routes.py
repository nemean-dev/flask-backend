from urllib.parse import urlsplit
from datetime import datetime, timezone
from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm
from app.models import User, Post

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        # db.session.add() not needed because any current_user reference invokes user loader callback function, 
        # which will run a database query that will put the target user in the db session.

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()

    if form.validate_on_submit():
        post = Post(author=current_user, body=form.post.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post was submitted successfully!')

        # redirect instead of just continuing to render_template below: 
        # see wikipedia article on 'Post/Redirect/Get' pattern
        return redirect(url_for('index')) 

    posts = db.session.scalars(current_user.following_posts()).all()

    return render_template('index.html', title= 'Home', posts= posts, form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()

    if form.validate_on_submit(): # on valid form submission (so only some POSTs)
        user = db.session.scalar(sa.select(User).where(
            User.username == form.username.data))
        
        if user is None or not user.check_password(form.password.data):
            flash("Invalid login credentials")
            return redirect(url_for('login'))
        
        else:
            login_user(user, remember=form.remember_me.data)
            flash("Successfully logged in") #TODO: delete?

            # Redirect user to page they tried to access
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('index')

            return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(
            email = form.email.data,
            username = form.username.data
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user! Please sign in')
        return redirect(url_for('login'))
    
    return render_template('register.html', title= 'Sign Up', form= form)

# dynamic routing in flask passes <string_var> as view function argument
@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    form = EmptyForm()
    posts = [
        {'author': user, 'body': 'test post #1: some random post'},
        {'author': user, 'body': 'test post #2'}
    ]

    return render_template('user.html', user=user, posts=posts, form=form)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.fname = form.fname.data
        current_user.lname = form.lname.data

        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.fname.data = current_user.fname
        form.lname.data = current_user.lname
    
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))

        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        
        if current_user == user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {username}')
        return redirect(url_for('user', username= username))
    
    else:
        return redirect(url_for('index'))
    
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))
        
        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('index'))
        
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('user', username=username))
    
    else:
        return redirect(url_for('index'))
