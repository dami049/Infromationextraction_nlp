import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

basedir = os.path.abspath(os.path.dirname(__file__))

engine = create_engine('sqlite:///' + os.path.join(basedir, 'aggregator.db'), echo=True, connect_args={"check_same_thread": False})
_SessionFactory = sessionmaker(bind=engine, autoflush=True)

# connect_args={'check_same_thread': False}
# engine=create_engine('sqlite:///data.db', echo=True, connect_args={"check_same_thread": False})

Base = declarative_base()

def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()

def drop_table_session_factory():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return _SessionFactory()