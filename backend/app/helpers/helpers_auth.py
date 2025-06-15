from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import TokenData
from app.services.firebase_auth import create_user, verify_and_decode_auth_token
from app.settings import SecuritySettings


settings = SecuritySettings()
auth_scheme = HTTPBearer(scheme_name='BearerAuth')


def check_auth_token(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> TokenData:
    """Check and decode the provided authentication token."""
    token_sub = verify_and_decode_auth_token(token=token.credentials)
    return TokenData(sub=token_sub)


def create_user_in_auth_service(email: str, password: str) -> str:
    """Create a user in the authentication service and return its external id."""
    return create_user(email=email, password=password)
