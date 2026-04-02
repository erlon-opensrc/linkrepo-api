from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from uuid import UUID

from ..models.user import UserDB, UserCreate, UserUpdate
from ..utils.hasher import password_hasher


def create(session: Session, user: UserCreate) -> UserDB:
    new_user = UserDB.model_validate(user)
    new_user.password = password_hasher.hash(new_user.password)
    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The username is already in use'
        )


def get_by_username(session: Session, username: str) -> UserDB | None:
    user = session.exec(
        select(UserDB).where(UserDB.username == username)
    ).first()

    return user


def get_by_id(session: Session, id: UUID) -> UserDB | None:
    user = session.exec(select(UserDB).where(UserDB.id == id)).first()
    return user


def update(session: Session, id: UUID, user_in: UserUpdate) -> UserDB:
    user = get_by_id(session, id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    user.sqlmodel_update(user_in.model_dump(exclude_unset=True))
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                'The data provided conflicts with a existing record '
                '(e.g., username already registered).'
            ),
        )


def delete(session: Session, id: UUID) -> None:
    user = get_by_id(session, id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    session.delete(user)
    session.commit()
