from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from api_app.api_v1.dependencies import UnicornException

from api_app.api_v1.users.crud import (
    get_user_full,
    insert_followers_user,
    delete_followers_user,
)


async def get_user_by_ip(
    user_pk: int,
    session: AsyncSession,
) -> dict:
    """
    Получение данных пользователя по Id
    """

    if user := await get_user_full(session, user_pk):
        return {"result": True, "user": user}
    raise UnicornException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_type="Not Found",
        error_message="User is not found.",
    )


async def add_follow(session, user_id, followed_user_id):
    """Добавление подписки на пользователя"""
    try:
        await insert_followers_user(session, user_id, followed_user_id)
    except IntegrityError:
        raise UnicornException(
            status_code=status.HTTP_409_CONFLICT,
            error_type="Conflict",
            error_message="User is already followed or does not exist.",
        )


async def delete_follow(session, user_id, followed_user_id):
    """Удаление подписки на пользователя"""
    try:
        await delete_followers_user(session, user_id, followed_user_id)
    except IntegrityError:
        raise UnicornException(
            status_code=status.HTTP_409_CONFLICT,
            error_type="Conflict",
            error_message="User is not already followed.",
        )
