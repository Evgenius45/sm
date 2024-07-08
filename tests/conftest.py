import asyncio
from pathlib import Path
from typing import AsyncGenerator

import httpx
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)
from testcontainers.postgres import PostgresContainer

from api_app.core.models import Base, db_helper, DatabaseHelper, User, Tweet, Media
from api_app.main import app

postgres_container = PostgresContainer("postgres", driver="asyncpg")
postgres_container.start()

url = postgres_container.get_connection_url()

tests_db_helper = DatabaseHelper(url=url, echo=False)

engine_test = tests_db_helper.engine
async_session_maker = tests_db_helper.session_factory

app.dependency_overrides[db_helper.scoped_session_dependency] = (
    tests_db_helper.scoped_session_dependency
)


async def insert_objects_bd(async_session: async_sessionmaker[AsyncSession]) -> None:
    """Adding some test data."""
    async with async_session() as session:
        async with session.begin():
            user_1 = User(name="Start", api_key="test")
            user_2 = User(name="Dimon", api_key="test_2")
            user_3 = User(name="Jon", api_key="test_3")
            user_4 = User(name="Ivan", api_key="test_4")

            with open(Path(__file__).parent / "files_for_tests/1.jpeg", "rb") as f:
                x = f.read()
            media_1 = Media(file_body=x, file_name="1.jpeg")
            media_2 = Media(file_body=x, file_name="2.jpeg")

            session.add_all([user_1, user_2, user_3, user_4, media_1, media_2])

            user_1.following.append(user_4)
            user_2.following.append(user_3)
            user_4.following.append(user_1)

            tweet_1 = Tweet(tweet_data="text_1")
            tweet_2 = Tweet(tweet_data="text_2")
            tweet_3 = Tweet(tweet_data="text_3")

            tweet_1.tweet_media_ids.append(media_1)
            tweet_1.tweet_media_ids.append(media_2)

            user_1.tweets.append(tweet_1)
            user_2.tweets.append(tweet_2)
            user_4.tweets.append(tweet_3)

            user_2.likes_tw.append(tweet_1)
            user_4.likes_tw.append(tweet_2)

            await session.commit()


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await insert_objects_bd(async_session_maker)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    postgres_container.stop()


@pytest_asyncio.fixture
async def restore_database():
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await insert_objects_bd(async_session_maker)


@pytest_asyncio.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


transport = httpx.ASGITransport(app=app)


@pytest_asyncio.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session")
async def session():
    async with async_session_maker() as session:
        yield session
