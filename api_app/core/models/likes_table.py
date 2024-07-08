from sqlalchemy import (
    Column,
    ForeignKey,
    Table,
)

from .base import Base

likes_table = Table(
    "likes_table",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column("tweet_id", ForeignKey("tweets.id"), primary_key=True, index=True),
)
