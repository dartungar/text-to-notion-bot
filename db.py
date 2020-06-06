import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = create_engine(os.environ['DATABASE_URL_NOTION'])
DBSession = sessionmaker(bind=engine)
session = DBSession()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64))
    notion_api_key = Column(String(250))
    page_address = Column(String(250))
    page_title = Column(String(250))


if not engine.dialect.has_table(engine, 'users'):
    Base.metadata.create_all(engine)


def create_new_user(session, username):
    if not session.query(User).filter(User.username == username).first():
        user = User(username=username)
        session.add(user)
        session.commit()


def check_if_user_exists(session, username):
    if not session.query(User).filter(User.username == username).first():
        return False
    return True
    