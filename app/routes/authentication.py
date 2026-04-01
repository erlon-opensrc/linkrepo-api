from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from ..auth.auth_user import authenticate_user, create_access_token

from ..database import crud_user
from ..database.config import get_session
from ..models.user import UserCreate, UserRead


router = APIRouter(prefix='/auth', tags=['Authentication'])


@router.post(
    '/signup', response_model=UserRead, status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user: UserCreate, session: Session = Depends(get_session),
) -> UserRead:
    """
    Register new user.

    - **username**: (str) Required. Username >= 3 and <= 20 characters.
    - **password**: (str) Required. Password >= 8 <= 255 characters.
    - **password_confirmation**: (str) Required. It must be identical to the
    value of the password property.
    """
    if user.password != user.password_confirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Password confirmation does not match'
        )
    new_user = crud_user.create(session, user)
    return UserRead(**new_user.model_dump())


@router.post('/signin')
async def user_login(
    session: Session = Depends(get_session),
    auth_data: OAuth2PasswordRequestForm = Depends()
) -> dict[str, str]:
    """
    Authenticate user and return access token (JWT).

    - **username**: (str) Required. Username of an already registered user.
    - **password**: (str) Required. User's password.
    """
    user = authenticate_user(session, auth_data.username, auth_data.password)
    if user:
        access_token = create_access_token(payload={'sub': str(user.id)})
        return {'access_token': access_token, 'token_type': 'bearer'}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect username or password',
        headers={'WWW-Authenticate': 'Bearer'},
    )
