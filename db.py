import os

from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]
DEBUG = os.environ["DEBUG"]

engine = create_engine(DATABASE_URL, echo=DEBUG)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
