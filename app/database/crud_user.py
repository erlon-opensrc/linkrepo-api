from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from ..models.user import UserDB, UserCreate
from ..utils.hasher import password_hasher


def create(session: Session, user: UserCreate) -> UserDB:
    new_user = UserDB.model_validate(user)
    new_user.password = password_hasher.hash(new_user.password)
    try:
        session.add(new_user)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The username is already in use'
        )
    session.refresh(new_user)
    return new_user


def get_by_username(session: Session, username: str) -> UserDB | None:
    user = session.exec(
        select(UserDB).where(UserDB.username == username)
    ).first()

    return user


def get_by_id(session: Session, id: str) -> UserDB | None:
    user = session.exec(select(UserDB).where(UserDB.id == id)).first()
    return user
