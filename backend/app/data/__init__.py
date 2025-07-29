import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.data.models import Base

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_url = os.environ.get("DB_URL") or \
         "sqlite:///" + os.path.join(basedir, "app.db")
engine = create_engine(db_url, echo=False)
Base.metadata.create_all(engine)