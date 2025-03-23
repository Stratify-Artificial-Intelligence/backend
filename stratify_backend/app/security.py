from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from passlib.context import CryptContext
from pydantic import ValidationError

from app.enums import AuthMethodEnum
from app.schemas import TokenData
from app.settings import SecuritySettings

settings = SecuritySettings()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

auth_scheme: HTTPBearer | OAuth2PasswordBearer
if settings.AUTH_METHOD == AuthMethodEnum.BEARER:
    auth_scheme = HTTPBearer(scheme_name='BearerAuth')
elif settings.AUTH_METHOD == AuthMethodEnum.OAUTH2:
    auth_scheme = OAuth2PasswordBearer(
        scheme_name='OAuth2',
        tokenUrl='token',
    )
else:
    raise ValueError(f'Unexpected Authorization method: {settings.AUTH_METHOD}')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(username: str, expiration_delta: timedelta | None = None):
    if not expiration_delta:
        expiration_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(tz=timezone.utc) + expiration_delta
    to_encode = {
        'sub': username,
        'exp': expire,
    }
    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.TOKEN_ENCRYPTION_ALGORITHM,
    )
    return encoded_jwt


def check_auth_token(
    token: str | HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> TokenData:
    if settings.AUTH_METHOD == AuthMethodEnum.BEARER:
        assert isinstance(token, HTTPAuthorizationCredentials)
        return _decode_token(token.credentials)
    elif settings.AUTH_METHOD == AuthMethodEnum.OAUTH2:
        assert isinstance(token, str)
        return _decode_token(token)
    else:
        raise ValueError(f'Unexpected Authorization method: {settings.AUTH_METHOD}')


def _decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.TOKEN_ENCRYPTION_ALGORITHM],
        )
        username: str | None = payload.get('sub')
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token does not contain sub',
            )
        return TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
        )
    except (jwt.InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
        )
