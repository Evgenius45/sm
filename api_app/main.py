from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette import status
from api_app.api_v1 import router as router_v1
from api_app.api_v1.schemas import ErrorResponseSchema
from api_app.core.config import settings
from api_app.core.models import User, Tweet, Media, db_helper, Base
from api_app.api_v1.dependencies import UnicornException


async def insert_objects_bd(async_session) -> None:
    """Заполнение базы для презентации."""
    async with async_session() as session:
        user_1 = User(name="Start", api_key="test")
        user_2 = User(name="Dimon", api_key="test_2")
        user_3 = User(name="Jon", api_key="test_3")
        user_4 = User(name="Ivan", api_key="test_4")

        with open(Path(__file__).parent / "./static_demo/1.jpeg", "rb") as f:
            file_body = f.read()
        media_1 = Media(file_body=file_body, file_name="1.jpeg")
        media_2 = Media(file_body=file_body, file_name="2.jpeg")

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if settings.api_db_echo:
        async with db_helper.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        await insert_objects_bd(db_helper.session_factory)
    yield
    if settings.api_db_echo:
        async with db_helper.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


app = FastAPI(
    lifespan=lifespan,
    responses={
        422: {
            "description": "Validation Error",
            "model": ErrorResponseSchema,
        },
    },
)

app.include_router(router=router_v1, prefix=settings.api_v1_prefix)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации запроса."""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "result": False,
            "error_type": "RequestValidationError",
            "error_message": exc.errors()[0]["msg"],
        },
    )


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    """ "Обработчик ошибок."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "result": False,
            "error_type": exc.error_type,
            "error_message": exc.error_message,
        },
    )


if __name__ == "__main__":
    uvicorn.run("main:app", app_dir="api_app", reload=True)

# docker-compose up --build
