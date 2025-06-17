"""バックエンドテスト専用のfixture定義"""

import pytest
from datetime import datetime
from src.backend.models import Message


@pytest.fixture
def sample_message_data():
    """テスト用のサンプルメッセージデータ"""
    return {
        "id": "test_msg_123",
        "channel_id": "1",
        "user_id": "test_user",
        "user_name": "テストユーザー",
        "content": "テストメッセージ",
        "timestamp": datetime.now().isoformat() + "Z",
        "is_own_message": True,
    }


@pytest.fixture
def create_test_messages(test_db):
    """テストメッセージを作成するヘルパー関数"""
    def _create_messages(channel_id: str, count: int = 5):
        messages = []
        for i in range(count):
            message = Message(
                id=f"test_msg_{channel_id}_{i}",
                channel_id=channel_id,
                user_id=f"user_{i}",
                user_name=f"ユーザー{i}",
                content=f"テストメッセージ{i}",
                timestamp=datetime.now(),
                is_own_message=i % 2 == 0,
            )
            test_db.add(message)
            messages.append(message)
        
        test_db.commit()
        return messages
    
    return _create_messages