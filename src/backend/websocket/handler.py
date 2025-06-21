"""WebSocketメッセージハンドリング"""

import json
import logging
import os
import traceback
from typing import Any, NotRequired, Required, TypedDict

from fastapi import WebSocket
from pydantic import ValidationError
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketState

from .. import crud
from ..ai.message_handlers import handle_ai_response
from ..schemas import MessageCreate
from ..utils.session_manager import save_message_with_session_management
from .manager import manager


class MessageTypes:
    SEND = "message:send"
    # 将来的に追加される予定
    # EDIT = "message:edit"
    # DELETE = "message:delete"


# サポートされているメッセージタイプ
SUPPORTED_MESSAGE_TYPES = {
    MessageTypes.SEND,
}

# メッセージ長制限
MAX_MESSAGE_LENGTH = 10000

logger = logging.getLogger(__name__)


def is_production() -> bool:
    """本番環境かどうかを判定"""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def validate_message_data(message_data: dict[str, Any]) -> tuple[bool, str | None]:
    """メッセージデータの詳細バリデーション"""
    required_fields = {
        "id": str,
        "channel_id": str,
        "user_id": str,
        "user_name": str,
        "content": str,
        "timestamp": str,
        "is_own_message": bool,
    }

    for field_name, field_type in required_fields.items():
        if field_name not in message_data:
            return False, f"必須フィールド '{field_name}' が不足しています"

        value = message_data[field_name]
        if not isinstance(value, field_type):
            return False, f"フィールド '{field_name}' の型が正しくありません（期待値: {field_type.__name__}）"

    # 追加的なバリデーション
    if not message_data["content"].strip():
        return False, "メッセージ内容は空にできません"

    if len(message_data["content"]) > MAX_MESSAGE_LENGTH:
        return False, "メッセージが長すぎます"

    return True, None


class WebSocketMessage(TypedDict):
    type: Required[str]
    data: NotRequired[dict[str, Any]]


def is_websocket_connected(websocket: WebSocket) -> bool:
    """WebSocket接続が有効かどうかをチェック"""
    try:
        # より堅牢な接続状態チェック
        return websocket.client_state == WebSocketState.CONNECTED
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

    if message_type == MessageTypes.SEND:
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

        # 詳細なメッセージデータバリデーション
        is_valid, validation_error = validate_message_data(message_data)
        if not is_valid:
            error_response = {
                "type": "message:error",
                "data": {
                    "id": message_data.get("id"),
                    "success": False,
                    "error": f"メッセージデータが無効です: {validation_error}",
                },
            }
            await safe_send_message(websocket, json.dumps(error_response))
            return

        try:
            # Pydanticバリデーション
            message_create = MessageCreate.model_validate(message_data)
            saved_message = save_message_with_session_management(
                lambda session: crud.create_message(session, message_create), db_session
            )

            # 保存成功をクライアントに通知
            response = {"type": "message:saved", "data": {"id": saved_message.id, "success": True}}
            await safe_send_message(websocket, json.dumps(response))

            logger.info(f"メッセージが保存されました: {saved_message.id}")

            # 送信者以外の全クライアントにブロードキャスト（送信者は楽観的更新済み）
            broadcast_data = {
                "id": saved_message.id,
                "channel_id": saved_message.channel_id,
                "user_id": saved_message.user_id,
                "user_name": saved_message.user_name,
                "content": saved_message.content,
                "timestamp": saved_message.timestamp.isoformat(),
                "is_own_message": False,  # 他のクライアントにとっては他人のメッセージ
            }

            user_broadcast_message = {
                "type": "message:broadcast",
                "data": broadcast_data,
            }
            await manager.broadcast(json.dumps(user_broadcast_message), exclude_websocket=websocket)
            logger.info(f"ユーザーメッセージをブロードキャスト（送信者除く）: {saved_message.id}")

            # AI応答の処理（エラーハンドリング付き）
            try:
                await handle_ai_response(message_data, db_session)
            except Exception as ai_error:
                logger.warning(f"AI応答処理エラー: {str(ai_error)}")
                logger.debug(f"AI応答エラーの詳細: {traceback.format_exc()}")
                # ユーザーにAI応答エラーを通知
                ai_error_response = {
                    "type": "ai:error",
                    "data": {"message": "AI応答の生成に失敗しました。しばらく時間をおいてから再度お試しください。"},
                }
                await safe_send_message(websocket, json.dumps(ai_error_response))
                # AI応答エラーはユーザーメッセージ保存に影響しないため継続

        except ValidationError as ve:
            logger.warning(f"Pydanticバリデーションエラー: {str(ve)}")
            # 本番環境では詳細なバリデーションエラーをログに出力しない
            if not is_production():
                logger.debug(f"バリデーション詳細: {ve.errors()}")

            error_response = {
                "type": "message:error",
                "data": {
                    "id": message_data.get("id") if message_data else None,
                    "success": False,
                    "error": "メッセージフォーマットが正しくありません",
                },
            }
            await safe_send_message(websocket, json.dumps(error_response))

        except Exception as e:
            # 本番環境では詳細なエラー情報をログに出力しない
            if is_production():
                logger.error("メッセージ保存処理でエラーが発生しました")
            else:
                logger.error(f"メッセージ保存エラー: {str(e)}")
                logger.error(f"詳細なエラー情報: {traceback.format_exc()}")

            # エラーをクライアントに通知（情報漏洩対策済み）
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
        logger.warning(f"未サポートのメッセージタイプ: {message_type}. サポートタイプ: {SUPPORTED_MESSAGE_TYPES}")
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
