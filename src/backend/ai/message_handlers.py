"""AI応答処理とメッセージハンドリング"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

try:
    # パッケージとして実行される場合
    from .. import crud
    from ..constants.timezone import JST
    from ..schemas import MessageBroadcastData, MessageCreate
    from ..utils.session_manager import save_message_with_session_management
    from ..websocket.manager import manager
    from .gemini_client import GeminiAPIClient, get_gemini_client
except ImportError:
    # 直接実行される場合
    import crud
    from ai.gemini_client import GeminiAPIClient, get_gemini_client
    from constants.timezone import JST
    from schemas import MessageBroadcastData, MessageCreate
    from utils.session_manager import save_message_with_session_management
    from websocket.manager import manager

logger = logging.getLogger(__name__)


def generate_ai_message_id(channel_id: str) -> str:
    """AI応答用のユニークIDを生成"""
    return f"ai_{channel_id}_{uuid.uuid4().hex[:8]}"


def generate_ai_error_message_id(channel_id: str) -> str:
    """AIエラー応答用のユニークIDを生成"""
    return f"ai_error_{channel_id}_{uuid.uuid4().hex[:8]}"


def create_ai_message_data(channel_id: str, content: str, personality) -> dict[str, Any]:
    """AI応答メッセージデータを作成"""
    return {
        "id": generate_ai_message_id(channel_id),
        "channel_id": channel_id,
        "user_id": personality.user_id,
        "user_name": personality.name,
        "user_type": "ai",
        "content": content,
        "timestamp": datetime.now(JST).isoformat(),
        "is_own_message": False,
    }


def create_broadcast_message(message_data: MessageBroadcastData) -> dict[str, Any]:
    """ブロードキャスト用メッセージを作成"""
    return {
        "type": "message:broadcast",
        "data": {
            "id": message_data.message_id,
            "channel_id": message_data.channel_id,
            "user_id": message_data.user_id,
            "user_name": message_data.user_name,
            "user_type": message_data.user_type,
            "content": message_data.content,
            "timestamp": message_data.timestamp.isoformat(),
            "is_own_message": False,
        },
    }


def _extract_message_attributes(ai_message_create: MessageCreate) -> tuple[str, str, str, str, str, datetime]:
    """メッセージ属性を抽出"""
    return (
        ai_message_create.id,
        ai_message_create.user_id,
        ai_message_create.user_name,
        ai_message_create.user_type,
        ai_message_create.content,
        ai_message_create.timestamp,
    )


async def _generate_ai_response(
    user_message: str, channel_id: str, db_session: Session | None = None
) -> tuple[MessageCreate, float]:
    """AI応答を生成し、タイミング情報を返す"""
    generation_start = time.time()
    gemini_client = get_gemini_client()

    # 連続発言防止：最新メッセージがAIの場合は、そのuser_idを除外対象とする
    exclude_user_id = None
    if db_session:
        try:
            recent_messages = crud.get_recent_channel_messages(db_session, channel_id, limit=1)
            if recent_messages:
                latest_msg = recent_messages[-1]  # 最新メッセージを取得
                logger.debug(
                    f"@AI応答 - 最新メッセージ詳細: user_name={latest_msg.user_name}, user_id={latest_msg.user_id}, user_type={latest_msg.user_type}"
                )

                if latest_msg.user_type == "ai":
                    exclude_user_id = latest_msg.user_id
                    logger.info(
                        f"@AI応答での連続発言防止: 前回AI発言者を除外 user_id={exclude_user_id}, user_name={latest_msg.user_name}"
                    )
                else:
                    logger.debug(
                        f"@AI応答 - 前回発言者はユーザー: {latest_msg.user_name} (user_type={latest_msg.user_type})"
                    )
        except Exception as e:
            logger.warning(f"連続発言防止チェック時のエラー: {str(e)}")

    ai_response, personality = await gemini_client.generate_response(
        user_message, channel_id=channel_id, db_session=db_session, max_retries=3, exclude_user_id=exclude_user_id
    )
    generation_time = time.time() - generation_start
    logger.info(
        f"AI応答生成完了: generation_time={generation_time:.2f}s, response_length={len(ai_response)}, selected_personality={personality.name} (user_id={personality.user_id}), excluded_user_id={exclude_user_id}"
    )

    ai_message_data = create_ai_message_data(channel_id, ai_response, personality)
    return MessageCreate.model_validate(ai_message_data), generation_time


async def generate_and_save_ai_response(
    user_message: str, channel_id: str, db_session: Session | None = None
) -> MessageBroadcastData:
    """AI応答を生成してデータベースに保存"""
    # AI応答を生成
    ai_message_create, _ = await _generate_ai_response(user_message, channel_id, db_session)

    # セッションから切り離される前に必要な情報を取得
    message_id, user_id, user_name, user_type, content, timestamp = _extract_message_attributes(ai_message_create)

    # データベースに保存
    db_start = time.time()
    save_message_with_session_management(
        lambda session: crud.create_message(session, ai_message_create), db_session, auto_commit=(db_session is None)
    )
    db_time = time.time() - db_start
    logger.info(f"AI応答DB保存完了: db_time={db_time:.2f}s, message_id={message_id}")

    return MessageBroadcastData(
        message_id=message_id,
        channel_id=channel_id,
        user_id=user_id,
        user_name=user_name,
        user_type=user_type,
        content=content,
        timestamp=timestamp,
    )


async def broadcast_ai_response(message_data: MessageBroadcastData) -> None:
    """AI応答をブロードキャスト"""
    broadcast_message = create_broadcast_message(message_data)
    broadcast_start = time.time()
    await manager.broadcast(json.dumps(broadcast_message))
    broadcast_time = time.time() - broadcast_start
    logger.info(
        f"AI応答ブロードキャスト完了: broadcast_time={broadcast_time:.2f}s, message_id={message_data.message_id}"
    )


async def handle_ai_error(channel_id: str, error: Exception, error_time: float) -> None:
    """AI応答エラー時の処理"""
    logger.error(f"AI応答エラー: {str(error)}, error_time={error_time:.2f}s")

    # エラー時のフォールバック応答
    fallback_message_data = {
        "id": generate_ai_error_message_id(channel_id),
        "channel_id": channel_id,
        "user_id": GeminiAPIClient.FALLBACK_AI_ID,
        "user_name": GeminiAPIClient.FALLBACK_AI_NAME,
        "user_type": "ai",
        "content": GeminiAPIClient.FALLBACK_MESSAGE,
        "timestamp": datetime.now(JST).isoformat(),
        "is_own_message": False,
    }

    # エラーメッセージも全クライアントにブロードキャスト
    error_broadcast_message = {
        "type": "message:broadcast",
        "data": fallback_message_data,
    }

    await manager.broadcast(json.dumps(error_broadcast_message))


async def handle_ai_response(message_data: dict[str, Any] | None, db_session: Session | None = None):
    """AI応答の処理"""
    start_time = time.time()

    if not message_data or not isinstance(message_data, dict):
        return

    user_message = message_data.get("content", "")
    channel_id = message_data.get("channel_id", "")
    logger.info(f"AI応答処理開始: channel_id={channel_id}, message='{user_message[:50]}...'")

    # @AI が含まれているかチェック（大文字小文字区別なし）
    gemini_client = get_gemini_client()
    if not gemini_client.should_respond_to_message(user_message):
        logger.debug("@AI検出されず、AI応答処理をスキップ")
        return

    logger.info("@AI検出、AI応答生成を開始")
    try:
        # AI応答を生成・保存
        ai_message_data = await generate_and_save_ai_response(user_message, channel_id, db_session)

        # AI応答をブロードキャスト
        await broadcast_ai_response(ai_message_data)

        total_time = time.time() - start_time
        logger.info(f"AI応答処理完了: total_time={total_time:.2f}s, message_id={ai_message_data.message_id}")

    except Exception as e:
        error_time = time.time() - start_time
        await handle_ai_error(channel_id, e, error_time)
