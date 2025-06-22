"""AI自動会話機能モジュール."""

import json
import logging
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

try:
    # パッケージとして実行される場合
    from .. import crud
    from ..schemas import MessageCreate
    from ..utils.session_manager import save_message_with_session_management
    from ..websocket.manager import manager
    from .conversation_config import get_conversation_config
    from .gemini_client import get_gemini_client
except ImportError:
    # 直接実行される場合
    import crud
    from ai.conversation_config import get_conversation_config
    from ai.gemini_client import get_gemini_client
    from schemas import MessageCreate
    from utils.session_manager import save_message_with_session_management
    from websocket.manager import manager

logger = logging.getLogger(__name__)


@dataclass
class MessageBroadcastData:
    """ブロードキャスト用メッセージデータ（循環インポート回避のため再定義）"""

    message_id: str
    channel_id: str
    user_id: str
    user_name: str
    user_type: str
    content: str
    timestamp: datetime


# 自動会話専用のプロンプト追加
AUTO_CONVERSATION_PROMPT_ADDITION = """

# 自動会話モード
あなたは今、会話が途切れたタイミングで自発的に話題を提供しています。
過去の会話履歴を参考にしながら、以下のように振る舞ってください：

- 自然に会話を続ける話題を提供する
- 過去の会話の流れを意識して関連する内容を話す
- 新しい視点や興味深い情報を提供する
- 質問形式ではなく、自分の意見や感想を積極的に述べる
- 会話が盛り上がるような内容を心がける

過去の会話の流れから自然に発展する話題で、コミュニティを活性化させてください。
"""


def generate_auto_conversation_message_id(channel_id: str) -> str:
    """自動会話用のユニークIDを生成."""
    return f"auto_ai_{channel_id}_{uuid.uuid4().hex[:8]}"


def create_auto_ai_message_data(channel_id: str, content: str, personality) -> dict:
    """自動会話用AI応答メッセージデータを作成."""
    # タイムゾーン定数（JST）
    from datetime import timedelta, timezone

    JST = timezone(timedelta(hours=9))

    return {
        "id": generate_auto_conversation_message_id(channel_id),
        "channel_id": channel_id,
        "user_id": personality.user_id,
        "user_name": personality.name,
        "user_type": "ai",
        "content": content,
        "timestamp": datetime.now(JST).isoformat(),
        "is_own_message": False,
    }


async def broadcast_auto_ai_response(message_data: MessageBroadcastData) -> None:
    """自動会話AI応答をブロードキャスト."""
    broadcast_message = {
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

    broadcast_start = time.time()
    await manager.broadcast(json.dumps(broadcast_message))
    broadcast_time = time.time() - broadcast_start
    logger.info(
        f"自動会話AI応答ブロードキャスト完了: broadcast_time={broadcast_time:.2f}s, message_id={message_data.message_id}"
    )


def should_start_auto_conversation(channel_id: str, db_session: Session) -> bool:
    """自動会話を開始すべきかどうかを判定."""
    config = get_conversation_config()

    # 機能が無効の場合
    if not config.enabled:
        logger.debug("自動会話機能が無効")
        return False

    # 対象チャンネル以外の場合
    if channel_id != config.target_channel_id:
        logger.debug(f"対象外のチャンネル: {channel_id}")
        return False

    try:
        # 最新メッセージを1件取得
        recent_messages = crud.get_recent_channel_messages(db_session, channel_id, limit=1)

        if not recent_messages:
            logger.debug("メッセージ履歴が存在しない")
            return False

        latest_message = recent_messages[0]

        # 直前のメッセージがAIの場合は発言しない（連続発言防止）
        if latest_message.user_type == "ai":
            logger.debug("直前のメッセージがAIのため、自動会話をスキップ")
            return False

        # 最後のメッセージからの経過時間をチェック
        now = datetime.now(UTC)
        # データベースのcreated_atがoffset-naiveの場合、UTCとして扱う
        if latest_message.created_at.tzinfo is None:
            latest_message_time = latest_message.created_at.replace(tzinfo=UTC)
        else:
            latest_message_time = latest_message.created_at

        time_diff = now - latest_message_time

        if time_diff.total_seconds() >= config.conversation_interval:
            logger.info(
                f"自動会話開始条件満了: 経過時間={time_diff.total_seconds():.1f}秒 (設定={config.conversation_interval}秒)"
            )
            return True
        else:
            remaining_time = config.conversation_interval - time_diff.total_seconds()
            logger.debug(f"自動会話まで残り時間: {remaining_time:.1f}秒")
            return False

    except Exception as e:
        logger.error(f"自動会話判定でエラー: {str(e)}")
        return False


async def generate_auto_conversation_response(channel_id: str, db_session: Session) -> MessageBroadcastData | None:
    """自動会話でのAI応答を生成・保存."""
    try:
        config = get_conversation_config()
        gemini_client = get_gemini_client()

        # 過去の会話履歴を取得
        recent_messages = crud.get_recent_channel_messages(db_session, channel_id, config.history_limit)

        # 会話履歴をフォーマット（既存のロジックを再利用）
        conversation_history = gemini_client._format_conversation_history(recent_messages)

        # 自動会話用のプロンプトを構築
        auto_conversation_message = f"""過去の会話を参考に、自然な流れで話題を提供してください。

{conversation_history}

{AUTO_CONVERSATION_PROMPT_ADDITION}

上記の会話履歴を踏まえて、今の流れに合った話題や感想を自然に述べてください。"""

        # AI応答を生成（既存のロジックを再利用）
        start_time = time.time()
        response_text, personality = await gemini_client.generate_response(
            auto_conversation_message, channel_id=channel_id, db_session=db_session, max_retries=3
        )
        generation_time = time.time() - start_time

        logger.info(f"自動会話AI応答生成完了: time={generation_time:.2f}s, personality={personality.name}")

        # メッセージデータを作成
        ai_message_data = create_auto_ai_message_data(channel_id, response_text, personality)

        ai_message_create = MessageCreate.model_validate(ai_message_data)

        # セッションから切り離される前に必要な情報を取得
        message_id = ai_message_create.id
        user_id = ai_message_create.user_id
        user_name = ai_message_create.user_name
        user_type = ai_message_create.user_type
        content = ai_message_create.content
        timestamp = ai_message_create.timestamp

        # データベースに保存
        db_start = time.time()
        save_message_with_session_management(
            lambda session: crud.create_message(session, ai_message_create),
            db_session,
            auto_commit=False,  # セッションは外部で管理
        )
        db_time = time.time() - db_start
        logger.info(f"自動会話AI応答DB保存完了: db_time={db_time:.2f}s, message_id={message_id}")

        return MessageBroadcastData(
            message_id=message_id,
            channel_id=channel_id,
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            content=content,
            timestamp=timestamp,
        )

    except Exception as e:
        logger.error(f"自動会話AI応答生成エラー: {str(e)}")
        return None


async def handle_auto_conversation_check(channel_id: str, db_session: Session) -> bool:
    """自動会話のチェック・実行を行う.

    Returns:
        自動会話が実行された場合True
    """
    try:
        # 自動会話を開始すべきかチェック
        if not should_start_auto_conversation(channel_id, db_session):
            return False

        logger.info(f"自動会話を開始: channel_id={channel_id}")

        # AI応答を生成・保存
        message_data = await generate_auto_conversation_response(channel_id, db_session)

        if message_data:
            # AI応答をブロードキャスト
            await broadcast_auto_ai_response(message_data)
            logger.info(f"自動会話完了: message_id={message_data.message_id}")
            return True
        else:
            logger.warning("自動会話の応答生成に失敗")
            return False

    except Exception as e:
        logger.error(f"自動会話処理エラー: {str(e)}")
        return False
