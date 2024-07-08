from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.ext.asyncio import AsyncSession
from api_app.core.models import Media
from typing import ByteString
from sqlalchemy import select


async def add_image_in_db(
    session: AsyncSession, file_name: str, file_body: ByteString
) -> int:
    """
    Сохранение в таблицу Media имен изображений.
    """
    img: Media = Media(file_name=file_name, file_body=file_body)
    session.add(img)
    await session.commit()
    return img.id


async def select_image_by_id(session: AsyncSession, id_image: int) -> BYTEA | None:
    """
    Получение изображения по его ID.
    """
    stmt = select(Media.file_body).where(Media.id == id_image)
    image = await session.scalar(stmt)
    return image
