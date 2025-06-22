from sqlalchemy.orm import Session

try:
    from .models import Channel, Message
    from .schemas import MessageCreate
except ImportError:
    from models import Channel, Message
    from schemas import MessageCreate


def create_message(db: Session, message: MessageCreate) -> Message:
    """メッセージを作成"""
    db_message = Message(
        id=message.id,
        channel_id=message.channel_id,
        user_id=message.user_id,
        user_name=message.user_name,
        content=message.content,
        timestamp=message.timestamp,
        is_own_message=message.is_own_message,
    )
    try:
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception:
        db.rollback()
        raise


def get_channel_messages(db: Session, channel_id: str, skip: int = 0, limit: int = 100) -> list[Message]:
    """チャンネルのメッセージを取得"""
    if skip < 0:
        raise ValueError("skip parameter must be non-negative")
    if limit <= 0:
        raise ValueError("limit parameter must be positive")

    return (
        db.query(Message)
        .filter(Message.channel_id == channel_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_channel_messages_count(db: Session, channel_id: str) -> int:
    """チャンネルのメッセージ総数を取得"""
    return db.query(Message).filter(Message.channel_id == channel_id).count()


def get_recent_channel_messages(db: Session, channel_id: str, limit: int = 30) -> list[Message]:
    """指定チャンネルの最新メッセージを指定件数取得（時系列順）"""
    if limit <= 0:
        raise ValueError("limit parameter must be positive")

    # 最新のlimit件を降順で取得して、時系列順に並び替え
    recent_messages = (
        db.query(Message)
        .filter(Message.channel_id == channel_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )

    # 時系列順に並び替えて返す
    return list(reversed(recent_messages))


def get_channels(db: Session) -> list[Channel]:
    """全チャンネルを取得"""
    return db.query(Channel).all()
