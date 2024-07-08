from typing import List, TYPE_CHECKING

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_app.core.models.base import Base
from api_app.core.models.likes_table import likes_table

if TYPE_CHECKING:
    from api_app.core.models.user import User
    from api_app.core.models.media import Media


class Tweet(Base):
    """Model Tweet"""

    tweet_data: Mapped[str] = mapped_column(String(length=10000))
    time_created = Column(DateTime(timezone=True), server_default=func.now())

    # tweet_media_ids: Mapped[List[str]] = mapped_column(
    #     ARRAY(String(200)),
    #     nullable=True,
    # )
    tweet_media_ids: Mapped[List["Media"]] = relationship(
        "Media", lazy="joined", back_populates="tweet", cascade="all, delete-orphan"
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tweets",
    )
    likes_us: Mapped[List["User"]] = relationship(
        "User",
        secondary=likes_table,
        back_populates="likes_tw",
    )

    def __repr__(self) -> str:
        return f"Tweet(id={self.id}, tweet_data={self.tweet_data}"
