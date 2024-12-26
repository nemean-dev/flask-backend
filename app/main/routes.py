from datetime import datetime, timezone
from langdetect import detect, LangDetectException
from flask import render_template, redirect, flash, url_for, request, g, \
    current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
import sqlalchemy as sa
from app import db
from app.main import bp
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
from app.models import User, Post
from app.translate import translate

@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
        # db.session.add() not needed because any current_user reference 
        # invokes user loader callback function, which will run a database 
        # query that will put the target user in the db session.

        g.search_form = SearchForm()

    g.locale = str(get_locale())

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()

    if form.validate_on_submit():
        try:
            language = detect(form.post.data)
            
        except LangDetectException:
            language = ''

        post = Post(author=current_user, body=form.post.data, language=language)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post was submitted successfully!'))

        # redirect instead of just continuing to render_template below: 
        # see wikipedia article on 'Post/Redirect/Get' pattern
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, int)
    posts = db.paginate(current_user.following_posts(), 
                        page=page, per_page=current_app.config['POSTS_PER_PAGE'], 
                        error_out=False)
    pagination = {
        'page': page,
        'next_url': url_for('main.index', page=posts.next_num) \
            if posts.has_next else None,
        'prev_url': url_for('main.index', page=posts.prev_num) \
            if posts.has_prev else None,
    }

    return render_template('index.html', title='Home', posts=posts.items, 
                           form=form, pagination=pagination)

@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, int)
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page, 
                        per_page=current_app.config['POSTS_PER_PAGE'], 
                        error_out=False)
    pagination = {
        'page': page,
        'next_url': url_for('main.explore', page=posts.next_num) \
            if posts.has_next else None,
        'prev_url': url_for('main.explore', page=posts.prev_num) \
            if posts.has_prev else None,
    }
    
    return render_template('index.html', title='Explore', posts=posts.items, 
                           pagination=pagination)

# dynamic routing in flask passes <string_var> as view function argument
@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    page = request.args.get('page', 1, int)
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(query, page=page, 
                        per_page=current_app.config['POSTS_PER_PAGE'], 
                        error_out=False)
    pagination = {
        'page': page,
        'next_url': url_for('main.user', username=username, 
                            page=posts.next_num) if posts.has_next else None,
        'prev_url': url_for('main.user', username=username, 
                            page=posts.prev_num) if posts.has_prev else None,
    }
    form = EmptyForm()

    return render_template('user.html', user=user, posts=posts, form=form, 
                           pagination=pagination)

@bp.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.fname = form.fname.data
        current_user.lname = form.lname.data

        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
        form.fname.data = current_user.fname
        form.lname.data = current_user.lname
    
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))

        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        
        if current_user == user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s', username=username))
        return redirect(url_for('main.user', username= username))
    
    else:
        return redirect(url_for('main.index'))
    
@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == username))
        
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    
    else:
        return redirect(url_for('main.index'))

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    data = request.get_json()
    return {'text': translate(data['text'], data['dest_language'])}

@bp.route('/search')
@login_required
def search():
    if not g.search_form.validate():
        return redirect(url_for('main.explore'))
    
    page = request.args.get('page', 1, type=int)
    posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    
    next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    
    pagination = {
        'page': page,
        'next_url': next_url,
        'prev_url': prev_url,
    }

    return render_template('search.html', title=_('Search'), posts=posts, 
                           pagination=pagination)