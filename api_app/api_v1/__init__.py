from typing import Annotated

from fastapi import APIRouter, Security, UploadFile, Path, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_app.api_v1.dependencies import (
    get_user_by_api_key,
    Client,
    read_and_write_image,
    get_image,
)
from api_app.core.models import db_helper
from api_app.api_v1.tweets.views import router as tweets_router
from api_app.api_v1.users.views import router as users_router
from api_app.api_v1.schemas import SuccessfulResultSchema, ErrorResponseSchema

router = APIRouter()

router.include_router(router=users_router, prefix="/users")
router.include_router(router=tweets_router, prefix="/tweets")


@router.post(
    "/medias",
    status_code=201,
    response_model=SuccessfulResultSchema,
    responses={
        415: {"description": "UNSUPPORTED_MEDIA_TYPE", "model": ErrorResponseSchema}
    },
)
async def save_image(
    file: UploadFile,
    client: Client = Security(get_user_by_api_key),
):
    """
    Сохранение изображения и возврат его ID.
    """
    image_id: int = await read_and_write_image(client.session, file)
    return {"result": True, "media_id": image_id}


@router.get(
    "/medias/{id_image}",
    responses={404: {"description": "Not Found", "model": ErrorResponseSchema}},
)
async def get_image_view(
    id_image: Annotated[int, Path(ge=1)],
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
):
    """
    Получение изображения по его ID.
    """
    image_body = await get_image(session, id_image)
    return Response(content=image_body, media_type="image/png")
