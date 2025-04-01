from datetime import datetime, timedelta, timezone

import jwt
from freezegun import freeze_time

from app.security import create_access_token, settings


@freeze_time(datetime(2020, 5, 8, 13, 0, 0, tzinfo=timezone.utc))
def test_create_access_token():
    test_username = 'test_username'

    expiration_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(tz=timezone.utc) + expiration_delta
    to_encode = {
        'sub': test_username,
        'exp': expire,
    }
    expected_token = jwt.encode(
        payload=to_encode,
        key=settings.SECRET_KEY,
        algorithm=settings.TOKEN_ENCRYPTION_ALGORITHM,
    )
    actual_token = create_access_token(username=test_username)

    assert expected_token == actual_token
