import os
import jwt
import uuid
from dotenv import load_dotenv
from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from typing import Literal, Any
from argon2.exceptions import VerifyMismatchError

from ..database import crud_user
from ..database.config import get_session
from ..models.user import UserRead
from ..utils.hasher import password_hasher
from ..utils.timestamps import utcnow


load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

if SECRET_KEY is None:
    raise ValueError('Unknown secret key')

ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 30)
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/signin')

user_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate user credentials',
)


def authenticate_user(
    session: Session, username: str, password: str
) -> UserRead | Literal[False]:
    user = crud_user.get_by_username(session, username)

    if user is None:
        return False

    try:
        password_hasher.verify(user.password, password)
    except VerifyMismatchError:
        return False

    return UserRead.model_validate(user)


def create_access_token(payload: dict[str, Any]) -> str:
    exp = utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    _payload = payload.copy()
    _payload.update({'exp': exp})

    return jwt.encode(_payload, SECRET_KEY, algorithm=ALGORITHM) # type: ignore


def get_current_user(
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
) -> UserRead:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # type: ignore
        user_id: str | None = payload.get('sub')
        if user_id is None:
            raise user_credentials_exception
    except jwt.DecodeError:
        raise user_credentials_exception

    current_user = crud_user.get_by_id(session, uuid.UUID(user_id))
    if current_user is None:
        raise user_credentials_exception

    return UserRead.model_validate(current_user)
