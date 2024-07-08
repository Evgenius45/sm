from typing import List
from pydantic import TypeAdapter
from typing_extensions import TypedDict


class SchemaAddTweetsSuccess(TypedDict):
    """Схема успешного результата создания твита"""

    result: bool
    tweet_id: int


schema_add_tweets_success = TypeAdapter(SchemaAddTweetsSuccess)


class AuthorSchema(TypedDict):
    id: int
    name: str


class LikesUserShema(TypedDict):
    name: str
    user_id: int


class SchemaFullTweet(TypedDict):
    """Схема полного твита"""

    id: int
    content: str
    attachments: List[str] | None
    author: AuthorSchema
    likes: List[LikesUserShema]


class SchemaGetTweetsSuccess(TypedDict):
    """Схема успешного результата получения твитов"""

    result: bool
    tweets: List[SchemaFullTweet]


schema_get_tweets_success = TypeAdapter(SchemaGetTweetsSuccess)


class SchemaExceptions(TypedDict):
    """Схема генерации отчета ошибок"""

    result: bool
    error_type: str
    error_message: str


schema_exceptions = TypeAdapter(SchemaExceptions)


class SaveImageSuccess(TypedDict):
    """Схема успешное сохранение изображений"""

    result: bool
    media_id: int


save_image_success = TypeAdapter(SaveImageSuccess)


class FullUserSchema(TypedDict):
    """Схема полного пользователя"""

    id: int
    name: str
    following: List[AuthorSchema]
    followers: List[AuthorSchema]


class SchemaFullUserSuccess(TypedDict):
    """Схема успешного получения своей страницы"""

    result: bool
    user: FullUserSchema


schema_full_user_success = TypeAdapter(SchemaFullUserSuccess)
