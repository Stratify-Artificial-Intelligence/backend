from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas import TokenData
from app.services import ServicesFactory
from app.settings import GeneralSettings


settings = GeneralSettings()
auth_scheme = HTTPBearer(scheme_name='BearerAuth')
identity_service = ServicesFactory().get_identity_provider()


def check_auth_token(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> TokenData:
    """Check and decode the provided authentication token."""
    # ToDo (pduran): [S-249] Implement this using api gateway instead.
    if token.credentials == settings.SERVICE_USER_TOKEN:
        return TokenData(sub='service_user')
    return identity_service.verify_and_decode_auth_token(token=token.credentials)


def create_user_in_auth_service(email: str, password: str) -> str:
    """Create a user in the authentication service and return its external id."""
    return identity_service.create_user(email=email, password=password)
