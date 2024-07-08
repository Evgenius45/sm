from typing import TYPE_CHECKING
from sqlalchemy import String, ForeignKey

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import BYTEA
from api_app.core.models.base import Base

if TYPE_CHECKING:
    from api_app.core.models.tweet import Tweet


class Media(Base):
    """Model Media."""

    file_name: Mapped[str] = mapped_column(String(length=200))
    file_body: Mapped[BYTEA] = mapped_column(BYTEA)

    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), nullable=True)
    tweet: Mapped["Tweet"] = relationship(
        "Tweet", back_populates="tweet_media_ids", single_parent=True
    )
