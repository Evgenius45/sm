from fastapi import Depends, Header
from sqlalchemy import select

from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api_app.api_v1.crud import add_image_in_db, select_image_by_id

from werkzeug.utils import secure_filename

from api_app.core.models import User
from api_app.core.models import db_helper

OUT_PATH = Path(__file__).parent / "./../../static_db/images"
OUT_PATH.mkdir(exist_ok=True, parents=True)
OUT_PATH = OUT_PATH.absolute()

TYPES_MEDIA: tuple = ("image/jpg", "image/png", "image/jpeg", "image/webp")


class UnicornException(Exception):
    def __init__(self, status_code: int, error_type: str, error_message: str):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message


async def read_and_write_image(
    session: AsyncSession,
    img: UploadFile,
) -> int:
    """
    Сохраняет файл в каталог
    """

    if img.content_type in TYPES_MEDIA:
        file_name: str = secure_filename(str(img.filename))
        file_body = await img.read()
        return await add_image_in_db(session, file_name, file_body)

    raise UnicornException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        error_type="UNSUPPORTED_MEDIA_TYPE",
        error_message="File type not supported",
    )


class Client:
    """Клиент прошедший идентификацию"""

    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.user_id = user_id


async def get_user_by_api_key(
    api_key: str = Header(alias="api-key"),
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> Client:
    """
    Проверка "api-key" на подлинность
    """
    stmt = select(User.id).where(User.api_key == api_key)

    if user_id := await session.scalar(stmt):
        client = Client(session, int(user_id))
        return client
    raise UnicornException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_type="Not Found",
        error_message="User is not found.",
    )


async def get_image(session: AsyncSession, id_image: int) -> BYTEA:
    """
    Получение изображения
    """

    if image_body := await select_image_by_id(session, id_image):
        return image_body
    raise UnicornException(
        status_code=status.HTTP_404_NOT_FOUND,
        error_type="Not Found",
        error_message="Image is not found.",
    )
