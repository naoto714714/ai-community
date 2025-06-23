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

try:
    # パッケージとして実行される場合
    from .. import crud
    from ..ai.message_handlers import handle_ai_response
    from ..schemas import MessageCreate
    from ..utils.session_manager import save_message_with_session_management
    from .manager import manager
except ImportError:
    # 直接実行される場合
    import crud
    from ai.message_handlers import handle_ai_response
    from schemas import MessageCreate
    from utils.session_manager import save_message_with_session_management
    from websocket.manager import manager


class MessageTypes:
    """サポートされるWebSocketメッセージタイプの定数クラス."""

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
    content = message_data["content"]
    if not content.strip():
        return False, "メッセージ内容は空にできません"

    if len(content) > MAX_MESSAGE_LENGTH:
        return False, "メッセージが長すぎます"

    return True, None


class WebSocketMessage(TypedDict):
    """クライアントから受信するWebSocketメッセージの型定義."""

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
        logger.error(f"WebSocketメッセージ送信エラー: {e!s}")
        return False


async def _send_error_response(websocket: WebSocket, message_id: str | None, error_message: str) -> None:
    """エラーレスポンスをクライアントに送信する共通処理."""
    error_response = {
        "type": "message:error",
        "data": {
            "id": message_id,
            "success": False,
            "error": error_message,
        },
    }
    await safe_send_message(websocket, json.dumps(error_response))


async def _validate_and_parse_message(message_data: dict[str, Any]) -> tuple[MessageCreate | None, str | None]:
    """メッセージデータのバリデーションとパース処理."""
    # 詳細なメッセージデータバリデーション
    is_valid, validation_error = validate_message_data(message_data)
    if not is_valid:
        return None, f"メッセージデータが無効です: {validation_error}"

    try:
        # Pydanticバリデーション
        message_create = MessageCreate.model_validate(message_data)
        return message_create, None
    except ValidationError as ve:
        logger.warning(f"Pydanticバリデーションエラー: {ve!s}")
        if not is_production():
            logger.debug(f"バリデーション詳細: {ve.errors()}")
        return None, "メッセージフォーマットが正しくありません"


async def _save_and_notify_success(
    websocket: WebSocket,
    message_create: MessageCreate,
    db_session: Session | None,
) -> None:
    """メッセージ保存と成功通知処理."""
    save_message_with_session_management(
        lambda session: crud.create_message(session, message_create),
        db_session,
        auto_commit=(db_session is None),
    )

    # 保存成功をクライアントに通知
    response = {"type": "message:saved", "data": {"id": message_create.id, "success": True}}
    await safe_send_message(websocket, json.dumps(response))
    logger.info(f"メッセージが保存されました: {message_create.id}")


async def _broadcast_message_to_others(websocket: WebSocket, message_create: MessageCreate) -> None:
    """送信者以外の全クライアントにメッセージをブロードキャスト."""
    broadcast_data = {
        "id": message_create.id,
        "channel_id": message_create.channel_id,
        "user_id": message_create.user_id,
        "user_name": message_create.user_name,
        "content": message_create.content,
        "timestamp": message_create.timestamp.isoformat(),
        "is_own_message": False,  # 他のクライアントにとっては他人のメッセージ
    }

    user_broadcast_message = {
        "type": "message:broadcast",
        "data": broadcast_data,
    }
    await manager.broadcast(json.dumps(user_broadcast_message), exclude_websocket=websocket)
    logger.info(f"ユーザーメッセージをブロードキャスト（送信者除く）: {message_create.id}")


async def _handle_ai_response_safely(
    websocket: WebSocket,
    message_data: dict[str, Any],
    db_session: Session | None,
) -> None:
    """AI応答処理（エラーハンドリング付き）."""
    try:
        await handle_ai_response(message_data, db_session)
    except Exception as ai_error:
        logger.warning(f"AI応答処理エラー: {ai_error!s}")
        logger.debug(f"AI応答エラーの詳細: {traceback.format_exc()}")
        # ユーザーにAI応答エラーを通知
        ai_error_response = {
            "type": "ai:error",
            "data": {"message": "AI応答の生成に失敗しました。しばらく時間をおいてから再度お試しください。"},
        }
        await safe_send_message(websocket, json.dumps(ai_error_response))
        # AI応答エラーはユーザーメッセージ保存に影響しないため継続


async def _handle_message_send(
    websocket: WebSocket,
    message_data: dict[str, Any] | None,
    db_session: Session | None,
) -> None:
    """メッセージ送信処理の実装."""
    # メッセージデータの存在を検証
    if not message_data or not isinstance(message_data, dict):
        await _send_error_response(websocket, None, "無効なメッセージデータです")
        return

    # バリデーションとパース
    message_create, error_message = await _validate_and_parse_message(message_data)
    if error_message or message_create is None:
        await _send_error_response(websocket, message_data.get("id"), error_message or "メッセージの解析に失敗しました")
        return

    try:
        # メッセージ保存と成功通知
        await _save_and_notify_success(websocket, message_create, db_session)

        # 他のクライアントにブロードキャスト
        await _broadcast_message_to_others(websocket, message_create)

        # AI応答処理
        await _handle_ai_response_safely(websocket, message_data, db_session)

    except Exception as e:
        # 本番環境では詳細なエラー情報をログに出力しない
        if is_production():
            logger.error("メッセージ保存処理でエラーが発生しました")
        else:
            logger.error(f"メッセージ保存エラー: {e!s}")
            logger.error(f"詳細なエラー情報: {traceback.format_exc()}")

        # エラーをクライアントに通知（情報漏洩対策済み）
        message_id = message_data.get("id") if message_data else None
        await _send_error_response(websocket, message_id, "メッセージの保存に失敗しました")


async def _handle_unsupported_message_type(websocket: WebSocket, message_type: str) -> None:
    """未サポートメッセージタイプの処理."""
    logger.warning(f"未サポートのメッセージタイプ: {message_type}. サポートタイプ: {SUPPORTED_MESSAGE_TYPES}")
    await _send_error_response(websocket, None, f"サポートされていないメッセージタイプです: {message_type}")


async def handle_websocket_message(
    websocket: WebSocket,
    data: WebSocketMessage,
    db_session: Session | None = None,
) -> None:
    """WebSocketメッセージの処理.

    Args:
        websocket: WebSocket接続オブジェクト
        data: クライアントから受信したメッセージデータ
        db_session: データベースセッション（オプション）
    """
    message_type = data.get("type")
    message_data = data.get("data")

    if message_type == MessageTypes.SEND:
        await _handle_message_send(websocket, message_data, db_session)
    else:
        await _handle_unsupported_message_type(websocket, message_type)
