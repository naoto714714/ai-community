"""API基本テスト（最小限・実用版）"""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest
from httpx import AsyncClient

from src.backend.models import Message

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from src.backend.models import Channel


@pytest.mark.asyncio
async def test_get_channels(async_client: AsyncClient, seed_channels: list["Channel"]) -> None:
    """チャンネル一覧取得APIのテスト"""
    response = await async_client.get("/api/channels")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 5
    assert all("id" in channel and "name" in channel and "createdAt" in channel for channel in data)

    # チャンネル名を確認
    channel_names = [ch["name"] for ch in data]
    assert "雑談" in channel_names
    assert "ゲーム" in channel_names
    assert "音楽" in channel_names
    assert "趣味" in channel_names
    assert "ニュース" in channel_names


@pytest.mark.asyncio
async def test_get_messages(async_client: AsyncClient, seed_channels: list["Channel"], test_db: "Session") -> None:
    """メッセージ履歴取得APIのテスト"""
    # テストメッセージを作成
    channel = seed_channels[0]
    for i in range(3):
        message = Message(
            id=f"api_test_msg_{i}",
            channel_id=channel.id,
            user_id=f"user_{i}",
            user_name=f"ユーザー{i}",
            content=f"テストメッセージ{i}",
            timestamp=datetime.now(UTC),
            is_own_message=i % 2 == 0,
        )
        test_db.add(message)
    test_db.commit()

    response = await async_client.get(f"/api/channels/{channel.id}/messages")
    assert response.status_code == 200
    data = response.json()

    assert "messages" in data
    assert "total" in data
    assert "hasMore" in data
    assert data["total"] == 3
    assert len(data["messages"]) == 3
    assert data["hasMore"] is False

    # メッセージ形式を確認（順序に依存しない検証）
    assert len(data["messages"]) > 0
    # 全メッセージが正しい形式を持つことを確認
    for message in data["messages"]:
        assert "id" in message
        assert "channelId" in message
        assert "userId" in message
        assert "userName" in message
        assert "content" in message
        assert "timestamp" in message
        assert "isOwnMessage" in message
        assert "createdAt" in message

    # 特定のメッセージが存在することを確認（順序に依存しない）
    message_ids = [msg["id"] for msg in data["messages"]]
    assert "api_test_msg_0" in message_ids
    assert "api_test_msg_1" in message_ids
    assert "api_test_msg_2" in message_ids


@pytest.mark.asyncio
async def test_invalid_channel(async_client: AsyncClient) -> None:
    """存在しないチャンネルのエラーハンドリングテスト"""
    response = await async_client.get("/api/channels/999/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == "チャンネルが見つかりません"
