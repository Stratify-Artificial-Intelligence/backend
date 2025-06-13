import logging

from fastapi import HTTPException, status
from firebase_admin import auth as firebase_auth, credentials, get_app, initialize_app

from app.settings import FirebaseAuthSettings

logger = logging.getLogger(__name__)
settings = FirebaseAuthSettings()

try:
    get_app()
except ValueError:
    # Firebase Admin returns ValueError if the app has not been initialized.
    cred = credentials.Certificate(settings.PRIVATE_KEY)
    initialize_app(credential=cred)


def verify_and_decode_auth_token(token: str) -> str:
    """Return the decoded Firebase sub from the provided token."""
    try:
        decoded_firebase_token = firebase_auth.verify_id_token(id_token=token)
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Firebase token has expired',
        )
    except firebase_auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate Firebase token',
        )
    except Exception as e:
        logger.warning('FIREBASE AUTH ERROR: ' + str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Firebase token',
        ) from e

    return decoded_firebase_token['sub']


def create_user(email: str, password: str) -> str:
    """Create a user in Firebase Auth and return its external id."""
    try:
        user = firebase_auth.create_user(email=email, password=password)
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Email already exists',
        )
    except Exception as e:
        logger.error('FIREBASE AUTH ERROR: ' + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to create user in Firebase Auth',
        ) from e
    return user.uid
