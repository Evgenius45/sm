from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, func, insert
from api_app.core.models import likes_table, Tweet, Media
from tests.schemas import (
    schema_add_tweets_success,
    schema_get_tweets_success,
    schema_exceptions,
)
from api_app.api_v1.dependencies import OUT_PATH


async def test_add_tweets_success(ac: AsyncClient, session: AsyncSession):
    """Тест создания твита"""

    media_1 = Media(id=3, file_body=b"1222233", file_name="1.jpeg")
    media_2 = Media(id=4, file_body=b"1222233", file_name="2.jpeg")
    session.add_all([media_1, media_2])
    await session.commit()
    x = await session.scalars(select(Media))
    print(11111, [y.id for y in x.all()])
    response = await ac.post(
        "/api/tweets",
        headers={"api-key": "test"},
        json={"tweet_data": "Тестовая строка", "tweet_media_ids": [3, 4]},
    )
    assert response.status_code == 201
    result = response.json()
    schema_add_tweets_success.validate_python(result)

    twit = await session.scalar(select(Tweet).filter(Tweet.id == result["tweet_id"]))
    await session.delete(twit)
    await session.commit()
    result = await session.scalars(select(Media))
    assert len(result.all()) == 2
    await session.commit()


async def test_get_all_tweets_success(ac: AsyncClient):
    """Тест получения всех твитов"""

    response = await ac.get(
        "/api/tweets",
        headers={"api-key": "test"},
    )
    result = response.json()
    print(result)
    assert len(result["tweets"]) == 2
    schema_get_tweets_success.validate_python(result)


async def test_add_like_tweet_success(ac: AsyncClient, session: AsyncSession):
    """Тест добавления лайка"""

    result = await session.scalar(
        select(func.count(likes_table.c.tweet_id)).where(likes_table.c.tweet_id == 2)
    )
    if not isinstance(result, int):
        assert False
    expected_quantity = result + 1
    print(expected_quantity)
    response = await ac.post(
        "/api/tweets/2/likes",
        headers={"api-key": "test"},
    )
    assert response.status_code == 201
    result = response.json()
    assert result["result"]
    result_2 = await session.scalar(
        select(func.count(likes_table.c.tweet_id)).where(likes_table.c.tweet_id == 2)
    )
    assert result_2 == expected_quantity
    await session.execute(
        delete(likes_table).where(
            and_(likes_table.c.tweet_id == 2), likes_table.c.user_id == 1
        ),
    )
    await session.commit()


async def test_delete_like_tweet_success(ac: AsyncClient, session: AsyncSession):
    """Удаление лайка TODO"""
    result_3 = await session.scalar(
        select(func.count(likes_table.c.tweet_id)).where(likes_table.c.tweet_id == 1)
    )
    print(result_3)

    response = await ac.delete(
        "/api/tweets/1/likes",
        headers={"api-key": "test_2"},
    )
    assert response.status_code == 201
    result = response.json()
    assert result["result"]
    result_2 = await session.scalar(
        select(func.count(likes_table.c.tweet_id)).where(likes_table.c.tweet_id == 1)
    )
    print(result_2)
    assert result_2 == 0
    await session.execute(insert(likes_table).values(user_id=2, tweet_id=1))
    await session.commit()


async def test_delete_like_tweet_invalid(ac: AsyncClient, session: AsyncSession):
    """Удаление несуществующего лайка TODO"""

    response = await ac.delete(
        "/api/tweets/55/likes",
        headers={"api-key": "test"},
    )
    response.status_code = 404
    result = response.json()
    schema_exceptions.validate_python(result)


async def test_delete_tweet_invalid(ac: AsyncClient, session: AsyncSession):
    """Удаление несуществующего твита TODO"""
    set_data = [("9999", "test"), ("2", "test")]
    for id_i, api_key in set_data:
        response = await ac.delete(
            f"/api/tweets/{id_i}",
            headers={"api-key": api_key},
        )
        response.status_code = 404
        result = response.json()
        schema_exceptions.validate_python(result)


async def test_delete_tweet_success(
    ac: AsyncClient, session: AsyncSession, restore_database
):
    """Удаление твита TODO"""
    file_1 = open(f"{OUT_PATH}/1.jpeg", "w")
    file_2 = open(f"{OUT_PATH}/2.jpeg", "w")
    file_2.close()
    file_1.close()

    response = await ac.delete(
        "/api/tweets/1",
        headers={"api-key": "test"},
    )

    assert response.status_code == 201
    result = response.json()
    assert result["result"]
