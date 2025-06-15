from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text

from database import Base


class Channel(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    channel_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    is_own_message = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
