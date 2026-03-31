import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine, SQLModel
from typing import Generator

from ..models.user import *

load_dotenv()

DATABASE_URI = os.getenv('DATABASE_URI')
ECHO_DB = os.getenv('ECHO_DB', True)

if DATABASE_URI is None:
    raise ValueError('Unknown database.')

engine = create_engine(
    DATABASE_URI,
    echo=ECHO_DB,
    connect_args={'check_same_thread': False},
)


def create_table_and_database() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
