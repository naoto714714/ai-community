"""WebSocketメッセージハンドリング"""

import json
import logging
import traceback
from typing import Any, NotRequired, Required, TypedDict

from fastapi import WebSocket
from sqlalchemy.orm import Session

from ..ai.message_handlers import handle_ai_response
from ..utils.session_manager import save_message_with_session_management
from .manager import manager

try:
    from .. import crud
    from ..schemas import MessageCreate
except ImportError:
    import crud
    from schemas import MessageCreate

logger = logging.getLogger(__name__)


class WebSocketMessage(TypedDict):
    type: Required[str]
    data: NotRequired[dict[str, Any]]


def is_websocket_connected(websocket: WebSocket) -> bool:
    """WebSocket接続が有効かどうかをチェック"""
    try:
        # client_stateの名前がCONNECTEDかどうかをチェック
        return websocket.client_state.name == "CONNECTED"
    except Exception:
        return False


async def safe_send_message(websocket: WebSocket, message: str) -> bool:
    """WebSocket接続が有効な場合のみメッセージを送信"""
    if not is_websocket_connected(websocket):
        logger.warning("WebSocket接続が切断されているため、メッセージ送信をスキップ")
        return False

    try:
        await manager.send_personal_message(message, websocket)
        return True
    except Exception as e:
        logger.error(f"WebSocketメッセージ送信エラー: {str(e)}")
        return False


async def handle_websocket_message(
    websocket: WebSocket,
    data: WebSocketMessage,
    db_session: Session | None = None,
):
    """WebSocketメッセージの処理"""
    message_type = data.get("type")
    message_data = data.get("data")

    if message_type == "message:send":
        # メッセージデータの存在を検証
        if not message_data or not isinstance(message_data, dict):
            error_response = {
                "type": "message:error",
                "data": {
                    "id": None,
                    "success": False,
                    "error": "無効なメッセージデータです",
                },
            }
            await safe_send_message(websocket, json.dumps(error_response))
            return

        try:
            # 共通のセッション管理ヘルパーを使用
            message_create = MessageCreate.model_validate(message_data)
            saved_message = save_message_with_session_management(
                lambda session: crud.create_message(session, message_create), db_session
            )

            # 保存成功をクライアントに通知
            response = {"type": "message:saved", "data": {"id": saved_message.id, "success": True}}
            await safe_send_message(websocket, json.dumps(response))

            logger.info(f"メッセージが保存されました: {saved_message.id}")

            # 送信者以外の全クライアントにブロードキャスト（送信者は楽観的更新済み）
            user_broadcast_message = {
                "type": "message:broadcast",
                "data": {
                    "id": saved_message.id,
                    "channel_id": saved_message.channel_id,
                    "user_id": saved_message.user_id,
                    "user_name": saved_message.user_name,
                    "content": saved_message.content,
                    "timestamp": saved_message.timestamp.isoformat(),
                    "is_own_message": False,  # 他のクライアントにとっては他人のメッセージ
                },
            }
            await manager.broadcast(json.dumps(user_broadcast_message), exclude_websocket=websocket)
            logger.info(f"ユーザーメッセージをブロードキャスト（送信者除く）: {saved_message.id}")

            # AI応答の処理（エラーハンドリング付き）
            try:
                await handle_ai_response(message_data, db_session)
            except Exception as ai_error:
                logger.error(f"AI応答処理エラー: {str(ai_error)}")
                # AI応答エラーはユーザーメッセージ保存に影響しないため継続

        except Exception as e:
            logger.error(f"メッセージ保存エラー: {str(e)}")
            # デバッグのため詳細なエラー情報もログに出力
            logger.error(f"詳細なエラー情報: {traceback.format_exc()}")

            # エラーをクライアントに通知（情報漏洩対策済み）
            # メッセージIDを安全に取得（None値の場合も考慮）
            message_id = None
            if message_data and isinstance(message_data, dict):
                message_id = message_data.get("id")

            error_response = {
                "type": "message:error",
                "data": {
                    "id": message_id,
                    "success": False,
                    "error": "メッセージの保存に失敗しました",  # 詳細なエラー情報を隠蔽
                },
            }
            await safe_send_message(websocket, json.dumps(error_response))

    else:
        logger.warning(f"未知のメッセージタイプ: {message_type}")
        # 未対応メッセージタイプをクライアントに通知
        error_response = {
            "type": "message:error",
            "data": {
                "id": None,
                "success": False,
                "error": f"サポートされていないメッセージタイプです: {message_type}",
            },
        }
        await safe_send_message(websocket, json.dumps(error_response))
