import pytest
from httpx import AsyncClient


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

    # データ形式を確認
    first_channel = data[0]
    assert first_channel["id"] == "1"
    assert first_channel["name"] == "雑談"
    assert "createdAt" in first_channel  # camelCaseで返されることを確認


@pytest.mark.asyncio
async def test_get_channels_empty_database(async_client: AsyncClient, test_db):
    """チャンネルが存在しない場合のテスト"""
    # seed_channelsを使わずに空のデータベースでテスト
    response = await async_client.get("/api/channels")

    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """ルートエンドポイントのテスト"""
    response = await async_client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "AI Community Backend API"}
