from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = 'Admin'
    BASIC = 'Basic'
    SERVICE = 'Service'


class UserLanguageEnum(str, Enum):
    ES = 'es'


class UserPlanEnum(str, Enum):
    STARTER = 'Starter'
    FOUNDER = 'Founder'
    CEO = 'CEO'
