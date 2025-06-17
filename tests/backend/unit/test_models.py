import pytest
from datetime import datetime
from src.backend.models import Channel, Message


def test_channel_creation(test_db):
    """チャンネルモデルの作成テスト"""
    channel = Channel(
        id="test_channel",
        name="テストチャンネル"
    )
    test_db.add(channel)
    test_db.commit()
    
    assert channel.id == "test_channel"
    assert channel.name == "テストチャンネル"
    assert isinstance(channel.created_at, datetime)


def test_message_creation(test_db, seed_channels):
    """メッセージモデルの作成テスト"""
    channel = seed_channels[0]
    message = Message(
        id="test_msg_001",
        channel_id=channel.id,
        user_id="test_user",
        user_name="テストユーザー",
        content="テストメッセージ",
        timestamp=datetime.now(),
        is_own_message=True
    )
    test_db.add(message)
    test_db.commit()
    
    assert message.id == "test_msg_001"
    assert message.channel_id == channel.id
    assert message.user_id == "test_user"
    assert message.user_name == "テストユーザー"
    assert message.content == "テストメッセージ"
    assert message.is_own_message is True
    assert isinstance(message.created_at, datetime)
    assert isinstance(message.timestamp, datetime)


def test_channel_messages_relationship(test_db, seed_channels):
    """チャンネルとメッセージのリレーションテスト"""
    channel = seed_channels[0]
    
    # 複数のメッセージを作成
    for i in range(3):
        message = Message(
            id=f"rel_test_msg_{i}",
            channel_id=channel.id,
            user_id=f"user_{i}",
            user_name=f"ユーザー{i}",
            content=f"メッセージ{i}",
            timestamp=datetime.now(),
            is_own_message=False
        )
        test_db.add(message)
    
    test_db.commit()
    
    # リレーションシップを確認
    messages = test_db.query(Message).filter(Message.channel_id == channel.id).all()
    assert len(messages) == 3
    assert all(msg.channel_id == channel.id for msg in messages)


def test_message_ordering(test_db, seed_channels):
    """メッセージの作成日時順ソートテスト"""
    channel = seed_channels[0]
    
    # 時系列でメッセージを作成
    messages_data = []
    for i in range(3):
        message = Message(
            id=f"order_test_msg_{i}",
            channel_id=channel.id,
            user_id="test_user",
            user_name="テストユーザー",
            content=f"メッセージ{i}",
            timestamp=datetime.now(),
            is_own_message=False
        )
        test_db.add(message)
        test_db.commit()  # 各メッセージを個別にコミットして時刻を確実に分ける
        messages_data.append(message)
    
    # 作成日時昇順で取得
    ordered_messages = (
        test_db.query(Message)
        .filter(Message.channel_id == channel.id)
        .order_by(Message.created_at.asc())
        .all()
    )
    
    # 順序が正しいことを確認
    for i in range(len(ordered_messages) - 1):
        assert ordered_messages[i].created_at <= ordered_messages[i + 1].created_at