import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Jobs(SqlAlchemyBase):
    __tablename__ = 'Jobs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relation('User')
    job = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    work_size = sqlalchemy.Column(sqlalchemy.INTEGER, nullable=True)

    collaborators = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    start_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    end_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
