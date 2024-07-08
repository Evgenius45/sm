import pytest

from api_app.core.models import Media
from pathlib import Path

from httpx import AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import save_image_success, schema_exceptions
from api_app.api_v1.crud import select_image_by_id
from api_app.api_v1.dependencies import get_image, UnicornException

OUT_PATH_TEST = Path(__file__).parent / "files_for_tests"
OUT_PATH_TEST.mkdir(exist_ok=True, parents=True)
OUT_PATH_TEST = OUT_PATH_TEST.absolute()


async def test_save_image_success(ac: AsyncClient, session: AsyncSession):
    """Тест сохранение картинок"""
    response = await ac.post(
        "/api/medias",
        headers={"api-key": "test"},
        files={"file": open(f"{OUT_PATH_TEST}/1.jpeg", "rb")},
    )
    assert response.status_code == 201
    result = response.json()
    save_image_success.validate_python(result)
    await session.scalar(
        delete(Media).where(Media.id == result["media_id"]).returning(Media.file_name)
    )


async def test_save_image_invalid(ac: AsyncClient, session: AsyncSession):
    """Тест фильтрации формата изображений"""
    response = await ac.post(
        "/api/medias",
        headers={"api-key": "test"},
        files={"file": open(f"{OUT_PATH_TEST}/3.txt", "rb")},
    )
    assert response.status_code == 415
    result = response.json()
    schema_exceptions.validate_python(result)


async def test_select_image_by_id_success(ac: AsyncClient, session: AsyncSession):
    """Тест фильтрации формата изображений"""
    result = await select_image_by_id(session, 99999)
    assert result is None
    result_2 = await select_image_by_id(session, 1)
    assert result_2


async def test_get_image_invalid(ac: AsyncClient, session: AsyncSession):
    """Ошибка если не найдено значение"""
    with pytest.raises(UnicornException):
        await get_image(session, 99999)


async def test_get_image_success(ac: AsyncClient, session: AsyncSession):
    """Успешный возврат тела картинки"""
    result = await get_image(session, 1)
    assert isinstance(result, bytes)


async def test_get_image_view_invalid(ac: AsyncClient, session: AsyncSession):
    """Тест возврата изображения по ID"""
    response = await ac.get(
        "/api/medias/1",
        headers={"api-key": "test"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
