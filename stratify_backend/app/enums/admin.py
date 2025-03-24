from enum import Enum


class AuthMethodEnum(str, Enum):
    BEARER = 'bearer'
    OAUTH2 = 'oauth2'
