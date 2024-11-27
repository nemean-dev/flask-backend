from flask import render_template, redirect, flash, url_for
from flask_login import current_user, login_user
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm
from app.models import User

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Bob'}
    posts = [
        {
            'author': {'username': 'Buzz Aldrin'},
            'body': 'The little blue dot is so pretty.'
        },
        {
            'author': {'username': 'Musky Musk'},
            'body' : 'I hate worker unions!'
        }
    ]
    return render_template('index.html', title = 'Home', user= user, posts= posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()

    if form.validate_on_submit(): # on valid form submission (so only some POSTs)
        user = db.session.scalar(sa.select(User).where(
            User.username == form.username.data))
        
        if user.username is None or not user.check_password(form.password.data):
            flash("Invalid login credentials")
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember_me.data)
            flash("Successfully logged in")
            return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)