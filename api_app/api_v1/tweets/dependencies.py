from sqlalchemy.ext.asyncio import AsyncSession

from api_app.api_v1.tweets.crud import create_like_tweet, delete_like_tw, delete_tweet
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from starlette import status
from api_app.api_v1.dependencies import UnicornException


async def add_like(session, user_id, tweet_id):
    """Добавление лайка твиту"""
    try:
        await create_like_tweet(session, user_id, tweet_id)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "result": False,
                "error_type": "Conflict",
                "error_message": "User is already followed or does not tweet exist.",
            },
        )


async def delete_like_tweet(session: AsyncSession, user_id: int, tweet_id: int) -> dict:
    """
    Удалить лайк у твита
    """
    if await delete_like_tw(session, user_id, tweet_id):
        return {"result": True}
    raise UnicornException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_type="Not Found",
        error_message="User is not found.",
    )


async def delete_your_tweet(session: AsyncSession, user_id: int, tweet_id: int) -> dict:
    """
    Удалить твит.
    """
    result = await delete_tweet(session, user_id, tweet_id)
    if result:
        return {"result": True}
    raise UnicornException(
        status_code=status.HTTP_409_CONFLICT,
        error_type="Conflict",
        error_message="The user is not the owner or there is no such tweet.",
    )
