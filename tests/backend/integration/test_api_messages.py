from datetime import datetime

import pytest
from httpx import AsyncClient

from src.backend.models import Message


@pytest.mark.asyncio
async def test_get_channel_messages(async_client: AsyncClient, seed_channels, test_db):
    """チャンネルメッセージ取得APIのテスト"""

    # テストメッセージを作成
    channel = seed_channels[0]
    for i in range(15):
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

    # ページネーションなし
    response = await async_client.get(f"/api/channels/{channel.id}/messages")
    assert response.status_code == 200
    data = response.json()

    assert "messages" in data
    assert "total" in data
    assert "hasMore" in data  # camelCase
    assert data["total"] == 15
    assert len(data["messages"]) == 15
    assert data["hasMore"] is False

    # 各メッセージの形式を確認
    first_message = data["messages"][0]
    assert "id" in first_message
    assert "channelId" in first_message  # camelCase
    assert "userId" in first_message  # camelCase
    assert "userName" in first_message  # camelCase
    assert "content" in first_message
    assert "timestamp" in first_message
    assert "isOwnMessage" in first_message  # camelCase
    assert "createdAt" in first_message  # camelCase


@pytest.mark.asyncio
async def test_get_channel_messages_with_pagination(async_client: AsyncClient, seed_channels, create_test_messages):
    """ページネーション付きメッセージ取得のテスト"""
    channel = seed_channels[0]
    create_test_messages(channel.id, 20)

    # limit=10, offset=5でテスト
    response = await async_client.get(f"/api/channels/{channel.id}/messages?limit=10&offset=5")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 20
    assert len(data["messages"]) == 10
    assert data["hasMore"] is True  # まだメッセージがある

    # offset=15, limit=10でテスト（残り5件）
    response = await async_client.get(f"/api/channels/{channel.id}/messages?limit=10&offset=15")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 20
    assert len(data["messages"]) == 5
    assert data["hasMore"] is False  # もうメッセージがない


@pytest.mark.asyncio
async def test_get_channel_messages_invalid_channel(async_client: AsyncClient):
    """存在しないチャンネルのメッセージ取得テスト"""
    response = await async_client.get("/api/channels/999/messages")

    assert response.status_code == 404
    assert response.json()["detail"] == "Channel not found"


@pytest.mark.asyncio
async def test_get_channel_messages_empty(async_client: AsyncClient, seed_channels):
    """メッセージが存在しないチャンネルのテスト"""
    channel = seed_channels[0]
    response = await async_client.get(f"/api/channels/{channel.id}/messages")

    assert response.status_code == 200
    data = response.json()

    assert data["messages"] == []
    assert data["total"] == 0
    assert data["hasMore"] is False


@pytest.mark.asyncio
async def test_get_channel_messages_limit_validation(async_client: AsyncClient, seed_channels):
    """limitパラメータのバリデーションテスト"""
    channel = seed_channels[0]

    # limit > 1000の場合
    response = await async_client.get(f"/api/channels/{channel.id}/messages?limit=1001")
    assert response.status_code == 422  # Validation Error

    # limit <= 0の場合
    response = await async_client.get(f"/api/channels/{channel.id}/messages?limit=0")
    assert response.status_code == 422  # Validation Error

    # offset < 0の場合
    response = await async_client.get(f"/api/channels/{channel.id}/messages?offset=-1")
    assert response.status_code == 422  # Validation Error


