from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.models_base import Base


DATABASE_URI = 'postgresql://postgres:9652@localhost:5432/postgres'
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)

def init_db(app):
    # Create all tables if not exist
    Base.metadata.create_all(engine)

def get_session():
    return Session()
