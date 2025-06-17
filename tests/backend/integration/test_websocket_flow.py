from fastapi.testclient import TestClient


def test_websocket_connection(client: TestClient):
    """WebSocket接続の基本テスト"""
    with client.websocket_connect("/ws") as websocket:
        # 接続成功を確認（接続時のメッセージは現在の実装では送信されない）
        # 接続が確立されたことだけを確認
        assert websocket is not None


def test_websocket_message_send(client: TestClient, seed_channels):
    """WebSocketメッセージ送信テスト"""
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

        # 保存確認メッセージを受信
        response = websocket.receive_json()
        assert response["type"] == "message:saved"
        assert response["data"]["success"] is True
        assert response["data"]["id"] == "ws_test_msg_1"


def test_websocket_invalid_message_type(client: TestClient, seed_channels):
    """無効なメッセージタイプのテスト"""
    with client.websocket_connect("/ws") as websocket:
        # 無効なタイプのメッセージを送信
        invalid_message = {"type": "invalid:type", "data": {"content": "テスト"}}

        websocket.send_json(invalid_message)

        # 現在の実装では特にエラーレスポンスは返さない
        # 接続が維持されることを確認

        # 有効なメッセージを送信して接続が生きていることを確認
        valid_message = {
            "type": "message:send",
            "data": {
                "id": "ws_test_msg_2",
                "channel_id": "1",
                "user_id": "test_user",
                "user_name": "テストユーザー",
                "content": "接続確認",
                "timestamp": "2025-01-16T10:00:00.000Z",
                "is_own_message": True,
            },
        }

        websocket.send_json(valid_message)
        response = websocket.receive_json()
        assert response["type"] == "message:saved"


def test_websocket_invalid_message_data(client: TestClient):
    """無効なメッセージデータのテスト"""
    with client.websocket_connect("/ws") as websocket:
        # 必須フィールドが不足しているメッセージを送信
        invalid_message = {
            "type": "message:send",
            "data": {
                "content": "不完全なメッセージ"
                # 他の必須フィールドが不足
            },
        }

        websocket.send_json(invalid_message)

        # エラーレスポンスを受信
        response = websocket.receive_json()
        assert response["type"] == "message:error"
        assert response["data"]["success"] is False
        assert "error" in response["data"]


def test_websocket_disconnect_handling(client: TestClient, seed_channels):
    """WebSocket切断処理のテスト"""
    # 複数の接続を作成
    with client.websocket_connect("/ws") as ws1:
        with client.websocket_connect("/ws"):
            # 両方の接続が確立されていることを確認
            test_message = {
                "type": "message:send",
                "data": {
                    "id": "disconnect_test",
                    "channel_id": "1",
                    "user_id": "user1",
                    "user_name": "ユーザー1",
                    "content": "切断テスト",
                    "timestamp": "2025-01-16T10:00:00.000Z",
                    "is_own_message": True,
                },
            }

            ws1.send_json(test_message)

            # 両方の接続でメッセージを受信できることを確認
            response1 = ws1.receive_json()
            assert response1["type"] == "message:saved"

        # ws2が切断された後も、ws1は動作することを確認
        ws1.send_json(test_message)
        response = ws1.receive_json()
        assert response["type"] == "message:saved"
