from urllib.parse import urlsplit
from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from app import app, db
from app.forms import LoginForm
from app.models import User

@app.route('/')
@app.route('/index')
@login_required
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
