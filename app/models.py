from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as orm
from app import db

class User(db.Model):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    username: orm.Mapped[str] = orm.mapped_column(sa.String(64), index=True,
                                                unique=True)
    email: orm.Mapped[str] = orm.mapped_column(sa.String(256), index=True,
                                             unique=True)
    fname: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(128))
    lname: orm.Mapped[Optional[str]] = orm.mapped_column(sa.String(128))
    password_hash: orm.Mapped[str] = orm.mapped_column(sa.String(256))

    def __repr__(self):
        return '<User {}>'.format(self.username)