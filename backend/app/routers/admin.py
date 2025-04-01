"""API endpoints for admin management."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import schemas
from app.deps import get_repository
from app.repositories import UserRepository
from app.schemas import Token
from app.security import create_access_token

router = APIRouter(
    tags=['Admin'],
)


@router.post(
    '/token',
    summary='Obtain token',
    status_code=status.HTTP_200_OK,
    response_model=Token,
    responses={
        status.HTTP_401_UNAUTHORIZED: {'model': schemas.HTTP401Unauthorized},
    },
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users_repo: UserRepository = Depends(get_repository(UserRepository)),
):
    """Log in."""
    user = await users_repo.authenticate_user(
        username=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token = create_access_token(username=user.username)
    return Token(access_token=access_token, token_type='bearer')
