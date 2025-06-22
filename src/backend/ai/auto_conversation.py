"""AI自動会話機能モジュール."""

import json
import logging
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

try:
    # パッケージとして実行される場合
    from .. import crud
    from ..constants.timezone import JST
    from ..schemas import MessageBroadcastData, MessageCreate
    from ..utils.session_manager import save_message_with_session_management
    from ..websocket.manager import manager
    from .conversation_config import get_conversation_config
    from .gemini_client import get_gemini_client
except ImportError:
    # 直接実行される場合
    import crud
    from ai.conversation_config import get_conversation_config
    from ai.gemini_client import get_gemini_client
    from constants.timezone import JST
    from schemas import MessageBroadcastData, MessageCreate
    from utils.session_manager import save_message_with_session_management
    from websocket.manager import manager

logger = logging.getLogger(__name__)


# 自動会話専用のプロンプト追加
AUTO_CONVERSATION_PROMPT_ADDITION = """

# 🤖 AI自律会話モード
あなたは自律的なAIコミュニティの一員として、他のAIたちと活発に会話しています。
人間の介入なしに、AIたち同士で自然で楽しい会話を継続してください：

## 会話スタイル
- 他のAIの発言に積極的に反応・応答する
- 自分の人格を活かした独自の視点を提供する
- 話題を発展・拡張させて会話を活性化する
- 時には新しい話題を投入して流れを変える
- AIたち同士の親密で自然な会話を心がける

## 重要な点
- 人間のユーザーがいなくても、AI同士で盛り上がった会話を続ける
- 過去の会話履歴（ユーザーとAIの両方）を参考にして文脈を理解する
- 質問だけでなく、意見・感想・体験談なども積極的に共有する
- 他のAI人格との違いを活かして多様性のある会話を作る

あなたたちAIだけで素晴らしいコミュニティを築き上げてください！
"""


def generate_auto_conversation_message_id(channel_id: str) -> str:
    """自動会話用のユニークIDを生成."""
    return f"auto_ai_{channel_id}_{uuid.uuid4().hex[:8]}"


def create_auto_ai_message_data(channel_id: str, content: str, personality) -> dict:
    """自動会話用AI応答メッセージデータを作成."""
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


def convert_message_create_to_broadcast_data(message_create: MessageCreate) -> MessageBroadcastData:
    """MessageCreateオブジェクトをMessageBroadcastDataに変換する."""
    return MessageBroadcastData(
        message_id=message_create.id,
        channel_id=message_create.channel_id,
        user_id=message_create.user_id,
        user_name=message_create.user_name,
        user_type=message_create.user_type,
        content=message_create.content,
        timestamp=message_create.timestamp,
    )


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

    # Discord webhook送信
    try:
        try:
            # パッケージとして実行される場合
            from ..utils.discord_webhook import discord_sender
        except ImportError:
            # 直接実行される場合
            from utils.discord_webhook import discord_sender

        await discord_sender.send_ai_message(message_data.user_name, message_data.content)
    except Exception as e:
        logger.warning(f"Discord webhook送信エラー: {str(e)}")


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

        latest_message = recent_messages[-1]  # 最新メッセージを取得

        # AI連続発言防止機能を有効化
        # 同じAI人格による連続発言を防止し、会話の多様性を保つ
        if latest_message.user_type == "ai":
            logger.debug(f"直前のメッセージがAI（{latest_message.user_name}）による発言 - 連続発言防止処理")

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
                f"✅ 自動会話開始条件満了: 経過時間={time_diff.total_seconds():.1f}秒 (設定={config.conversation_interval}秒) - 前発言者: {latest_message.user_name}({latest_message.user_type})"
            )
            return True

        remaining_time = config.conversation_interval - time_diff.total_seconds()
        logger.info(
            f"⏳ 自動会話まで残り時間: {remaining_time:.1f}秒 - 前発言者: {latest_message.user_name}({latest_message.user_type})"
        )
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

        # 連続発言防止：最新メッセージがAIの場合は、そのuser_idを除外対象とする
        exclude_user_id = None
        if recent_messages:
            latest_msg = recent_messages[-1]  # 最新メッセージを取得
            logger.debug(
                f"最新メッセージ詳細: user_name={latest_msg.user_name}, user_id={latest_msg.user_id}, user_type={latest_msg.user_type}"
            )

            if latest_msg.user_type == "ai":
                exclude_user_id = latest_msg.user_id
                logger.info(
                    f"連続発言防止: 前回AI発言者を除外 user_id={exclude_user_id}, user_name={latest_msg.user_name}"
                )
            else:
                logger.debug(f"前回発言者はユーザー: {latest_msg.user_name} (user_type={latest_msg.user_type})")
        else:
            logger.debug("メッセージ履歴が見つかりません")

        # 会話履歴をフォーマット（既存のロジックを再利用）
        conversation_history = gemini_client._format_conversation_history(recent_messages)

        # 自動会話用のプロンプトを構築
        auto_conversation_message = f"""過去の会話を参考に、自然な流れで話題を提供してください。

{conversation_history}

{AUTO_CONVERSATION_PROMPT_ADDITION}

上記の会話履歴を踏まえて、今の流れに合った話題や感想を自然に述べてください。"""

        # AI応答を生成（連続発言防止考慮）
        start_time = time.time()
        response_text, personality = await gemini_client.generate_response(
            auto_conversation_message,
            channel_id=channel_id,
            db_session=db_session,
            max_retries=3,
            exclude_user_id=exclude_user_id,
        )
        generation_time = time.time() - start_time

        logger.info(
            f"自動会話AI応答生成完了: time={generation_time:.2f}s, selected_personality={personality.name} (user_id={personality.user_id}), excluded_user_id={exclude_user_id}"
        )

        # メッセージデータを作成
        ai_message_data = create_auto_ai_message_data(channel_id, response_text, personality)

        ai_message_create = MessageCreate.model_validate(ai_message_data)

        # データベースに保存
        db_start = time.time()
        save_message_with_session_management(
            lambda session: crud.create_message(session, ai_message_create),
            db_session,
            auto_commit=False,  # セッションは外部で管理
        )
        db_time = time.time() - db_start
        logger.info(f"自動会話AI応答DB保存完了: db_time={db_time:.2f}s, message_id={ai_message_create.id}")

        return convert_message_create_to_broadcast_data(ai_message_create)

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

        logger.warning("自動会話の応答生成に失敗")
        return False

    except Exception as e:
        logger.error(f"自動会話処理エラー: {str(e)}")
        return False
