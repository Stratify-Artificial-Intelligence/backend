from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = 'Admin'
    BASIC = 'Basic'
