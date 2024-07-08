from typing import List, Any
from pydantic import BaseModel, ConfigDict, model_serializer


class UserSchema(BaseModel):
    name: str


class AuthorSchema(UserSchema):
    id: int


class TypeLikesUserSchema(BaseModel):
    name: str
    user_id: int


class LikesUserSchema(UserSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int  # user_id

    @model_serializer(return_type=TypeLikesUserSchema)
    def ser_model(self):
        return TypeLikesUserSchema(name=self.name, user_id=self.id)


class TweetSchema1(UserSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int  # tweet_id
    tweet_data: str
    time_created: Any
    tweet_media_ids: List[str] | None  # [id_image]
    user_id: int

    @model_serializer(return_type=TypeLikesUserSchema)
    def ser_model(self):
        return TypeLikesUserSchema(name=self.name, user_id=self.id)


class InputTweetSchema(BaseModel):
    """Схема создания твита"""

    tweet_data: str
    tweet_media_ids: List[int]


class MediaSchema(BaseModel):
    id: int

    @model_serializer()
    def ser_model(self):
        return self.id


class TweetSchema(BaseModel):
    id: int
    tweet_data: str
    time_created: Any
    tweet_media_ids: List[MediaSchema]  # [id_image]
    user_id: int


class TypeTweetSchema(BaseModel):
    id: int
    content: str
    attachments: Any
    author: AuthorSchema
    likes: List[LikesUserSchema]


class FullTweetSchema(TweetSchema):
    model_config = ConfigDict(from_attributes=True)

    user: AuthorSchema
    likes_us: List[LikesUserSchema]

    @model_serializer(return_type=TypeTweetSchema)
    def ser_model(self):
        return TypeTweetSchema(
            id=self.id,
            content=self.tweet_data,
            attachments=[
                f"/api/medias/{i_attachment.id}"
                for i_attachment in self.tweet_media_ids
            ],
            author=self.user,
            likes=self.likes_us,
        )


class FollowingTweetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    result: bool
    tweets: List[FullTweetSchema]


class TypeResultCreateTweetSchema(BaseModel):
    result: bool
    tweet_id: int


class ResultCreateTweetSchema(TweetSchema):
    @model_serializer(return_type=TypeResultCreateTweetSchema)
    def ser_model(self):
        return TypeResultCreateTweetSchema(result=True, tweet_id=self.id)


class SuccessfulResultSchema(BaseModel):
    """Схема результата успешного выполнения запроса"""

    result: bool
