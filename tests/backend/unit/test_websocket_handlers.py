import json
from unittest.mock import AsyncMock, Mock

import pytest

from src.backend.websocket import ConnectionManager


def test_connection_manager_initialization():
    """ConnectionManagerの初期化テスト"""
    manager = ConnectionManager()
    assert manager.active_connections == []
    assert isinstance(manager.active_connections, list)


@pytest.mark.asyncio
async def test_connection_manager_connect():
    """ConnectionManagerの接続テスト"""
    manager = ConnectionManager()

    # モックWebSocketを作成
    mock_websocket = Mock()
    mock_websocket.accept = AsyncMock()

    await manager.connect(mock_websocket)

    # acceptが呼ばれたことを確認
    mock_websocket.accept.assert_called_once()

    # active_connectionsに追加されたことを確認
    assert mock_websocket in manager.active_connections
    assert len(manager.active_connections) == 1


def test_connection_manager_disconnect():
    """ConnectionManagerの切断テスト"""
    manager = ConnectionManager()

    # モックWebSocketを作成して追加
    mock_websocket1 = Mock()
    mock_websocket2 = Mock()
    manager.active_connections = [mock_websocket1, mock_websocket2]

    # websocket1を切断
    manager.disconnect(mock_websocket1)

    # active_connectionsから削除されたことを確認
    assert mock_websocket1 not in manager.active_connections
    assert mock_websocket2 in manager.active_connections
    assert len(manager.active_connections) == 1


@pytest.mark.asyncio
async def test_connection_manager_send_personal_message():
    """個別メッセージ送信テスト"""
    manager = ConnectionManager()

    # モックWebSocketを作成
    mock_websocket = Mock()
    mock_websocket.send_text = AsyncMock()

    test_message = {"type": "test", "data": "hello"}
    await manager.send_personal_message(json.dumps(test_message), mock_websocket)

    # send_textが正しいメッセージで呼ばれたことを確認
    mock_websocket.send_text.assert_called_once_with(json.dumps(test_message))


@pytest.mark.asyncio
async def test_connection_manager_broadcast():
    """ブロードキャストテスト"""
    manager = ConnectionManager()

    # 複数のモックWebSocketを作成
    mock_websocket1 = Mock()
    mock_websocket1.send_text = AsyncMock()
    mock_websocket2 = Mock()
    mock_websocket2.send_text = AsyncMock()

    manager.active_connections = [mock_websocket1, mock_websocket2]

    test_message = {"type": "broadcast", "data": "hello everyone"}
    await manager.broadcast(json.dumps(test_message))

    # 両方のWebSocketにメッセージが送信されたことを確認
    mock_websocket1.send_text.assert_called_once_with(json.dumps(test_message))
    mock_websocket2.send_text.assert_called_once_with(json.dumps(test_message))


@pytest.mark.asyncio
async def test_connection_manager_broadcast_with_error():
    """ブロードキャスト中のエラーハンドリングテスト"""
    manager = ConnectionManager()

    # 正常なWebSocketとエラーを起こすWebSocketを作成
    mock_websocket1 = Mock()
    mock_websocket1.send_text = AsyncMock()

    mock_websocket2 = Mock()
    mock_websocket2.send_text = AsyncMock(side_effect=Exception("Connection closed"))

    manager.active_connections = [mock_websocket1, mock_websocket2]

    test_message = {"type": "broadcast", "data": "test"}

    # エラーが発生してもブロードキャストは継続される
    await manager.broadcast(json.dumps(test_message))

    # 正常なWebSocketにはメッセージが送信される
    mock_websocket1.send_text.assert_called_once()
