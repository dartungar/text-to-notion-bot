from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker


def init_db():
    global Base
    global engine
    global session
    Base = declarative_base()
    engine = create_engine('postgres://txlpcfjyjefqxa:5d47c7968d697c57a96fc1d6e548b00d1f1c81057f88cc6ab04acbe05def76f7@ec2-54-195-252-243.eu-west-1.compute.amazonaws.com:5432/dd7qeeent7ma5a')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()


def create_users_table(engine, table_name='users'):
    Base = declarative_base()
    if not engine.dialect.has_table(engine, table_name):
        class User(Base):
            __tablename__ = table_name
            id = Column(Integer, primary_key=True)
            username = Column(String(64))
            notion_api_key = Column(String(250))
            page_address = Column(String(250))
            page_title = Column(String(250))


def create_new_user(session, username):
    if not session.query(User).filter(User.username == username).one():
        user = User(username=username)
        session.add(user)
        session.commit()