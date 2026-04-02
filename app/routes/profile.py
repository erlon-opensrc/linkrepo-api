from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session

from ..database import crud_user
from ..database.config import get_session
from ..auth.auth_user import get_current_user
from ..models.user import UserGet, UserRead, UserDelete, UserUpdate


router = APIRouter(
    prefix='/users',
    tags=['Profile'],
)

DELETE_CONFIRMATION_TEXT = 'delete my account'


@router.get('/me', response_model=UserRead)
async def read_profile(current_user: UserGet = Depends(get_current_user)):
    """
    Retrieve data from the authenticated user.

    Uses the JWT token to identify and return the logged-in user's profile.
    """
    return current_user


@router.patch('/me/update', response_model=UserRead)
async def update_user(
    *,
    session: Session = Depends(get_session),
    current_user: UserGet = Depends(get_current_user),
    user_in: UserUpdate
):
    """
    TODO: add docstring
    """
    updated_user = crud_user.update(
        session=session,
        id=current_user.id,
        user_in=user_in
    )
    return updated_user


@router.delete('/me/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    *,
    session: Session = Depends(get_session),
    current_user: UserGet = Depends(get_current_user),
    user_in: UserDelete
):
    """
    TODO: add docstring
    """
    if user_in.confirm_text.lower() != DELETE_CONFIRMATION_TEXT:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                'invalid_field': 'confirm_text',
                'expected': DELETE_CONFIRMATION_TEXT,
                'message': 'The confirmation text entered is incorrect'
            }
        )

    crud_user.delete(session, current_user.id)
