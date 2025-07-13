from pydantic import BaseModel, ConfigDict


class HTTP400BadRequest(BaseModel):
    detail: str

    model_config = ConfigDict(json_schema_extra={'example': {'detail': 'Bad request'}})


class HTTP401Unauthorized(BaseModel):
    detail: str

    model_config = ConfigDict(
        json_schema_extra={'example': {'detail': 'Could not validate credentials'}},
    )


class HTTP402PaymentRequired(BaseModel):
    detail: str

    model_config = ConfigDict(
        json_schema_extra={'example': {'detail': 'Payment required'}},
    )


class HTTP403Forbidden(BaseModel):
    detail: str

    model_config = ConfigDict(
        json_schema_extra={'example': {'detail': 'Not authenticated'}},
    )


class HTTP404NotFound(BaseModel):
    detail: str

    model_config = ConfigDict(
        json_schema_extra={'example': {'detail': 'Item not found'}},
    )


class HTTP405MethodNotAllowed(BaseModel):
    detail: str

    model_config = ConfigDict(
        json_schema_extra={'example': {'detail': 'Method not allowed'}},
    )
