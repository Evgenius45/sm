from typing import List

from pydantic import BaseModel, ConfigDict, model_serializer


class UserBaseSchema(BaseModel):
    name: str


class OutputUserSchema(UserBaseSchema):
    id: int


class UserSchemaFull(OutputUserSchema):
    model_config = ConfigDict(from_attributes=True)

    following: List[OutputUserSchema]
    followers: List[OutputUserSchema]


class TypeOutputUserSchemaFull(BaseModel):
    result: bool
    user: UserSchemaFull


class OutputUserSchemaFull(BaseModel):
    result: bool
    user: UserSchemaFull

    @model_serializer(return_type=TypeOutputUserSchemaFull)
    def ser_model(self):
        return TypeOutputUserSchemaFull(
            result=True,
            user=UserSchemaFull(
                id=self.user.id,
                name=self.user.name,
                followers=self.user.followers,
                following=self.user.following,
            ),
        )


class SuccessfulResultSchema(BaseModel):
    result: bool
