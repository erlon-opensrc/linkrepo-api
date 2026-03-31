from fastapi import HTTPException, status
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from ..models.user import UserDB, UserCreate

def create(session: Session, user: UserCreate) -> UserDB:
    new_user = UserDB.model_validate(user)
    # TODO: hash password
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
