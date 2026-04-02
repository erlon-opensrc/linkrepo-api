from uuid import UUID, uuid7
from datetime import datetime
from sqlmodel import SQLModel, Field

from ..utils.timestamps import utcnow


class User(SQLModel):
    username: str = Field(index=True, unique=True, min_length=3, max_length=20)


class UserDB(User, table=True):
    __tablename__ = 'users' # type: ignore

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    password: str = Field(unique=True, nullable=False)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow, sa_column_kwargs={
        'onupdate': utcnow,
    })


class UserCreate(User):
    password: str = Field(min_length=8, max_length=255)
    password_confirmation: str = Field(min_length=8, max_length=255)


class UserRead(SQLModel):
    id: UUID
    username: str


class UserGet(SQLModel):
    id: UUID


class UserUpdate(SQLModel):
    pass
