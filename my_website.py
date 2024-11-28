# from app import app
import sqlalchemy as sa
import sqlalchemy.orm as orm
from app import app, db
from app.models import User, Post

# adds the database instance and models to a shell session started
# with `flask shell`
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': orm, 'db': db, 'User': User, 'Post': Post}