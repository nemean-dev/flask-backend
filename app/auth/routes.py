from urllib.parse import urlsplit
from flask import render_template, redirect, flash, url_for, request
from flask_login import current_user, login_user, logout_user
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.models import User
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, \
                      ResetPasswordForm
from app.auth.email import send_password_reset_email

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(
            User.username == form.username.data))
        
        if user is None or not user.check_password(form.password.data):
            flash(_("Invalid login credentials"))
            return redirect(url_for('auth.login'))
        
        else:
            login_user(user, remember=form.remember_me.data)
            flash(_("You are now logged in"))

            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('main.index')

            return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(
            email = form.email.data,
            username = form.username.data
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()
        
        flash(_('Congratulations, you are now a registered user! Please sign in'))
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title= 'Sign Up', form= form)

@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        email = form.email.data
        user = db.session.scalar(sa.select(User).where(User.email == email))
        if user:
            send_password_reset_email(user)
            flash(_("Check your email for instructions on how to reset your password."))
            return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password_request.html', form=form, title='Reset Password')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)