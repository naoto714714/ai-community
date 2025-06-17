from datetime import datetime

from src.backend import crud
from src.backend.schemas import MessageCreate


def test_get_channels(test_db, seed_channels):
    """チャンネル一覧取得のテスト"""
    from src.backend.models import Channel

    channels = crud.get_channels(test_db)

    assert len(channels) == 5
    assert all(isinstance(ch, Channel) for ch in channels)

    # IDと名前を確認
    channel_names = [ch.name for ch in channels]
    assert "雑談" in channel_names
    assert "ゲーム" in channel_names
    assert "音楽" in channel_names


def test_create_message(test_db, seed_channels):
    """メッセージ作成のテスト"""
    channel = seed_channels[0]

    message_data = MessageCreate(
        id="crud_test_msg_001",
        channel_id=channel.id,
        user_id="test_user",
        user_name="テストユーザー",
        content="CRUDテストメッセージ",
        timestamp=datetime.now(),
        is_own_message=True,
    )

    created_message = crud.create_message(test_db, message_data)

    assert created_message.id == "crud_test_msg_001"
    assert created_message.channel_id == channel.id
    assert created_message.content == "CRUDテストメッセージ"
    assert created_message.user_name == "テストユーザー"

    # データベースに保存されているか確認
    from src.backend.models import Message

    saved_message = test_db.query(Message).filter(Message.id == "crud_test_msg_001").first()
    assert saved_message is not None
    assert saved_message.content == "CRUDテストメッセージ"


def test_get_channel_messages(test_db, seed_channels, create_test_messages):
    """チャンネルメッセージ取得のテスト"""
    channel = seed_channels[0]

    # テストメッセージを作成
    create_test_messages(channel.id, 10)

    # 全件取得
    messages = crud.get_channel_messages(test_db, channel.id)
    assert len(messages) == 10

    # ページネーションのテスト（skip=2, limit=5）
    paginated_messages = crud.get_channel_messages(test_db, channel.id, skip=2, limit=5)
    assert len(paginated_messages) == 5

    # 作成日時昇順で返されることを確認
    for i in range(len(paginated_messages) - 1):
        assert paginated_messages[i].created_at <= paginated_messages[i + 1].created_at


def test_get_channel_messages_count(test_db, seed_channels, create_test_messages):
    """チャンネルメッセージ数取得のテスト"""
    channel1 = seed_channels[0]
    channel2 = seed_channels[1]

    # チャンネル1に5件、チャンネル2に3件のメッセージを作成
    create_test_messages(channel1.id, 5)
    create_test_messages(channel2.id, 3)

    count1 = crud.get_channel_messages_count(test_db, channel1.id)
    count2 = crud.get_channel_messages_count(test_db, channel2.id)

    assert count1 == 5
    assert count2 == 3


def test_create_message_with_invalid_channel(test_db):
    """存在しないチャンネルへのメッセージ作成テスト"""
    message_data = MessageCreate(
        id="invalid_channel_msg",
        channel_id="999",  # 存在しないチャンネルID
        user_id="test_user",
        user_name="テストユーザー",
        content="無効なチャンネルへのメッセージ",
        timestamp=datetime.now(),
        is_own_message=True,
    )

    # エラーは発生しないが、メッセージは作成される
    # （外部キー制約がないため）
    created_message = crud.create_message(test_db, message_data)
    assert created_message.channel_id == "999"
