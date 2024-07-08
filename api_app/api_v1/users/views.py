from typing import Annotated

from fastapi import APIRouter, Path, Security

from api_app.api_v1.schemas import ErrorResponseSchema
from api_app.api_v1.users.dependencies import (
    get_user_by_ip,
    add_follow,
    delete_follow,
)
from api_app.api_v1.users.schemas import OutputUserSchemaFull, SuccessfulResultSchema
from api_app.api_v1.dependencies import get_user_by_api_key, Client

router = APIRouter(tags=["Users"])


@router.get(
    "/me",
    response_model=OutputUserSchemaFull,
    responses={404: {"description": "Not Found", "model": ErrorResponseSchema}},
)
async def get_user_info_by_api_key(
    client: Client = Security(get_user_by_api_key),
):
    """
    Получить информацию о своём профиле по "api_key".
    """
    return await get_user_by_ip(client.user_id, client.session)


@router.get(
    "/{user_id}",
    response_model=OutputUserSchemaFull,
    responses={404: {"description": "Not Found", "model": ErrorResponseSchema}},
)
async def get_user_info_by_id(
    user_id: Annotated[int, Path(ge=1)],
    client: Client = Security(get_user_by_api_key),
):
    """
    Получить информацию о профиле по "ip".
    """
    return await get_user_by_ip(user_id, client.session)


@router.post(
    "/{user_id}/follow",
    status_code=201,
    response_model=SuccessfulResultSchema,
    responses={409: {"description": "Conflict", "model": ErrorResponseSchema}},
)
async def add_follow_user(
    user_id: Annotated[int, Path(ge=1)],
    client: Client = Security(get_user_by_api_key),
):
    """
    Подписаться на другого пользователя
    """
    await add_follow(client.session, client.user_id, user_id)
    return {"result": True}


@router.delete(
    "/{user_id}/follow",
    status_code=201,
    response_model=SuccessfulResultSchema,
    responses={
        409: {"description": "Conflict", "model": ErrorResponseSchema},
    },
)
async def delete_follow_user(
    user_id: Annotated[int, Path(ge=1)],
    client: Client = Security(get_user_by_api_key),
):
    """
    Удаление подписки на другого пользователя
    """

    await delete_follow(client.session, client.user_id, user_id)
    return {"result": True}
