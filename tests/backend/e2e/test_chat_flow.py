import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.backend.main import app


@pytest.mark.asyncio
async def test_complete_chat_flow(async_client: AsyncClient, client: TestClient, seed_channels):
    """完全なチャットフローのE2Eテスト"""
    # 1. チャンネル一覧を取得
    response = await async_client.get("/api/channels")
    assert response.status_code == 200
    channels = response.json()
    assert len(channels) >= 1
    channel_id = channels[0]["id"]

    # 2. WebSocket接続を確立
    with client.websocket_connect("/ws") as websocket:
        # 3. メッセージを送信
        message_data = {
            "type": "message:send",
            "data": {
                "id": "e2e_test_msg",
                "channel_id": str(channel_id),
                "user_id": "e2e_user",
                "user_name": "E2Eテストユーザー",
                "content": "E2Eテストメッセージ",
                "timestamp": "2025-01-16T10:00:00.000Z",
                "is_own_message": True,
            },
        }

        websocket.send_json(message_data)

        # 4. 保存確認を受信
        saved_response = websocket.receive_json()
        assert saved_response["type"] == "message:saved"
        assert saved_response["data"]["success"] is True
        assert saved_response["data"]["id"] == "e2e_test_msg"

    # 5. メッセージ履歴を確認
    response = await async_client.get(f"/api/channels/{channel_id}/messages")
    assert response.status_code == 200
    messages = response.json()["messages"]

    # 送信したメッセージが含まれていることを確認
    assert any(msg["content"] == "E2Eテストメッセージ" for msg in messages)
    assert any(msg["id"] == "e2e_test_msg" for msg in messages)


@pytest.mark.asyncio
async def test_multiple_channels_flow(async_client: AsyncClient, client: TestClient, seed_channels):
    """複数チャンネルでのフローテスト"""
    # チャンネル一覧を取得
    response = await async_client.get("/api/channels")
    channels = response.json()
    assert len(channels) >= 2

    channel1_id = channels[0]["id"]
    channel2_id = channels[1]["id"]

    with client.websocket_connect("/ws") as websocket:
        # チャンネル1にメッセージ送信
        message1 = {
            "type": "message:send",
            "data": {
                "id": "multi_ch_msg_1",
                "channel_id": channel1_id,
                "user_id": "multi_user",
                "user_name": "マルチチャンネルユーザー",
                "content": "チャンネル1のメッセージ",
                "timestamp": "2025-01-16T10:00:00.000Z",
                "is_own_message": True,
            },
        }

        websocket.send_json(message1)
        response1 = websocket.receive_json()
        assert response1["type"] == "message:saved"

        # チャンネル2にメッセージ送信
        message2 = {
            "type": "message:send",
            "data": {
                "id": "multi_ch_msg_2",
                "channel_id": channel2_id,
                "user_id": "multi_user",
                "user_name": "マルチチャンネルユーザー",
                "content": "チャンネル2のメッセージ",
                "timestamp": "2025-01-16T10:00:00.000Z",
                "is_own_message": True,
            },
        }

        websocket.send_json(message2)
        response2 = websocket.receive_json()
        assert response2["type"] == "message:saved"

    # 各チャンネルのメッセージを確認
    ch1_response = await async_client.get(f"/api/channels/{channel1_id}/messages")
    ch1_messages = ch1_response.json()["messages"]
    assert any(msg["content"] == "チャンネル1のメッセージ" for msg in ch1_messages)

    ch2_response = await async_client.get(f"/api/channels/{channel2_id}/messages")
    ch2_messages = ch2_response.json()["messages"]
    assert any(msg["content"] == "チャンネル2のメッセージ" for msg in ch2_messages)


@pytest.mark.asyncio
async def test_error_handling_flow(async_client: AsyncClient, client: TestClient):
    """エラーハンドリングのE2Eテスト"""
    # 1. 存在しないチャンネルへのAPI呼び出し
    response = await async_client.get("/api/channels/999/messages")
    assert response.status_code == 404

    # 2. 無効なメッセージをWebSocketで送信
    with client.websocket_connect("/ws") as websocket:
        invalid_message = {
            "type": "message:send",
            "data": {
                "content": "不完全なメッセージ"
                # 必須フィールドが不足
            },
        }

        websocket.send_json(invalid_message)

        # エラーレスポンスを受信
        error_response = websocket.receive_json()
        assert error_response["type"] == "message:error"
        assert error_response["data"]["success"] is False

        # その後の正常なメッセージは処理される
        valid_message = {
            "type": "message:send",
            "data": {
                "id": "recovery_test_msg",
                "channel_id": "1",
                "user_id": "recovery_user",
                "user_name": "回復テストユーザー",
                "content": "回復テスト",
                "timestamp": "2025-01-16T10:00:00.000Z",
                "is_own_message": True,
            },
        }

        websocket.send_json(valid_message)
        valid_response = websocket.receive_json()
        assert valid_response["type"] == "message:saved"


@pytest.mark.asyncio
async def test_concurrent_users_flow(async_client: AsyncClient):
    """複数ユーザーの並行利用テスト"""
    from fastapi.testclient import TestClient

    client1 = TestClient(app)
    client2 = TestClient(app)

    with client1.websocket_connect("/ws") as ws1:
        with client2.websocket_connect("/ws") as ws2:
            # ユーザー1がメッセージ送信
            message1 = {
                "type": "message:send",
                "data": {
                    "id": "concurrent_msg_1",
                    "channel_id": "1",
                    "user_id": "user1",
                    "user_name": "ユーザー1",
                    "content": "並行テスト1",
                    "timestamp": "2025-01-16T10:00:00.000Z",
                    "is_own_message": True,
                },
            }

            ws1.send_json(message1)

            # ユーザー1で保存確認を受信
            saved1 = ws1.receive_json()
            assert saved1["type"] == "message:saved"

            # ユーザー2がメッセージ送信
            message2 = {
                "type": "message:send",
                "data": {
                    "id": "concurrent_msg_2",
                    "channel_id": "1",
                    "user_id": "user2",
                    "user_name": "ユーザー2",
                    "content": "並行テスト2",
                    "timestamp": "2025-01-16T10:00:00.000Z",
                    "is_own_message": True,
                },
            }

            ws2.send_json(message2)

            # ユーザー2で保存確認を受信
            saved2 = ws2.receive_json()
            assert saved2["type"] == "message:saved"

    # 両方のメッセージがデータベースに保存されていることを確認
    response = await async_client.get("/api/channels/1/messages")
    messages = response.json()["messages"]

    contents = [msg["content"] for msg in messages]
    assert "並行テスト1" in contents
    assert "並行テスト2" in contents


