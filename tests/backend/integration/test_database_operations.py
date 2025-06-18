from datetime import datetime, timedelta

from src.backend import crud
from src.backend.models import Channel, Message
from src.backend.schemas import MessageCreate


def test_database_transaction_rollback(test_db):
    """データベーストランザクションのロールバックテスト"""
    # 初期状態のメッセージ数を確認
    initial_count = test_db.query(Message).count()

    try:
        # トランザクション内でメッセージを作成
        message = Message(
            id="rollback_test",
            channel_id="1",
            user_id="test_user",
            user_name="テストユーザー",
            content="ロールバックテスト",
            timestamp=datetime.now(),
            is_own_message=True,
        )
        test_db.add(message)

        # エラーを意図的に発生させる
        raise Exception("意図的なエラー")
    except Exception:
        test_db.rollback()

    # ロールバック後のメッセージ数を確認
    final_count = test_db.query(Message).count()
    assert final_count == initial_count


def test_bulk_message_creation(test_db, seed_channels):
    """複数メッセージ作成のテスト"""
    channel = seed_channels[0]

    # 複数のメッセージを連続して作成
    message_ids = []
    for i in range(10):
        message_data = MessageCreate(
            id=f"bulk_msg_{i}",
            channel_id=channel.id,
            user_id=f"user_{i}",
            user_name=f"ユーザー{i}",
            content=f"一括メッセージ{i}",
            timestamp=datetime.now(),
            is_own_message=False,
        )

        created_message = crud.create_message(test_db, message_data)
        message_ids.append(created_message.id)

    # すべてのメッセージが作成されていることを確認
    messages = test_db.query(Message).filter(Message.id.in_(message_ids)).all()
    assert len(messages) == 10
    assert all(msg.id in message_ids for msg in messages)


def test_message_ordering_consistency(test_db, seed_channels):
    """メッセージ順序の一貫性テスト"""
    channel = seed_channels[0]

    # 異なるタイムスタンプでメッセージを作成
    base_time = datetime.now()
    for i in range(5):
        message = Message(
            id=f"order_test_{i}",
            channel_id=channel.id,
            user_id="test_user",
            user_name="テストユーザー",
            content=f"順序テスト{i}",
            timestamp=base_time + timedelta(minutes=i),
            is_own_message=False,
        )
        test_db.add(message)

    test_db.commit()

    # created_atでソートして取得
    messages = crud.get_channel_messages(test_db, channel.id)

    # 順序が保たれていることを確認
    for i in range(len(messages) - 1):
        assert messages[i].created_at <= messages[i + 1].created_at


def test_channel_message_cascade(test_db):
    """チャンネルとメッセージのカスケード動作テスト"""
    # 新しいチャンネルを作成
    channel = Channel(id="cascade_test", name="カスケードテスト")
    test_db.add(channel)
    test_db.commit()

    # チャンネルにメッセージを追加
    for i in range(3):
        message = Message(
            id=f"cascade_msg_{i}",
            channel_id=channel.id,
            user_id="test_user",
            user_name="テストユーザー",
            content=f"カスケードメッセージ{i}",
            timestamp=datetime.now(),
            is_own_message=False,
        )
        test_db.add(message)

    test_db.commit()

    # メッセージが存在することを確認
    messages = test_db.query(Message).filter(Message.channel_id == channel.id).all()
    assert len(messages) == 3

    # 注意: 現在の実装では外部キー制約がないため、
    # チャンネルを削除してもメッセージは残る
    test_db.delete(channel)
    test_db.commit()

    # チャンネルが削除されたことを確認
    deleted_channel = test_db.query(Channel).filter(Channel.id == "cascade_test").first()
    assert deleted_channel is None

    # メッセージはまだ存在する（外部キー制約がないため）
    orphan_messages = test_db.query(Message).filter(Message.channel_id == "cascade_test").all()
    assert len(orphan_messages) == 3


def test_database_session_isolation(test_db, seed_channels):
    """データベースセッションの分離テスト"""
    from sqlalchemy.orm import sessionmaker

    channel = seed_channels[0]
    # テストセッションからエンジンを取得
    engine = test_db.bind
    SessionLocal = sessionmaker(bind=engine)

    # セッション1でメッセージを作成（コミットしない）
    message1 = Message(
        id="isolation_test_1",
        channel_id=channel.id,
        user_id="user1",
        user_name="ユーザー1",
        content="分離テスト1",
        timestamp=datetime.now(),
        is_own_message=True,
    )
    test_db.add(message1)
    # まだコミットしない

    # 同じセッションでは見える
    found = test_db.query(Message).filter(Message.id == "isolation_test_1").first()
    assert found is not None

    # 新しい別のセッションを作成してトランザクション分離をテスト
    separate_db = SessionLocal()
    try:
        # 別のセッションからはコミット前は見えない
        not_found = separate_db.query(Message).filter(Message.id == "isolation_test_1").first()
        assert not_found is None
    finally:
        separate_db.close()

    # コミット
    test_db.commit()

    # コミット後は別のセッションからも見える
    another_db = SessionLocal()
    try:
        found_after = another_db.query(Message).filter(Message.id == "isolation_test_1").first()
        assert found_after is not None
    finally:
        another_db.close()
