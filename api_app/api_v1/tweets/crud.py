from typing import Dict

from sqlalchemy.orm import selectinload

from api_app.api_v1.tweets.schemas import InputTweetSchema

from api_app.core.models import Tweet, followers_user, likes_table, Media
from sqlalchemy import select, insert, delete, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession


async def add_tweet_in_db(
    session: AsyncSession,
    user_id: int,
    tweet_in: InputTweetSchema,
) -> Tweet:
    """
    Добавление нового твита
    """
    tweet = Tweet(user_id=user_id, tweet_data=tweet_in.tweet_data, tweet_media_ids=[])
    session.add(tweet)
    if len(tweet_in.tweet_data) > 0:
        stmt = (
            update(Media)
            .where(Media.id.in_(tweet_in.tweet_media_ids))
            .values(tweet_id=tweet.id)
            .returning(Media)
        )
        medias = await session.scalars(stmt)
        tweet.tweet_media_ids = list(medias.all())
    await session.commit()
    return tweet


async def get_following_tweet(session: AsyncSession, user_id: int) -> Dict:
    """
    Получение списка твитов пользователя и твитов пользователей на кого он подписан.
    """

    user_following_stmt = select(followers_user.c.follower_id).filter(
        followers_user.c.followed_id == user_id
    )
    stmt = (
        select(Tweet)
        .options(selectinload(Tweet.user))
        .options(selectinload(Tweet.likes_us))
        .options(selectinload(Tweet.tweet_media_ids))
        .filter(or_(Tweet.user_id.in_(user_following_stmt), Tweet.user_id == user_id))
        .order_by(Tweet.time_created)
    )
    result = await session.scalars(stmt)
    return {"result": True, "tweets": [tweet for tweet in result.all()]}


async def create_like_tweet(session: AsyncSession, user_id: int, tweet_id) -> None:
    """
    Добавить лайк твиту.
    """
    stmt = insert(likes_table).values(user_id=user_id, tweet_id=tweet_id)
    await session.execute(stmt)
    await session.commit()


async def delete_like_tw(session: AsyncSession, user_id: int, tweet_id) -> bool:
    """
    Удалить лайк с твита
    """
    stmt = (
        delete(likes_table)
        .where(
            and_(
                likes_table.c.user_id == user_id,
                likes_table.c.tweet_id == tweet_id,
            )
        )
        .returning(likes_table)
    )
    response = await session.execute(stmt)
    await session.commit()
    if response.fetchall():
        return True
    return False


async def delete_tweet(session: AsyncSession, user_id: int, tweet_id) -> Tweet | None:
    """
    Удаление твита
    """
    tweet = await session.scalar(
        select(Tweet).where(and_(Tweet.id == tweet_id, Tweet.user_id == user_id))
    )

    if tweet:
        await session.delete(tweet)
        await session.commit()
        return tweet
    return None
