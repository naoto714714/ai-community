"""API基本テスト（最小限・実用版）"""

from datetime import datetime

import pytest
from httpx import AsyncClient

from src.backend.models import Message


@pytest.mark.asyncio
async def test_get_channels(async_client: AsyncClient, seed_channels):
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
async def test_get_messages(async_client: AsyncClient, seed_channels, test_db):
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
            timestamp=datetime.now(),
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

    # メッセージ形式を確認
    first_message = data["messages"][0]
    assert "id" in first_message
    assert "channelId" in first_message
    assert "userId" in first_message
    assert "userName" in first_message
    assert "content" in first_message
    assert "timestamp" in first_message
    assert "isOwnMessage" in first_message
    assert "createdAt" in first_message


@pytest.mark.asyncio
async def test_invalid_channel(async_client: AsyncClient):
    """存在しないチャンネルのエラーハンドリングテスト"""
    response = await async_client.get("/api/channels/999/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == "Channel not found"
