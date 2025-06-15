from sqlalchemy.orm import Session

from models import Channel, Message
from schemas import MessageCreate


def create_message(db: Session, message: MessageCreate) -> Message:
    """Create a new message"""
    timestamp = message.timestamp

    db_message = Message(
        id=message.id,
        channel_id=message.channel_id,
        user_id=message.user_id,
        user_name=message.user_name,
        content=message.content,
        timestamp=timestamp,
        is_own_message=message.is_own_message,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_channel_messages(db: Session, channel_id: str, skip: int = 0, limit: int = 100):
    """Get messages for a specific channel"""
    return (
        db.query(Message)
        .filter(Message.channel_id == channel_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_channels(db: Session):
    """Get all channels"""
    return db.query(Channel).all()
