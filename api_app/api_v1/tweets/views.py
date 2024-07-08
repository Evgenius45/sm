from typing import Annotated

from fastapi import APIRouter
from fastapi import Security, Path

from api_app.api_v1.dependencies import get_user_by_api_key, Client
from api_app.api_v1.schemas import ErrorResponseSchema
from api_app.api_v1.tweets.dependencies import (
    add_like,
    delete_like_tweet,
    delete_your_tweet,
)
from api_app.api_v1.tweets.schemas import (
    InputTweetSchema,
    ResultCreateTweetSchema,
    FollowingTweetSchema,
    SuccessfulResultSchema,
)
from api_app.api_v1.tweets.crud import add_tweet_in_db, get_following_tweet

router = APIRouter(tags=["Tweets"])


@router.post("", response_model=ResultCreateTweetSchema, status_code=201)
async def add_tweets_view(
    tweet_in: InputTweetSchema, client: Client = Security(get_user_by_api_key)
):
    """
    Создание твита
    """
    return await add_tweet_in_db(client.session, client.user_id, tweet_in)


@router.get("", response_model=FollowingTweetSchema)
async def get_all_tweets_view(client: Client = Security(get_user_by_api_key)):
    """
    Получение твитов пользователя.
    """
    return await get_following_tweet(client.session, client.user_id)


@router.post(
    "/{tweet_id}/likes",
    status_code=201,
    response_model=SuccessfulResultSchema,
    responses={409: {"description": "Conflict", "model": ErrorResponseSchema}},
)
async def add_like_tweet_view(
    tweet_id: Annotated[int, Path(ge=1)],
    client: Client = Security(get_user_by_api_key),
):
    """
    Добавить лайк твиту.
    """
    await add_like(client.session, client.user_id, tweet_id)

    return {"result": True}


@router.delete(
    "/{tweet_id}/likes",
    status_code=201,
    response_model=SuccessfulResultSchema,
    responses={404: {"description": "Not Found", "model": ErrorResponseSchema}},
)
async def delete_like_tweet_view(
    tweet_id: Annotated[int, Path(ge=1)], client: Client = Security(get_user_by_api_key)
):
    """
    Удалить лайк с твита
    """
    return await delete_like_tweet(client.session, client.user_id, tweet_id)


@router.delete(
    "/{tweet_id}",
    status_code=201,
    response_model=SuccessfulResultSchema,
    responses={409: {"description": "Conflict", "model": ErrorResponseSchema}},
)
async def delete_tweet_view(
    tweet_id: Annotated[int, Path(ge=1)], client: Client = Security(get_user_by_api_key)
):
    """
    Удаление твита.
    """
    return await delete_your_tweet(client.session, client.user_id, tweet_id)
