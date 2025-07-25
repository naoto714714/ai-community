"""データベースモデル定義.

ChannelとMessageのSQLAlchemyモデルを定義し、チャットアプリケーションのデータ構造を表現します。
"""

from datetime import UTC, datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

try:
    from .database import Base
except ImportError:
    from database import Base


class Channel(Base):
    """チャットチャンネルモデル"""

    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class Message(Base):
    """チャットメッセージモデル"""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    channel_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    user_type: Mapped[str] = mapped_column(String, nullable=False, default="user")  # "user", "ai"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    is_own_message: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
