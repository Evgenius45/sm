from typing import List, TYPE_CHECKING

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_app.core.models.base import Base
from api_app.core.models.likes_table import likes_table

if TYPE_CHECKING:
    from api_app.core.models.tweet import Tweet

followers_user = Table(
    "followers_user",
    Base.metadata,
    Column("follower_id", ForeignKey("users.id"), primary_key=True, index=True),
    Column("followed_id", ForeignKey("users.id"), primary_key=True, index=True),
)


class User(Base):
    """Model User."""

    api_key: Mapped[str] = mapped_column(String(length=50), unique=True)
    name: Mapped[str] = mapped_column(String(length=50))
    likes_tw: Mapped[List["Tweet"]] = relationship(
        secondary=likes_table,
        back_populates="likes_us",
        lazy="select",
        cascade="all, delete",
    )
    tweets: Mapped[List["Tweet"]] = relationship(
        "Tweet",
        back_populates="user",
        lazy="select",
        cascade="all, delete",
    )
    following: Mapped[List["User"]] = relationship(
        "User",
        secondary=followers_user,
        primaryjoin="User.id==followers_user.c.follower_id",
        secondaryjoin="User.id==followers_user.c.followed_id",
        back_populates="followers",
        lazy="select",
    )
    followers: Mapped[List["User"]] = relationship(
        "User",
        secondary=followers_user,
        primaryjoin="User.id==followers_user.c.followed_id",
        secondaryjoin="User.id==followers_user.c.follower_id",
        back_populates="following",
        lazy="select",
    )
