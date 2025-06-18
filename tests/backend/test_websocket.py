"""WebSocket基本テスト（最小限・実用版）"""

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_websocket_connection(client: TestClient):
    """WebSocket接続の基本テスト"""
    with client.websocket_connect("/ws") as websocket:
        # 接続成功を確認（接続時のメッセージは現在の実装では送信されない）
        # 接続が確立されたことだけを確認
        assert websocket is not None


def test_websocket_message_send(client: TestClient, seed_channels, test_db):
    """WebSocketメッセージ送信テスト"""
    # WebSocketハンドラーでテスト用データベースセッションを使用するようにパッチ
    from src.backend.websocket import handle_websocket_message

    async def mock_handle_websocket_message(websocket, data):
        return await handle_websocket_message(websocket, data, db_session=test_db)

    with patch("src.backend.main.handle_websocket_message", side_effect=mock_handle_websocket_message):
        with client.websocket_connect("/ws") as websocket:
            # メッセージを送信
            test_message = {
                "type": "message:send",
                "data": {
                    "id": "ws_test_msg_1",
                    "channel_id": "1",
                    "user_id": "test_user",
                    "user_name": "テストユーザー",
                    "content": "WebSocketテスト",
                    "timestamp": "2025-01-16T10:00:00.000Z",
                    "is_own_message": True,
                },
            }

            websocket.send_json(test_message)

            # 保存成功メッセージを受信
            response = websocket.receive_json()
            assert response["type"] == "message:saved"
            assert response["data"]["success"] is True
            assert response["data"]["id"] == "ws_test_msg_1"
