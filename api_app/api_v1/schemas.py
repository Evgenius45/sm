from pydantic import BaseModel


class SuccessfulResultSchema(BaseModel):
    """Схема результата успешного выполнения запроса"""

    result: bool
    media_id: int


class ErrorResponseSchema(BaseModel):
    """Схема ошибки запроса"""

    result: bool = False
    error_type: str
    error_message: str
