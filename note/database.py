from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///./notes.db')
db_session = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
)
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import note.models
    Base.metadata.create_all(bind=engine)

def delete_tables():
    import note.models
    Base.metadata.drop_all(bind=engine)