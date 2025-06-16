import json
import logging

from fastapi import WebSocket

import crud
from database import SessionLocal
from schemas import MessageCreate

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
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                # 接続が切れている場合は削除
                self.disconnect(connection)


manager = ConnectionManager()


async def handle_websocket_message(websocket: WebSocket, data: dict):
    """WebSocketメッセージの処理"""
    message_type = data.get("type")
    message_data = data.get("data")

    if message_type == "message:send":
        # データベースにメッセージを保存
        db = SessionLocal()
        try:
            message_create = MessageCreate.model_validate(message_data)
            saved_message = crud.create_message(db, message_create)

            # 保存成功をクライアントに通知
            response = {"type": "message:saved", "data": {"id": saved_message.id, "success": True}}
            await manager.send_personal_message(json.dumps(response), websocket)

            logger.info(f"Message saved: {saved_message.id}")

        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")

            # エラーをクライアントに通知
            error_response = {
                "type": "message:error",
                "data": {"id": message_data.get("id") if message_data else None, "success": False, "error": str(e)},
            }
            await manager.send_personal_message(json.dumps(error_response), websocket)

        finally:
            db.close()

    else:
        logger.warning(f"Unknown message type: {message_type}")
