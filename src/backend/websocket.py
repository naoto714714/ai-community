import json
import logging
from typing import Any, TypedDict

from fastapi import WebSocket

import crud
from schemas import MessageCreate


class WebSocketMessageData(TypedDict):
    """WebSocketメッセージのdata部分の型定義"""

    id: str
    channel_id: str
    user_id: str
    user_name: str
    content: str
    timestamp: str
    is_own_message: bool


class WebSocketMessage(TypedDict):
    """WebSocketメッセージの型定義"""

    type: str
    data: WebSocketMessageData | None


logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception:
            # 接続が切断されている場合は削除
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        connections_to_remove = []
        for connection in self.active_connections.copy():  # リストのコピーを作成して安全にイテレート
            try:
                # WebSocket接続状態を厳密にチェック
                if connection.client_state.name == "DISCONNECTED":
                    connections_to_remove.append(connection)
                    continue
                await connection.send_text(message)
            except Exception:
                connections_to_remove.append(connection)

        # 切断された接続を削除
        for conn in connections_to_remove:
            self.disconnect(conn)


manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """ConnectionManagerのインスタンスを取得（テスト用）"""
    return manager


async def handle_websocket_message(websocket: WebSocket, data: dict[str, Any]):
    """WebSocketメッセージの処理"""
    message_type = data.get("type")
    message_data = data.get("data")

    if message_type == "message:send":
        # データベースセッションをコンテキストマネージャーで安全に管理
        from database import SessionLocal

        async def save_message_with_session():
            db = SessionLocal()
            try:
                message_create = MessageCreate.model_validate(message_data)
                saved_message = crud.create_message(db, message_create)
                return saved_message
            finally:
                db.close()

        try:
            saved_message = await save_message_with_session()

            # 保存成功をクライアントに通知
            response = {"type": "message:saved", "data": {"id": saved_message.id, "success": True}}
            await manager.send_personal_message(json.dumps(response), websocket)

            logger.info(f"Message saved: {saved_message.id}")

        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")

            # エラーをクライアントに通知（情報漏洩対策済み）
            error_response = {
                "type": "message:error",
                "data": {
                    "id": message_data.get("id") if message_data else None,
                    "success": False,
                    "error": "Failed to save message",  # 詳細なエラー情報を隠蔽
                },
            }
            await manager.send_personal_message(json.dumps(error_response), websocket)

    else:
        logger.warning(f"Unknown message type: {message_type}")
