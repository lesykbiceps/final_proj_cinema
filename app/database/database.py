from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.main import Config

db_string = Config.SQLALCHEMY_DATABASE_URI
db = create_engine(db_string, connect_args={'check_same_thread': False})
base = declarative_base()
Session = sessionmaker(db)
session = Session()
