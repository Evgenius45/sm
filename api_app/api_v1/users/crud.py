from sqlalchemy import select, insert, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api_app.core.models import User, followers_user


async def get_user_full(session: AsyncSession, user_id: int) -> User | None:
    """
    Получение данных пользователя по Id
    """
    stmt = (
        select(User)
        .options(joinedload(User.following))
        .options(joinedload(User.followers))
        .options(joinedload(User.tweets))
        .filter(User.id == user_id)
    )

    return await session.scalar(stmt)


async def insert_followers_user(
    session: AsyncSession, user_id: int, followed_user_id: int
) -> None:
    """
    Добавление пользователя в список подписчиков
    """
    stmt = insert(followers_user).values(
        followed_id=followed_user_id, follower_id=user_id
    )
    await session.execute(stmt)
    await session.commit()


async def delete_followers_user(
    session: AsyncSession, user_id: int, followed_user_id: int
):
    """
    Удаление пользователя из списка подписчиков
    """
    stmt = delete(followers_user).where(
        and_(
            followers_user.c.followed_id == followed_user_id,
            followers_user.c.follower_id == user_id,
        )
    )
    await session.execute(stmt)
    await session.commit()
