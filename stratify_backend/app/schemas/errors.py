from pydantic import BaseModel


class HTTP400BadRequest(BaseModel):
    detail: str

    class Config:
        schema_extra = {'example': {'detail': 'Bad request'}}


class HTTP401Unauthorized(BaseModel):
    detail: str

    class Config:
        schema_extra = {'example': {'detail': 'Could not validate credentials'}}


class HTTP403Forbidden(BaseModel):
    detail: str

    class Config:
        schema_extra = {'example': {'detail': 'Not authenticated'}}


class HTTP404NotFound(BaseModel):
    detail: str

    class Config:
        schema_extra = {'example': {'detail': 'Item not found'}}


class HTTP405MethodNotAllowed(BaseModel):
    detail: str

    class Config:
        schema_extra = {'example': {'detail': 'Method not allowed'}}
