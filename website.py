# from app import app
import sqlalchemy as sa
import sqlalchemy.orm as orm
from app import create_app, db
from app.models import User, Post

app = create_app()

# for shells initiated with `flask shell`
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': orm, 'db': db, 'User': User, 'Post': Post}
