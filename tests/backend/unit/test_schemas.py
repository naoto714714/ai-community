from datetime import datetime

import pytest
from pydantic import ValidationError

from src.backend.schemas import ChannelResponse, MessageCreate, MessageResponse, MessagesListResponse, to_camel


def test_to_camel():
    """snake_caseからcamelCaseへの変換テスト"""
    assert to_camel("snake_case") == "snakeCase"
    assert to_camel("channel_id") == "channelId"
    assert to_camel("is_own_message") == "isOwnMessage"
    assert to_camel("created_at") == "createdAt"
    assert to_camel("simple") == "simple"
    assert to_camel("") == ""


def test_message_create_schema():
    """MessageCreateスキーマのバリデーションテスト"""
    # 正常なデータ
    valid_data = {
        "id": "msg_123",
        "channel_id": "1",
        "user_id": "user_456",
        "user_name": "テストユーザー",
        "content": "テストメッセージ",
        "timestamp": datetime.now(),
        "is_own_message": True,
    }

    message = MessageCreate(**valid_data)
    assert message.id == "msg_123"
    assert message.channel_id == "1"
    assert message.content == "テストメッセージ"

    # 必須フィールドが不足している場合
    with pytest.raises(ValidationError):
        MessageCreate(  # type: ignore[call-arg]
            id="msg_123",
            channel_id="1",
            # user_idが不足
            user_name="テストユーザー",
            content="テストメッセージ",
            timestamp=datetime.now(),
            is_own_message=True,
        )


def test_message_response_schema():
    """MessageResponseスキーマのバリデーションテスト"""
    data = {
        "id": "msg_123",
        "channel_id": "1",
        "user_id": "user_456",
        "user_name": "テストユーザー",
        "content": "テストメッセージ",
        "timestamp": datetime.now(),
        "is_own_message": True,
        "created_at": datetime.now(),
    }

    response = MessageResponse(**data)
    assert response.id == "msg_123"
    assert isinstance(response.created_at, datetime)

    # model_dumpでcamelCase変換を確認
    dumped = response.model_dump(by_alias=True)
    assert "channelId" in dumped
    assert "userId" in dumped
    assert "isOwnMessage" in dumped
    assert "createdAt" in dumped


def test_channel_response_schema():
    """ChannelResponseスキーマのバリデーションテスト"""
    data = {"id": "1", "name": "雑談", "created_at": datetime.now()}

    response = ChannelResponse(**data)
    assert response.id == "1"
    assert response.name == "雑談"
    assert isinstance(response.created_at, datetime)

    # model_dumpでcamelCase変換を確認
    dumped = response.model_dump(by_alias=True)
    assert "createdAt" in dumped


def test_messages_list_response_schema():
    """MessagesListResponseスキーマのバリデーションテスト"""
    message_data = {
        "id": "msg_123",
        "channel_id": "1",
        "user_id": "user_456",
        "user_name": "テストユーザー",
        "content": "テストメッセージ",
        "timestamp": datetime.now(),
        "is_own_message": True,
        "created_at": datetime.now(),
    }

    response = MessagesListResponse(messages=[MessageResponse(**message_data)], total=1, has_more=False)

    assert len(response.messages) == 1
    assert response.total == 1
    assert response.has_more is False

    # model_dumpでcamelCase変換を確認
    dumped = response.model_dump(by_alias=True)
    assert "hasMore" in dumped
    assert dumped["hasMore"] is False
