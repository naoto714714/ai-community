"""自動会話機能の設定管理モジュール."""

import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConversationConfig:
    """自動会話機能の設定."""

    # 自動会話の間隔（秒）
    conversation_interval: int = 60  # デフォルト1分

    # 対象チャンネルID（雑談チャンネル）
    target_channel_id: str = "1"

    # 会話履歴の参照件数
    history_limit: int = 10

    # 自動会話機能の有効/無効
    enabled: bool = True


def load_conversation_config() -> ConversationConfig:
    """環境変数から設定を読み込んで ConversationConfig を作成."""
    config = ConversationConfig()

    # 環境変数から間隔を取得（分単位で指定、秒に変換）
    interval_minutes = os.getenv("AI_CONVERSATION_INTERVAL_MINUTES")
    if interval_minutes:
        try:
            minutes_value = int(interval_minutes)
            # 負の値や0を拒否
            if minutes_value <= 0:
                logger.error(
                    f"無効な間隔設定（正の値が必要）: {interval_minutes}分, デフォルト値{config.conversation_interval // 60}分を使用"
                )
            # 範囲チェック（最小30秒、最大24時間）
            elif minutes_value < 0.5 or minutes_value > 1440:
                logger.error(
                    f"間隔設定が範囲外（0.5-1440分）: {interval_minutes}分, デフォルト値{config.conversation_interval // 60}分を使用"
                )
            else:
                config.conversation_interval = minutes_value * 60
                logger.info(f"自動会話間隔を環境変数から設定: {interval_minutes}分 ({config.conversation_interval}秒)")
        except ValueError:
            logger.error(
                f"無効な間隔設定（数値変換エラー）: {interval_minutes}, デフォルト値{config.conversation_interval // 60}分を使用"
            )

    # 環境変数から対象チャンネルIDを取得
    target_channel = os.getenv("AI_CONVERSATION_TARGET_CHANNEL")
    if target_channel:
        # チャンネルIDの形式検証
        if not _validate_channel_id(target_channel):
            logger.error(f"無効なチャンネルID形式: {target_channel}, デフォルト値{config.target_channel_id}を使用")
        else:
            config.target_channel_id = target_channel
            logger.info(f"対象チャンネルIDを環境変数から設定: {target_channel}")

    # 環境変数から有効/無効を取得
    enabled = os.getenv("AI_CONVERSATION_ENABLED", "true").lower()
    config.enabled = enabled in ("true", "1", "yes", "on")
    logger.info(f"自動会話機能: {'有効' if config.enabled else '無効'}")

    logger.info(
        f"自動会話設定読み込み完了: interval={config.conversation_interval}s, channel={config.target_channel_id}"
    )
    return config


def _validate_channel_id(channel_id: str) -> bool:
    """チャンネルIDの形式を検証."""
    # 空文字列チェック
    if not channel_id or not channel_id.strip():
        return False

    # 長さチェック（1-50文字）
    if len(channel_id) < 1 or len(channel_id) > 50:
        return False

    # 数字のみまたは英数字とハイフン、アンダースコアのパターンをチェック
    # チャンネルIDは通常数字または英数字の組み合わせ
    if not channel_id.replace("-", "").replace("_", "").isalnum():
        return False

    return True


# グローバル設定インスタンス
_config: ConversationConfig | None = None


def get_conversation_config() -> ConversationConfig:
    """設定のシングルトンインスタンスを取得."""
    global _config
    if _config is None:
        _config = load_conversation_config()
    return _config


def reload_conversation_config() -> ConversationConfig:
    """設定を再読み込み."""
    global _config
    _config = load_conversation_config()
    return _config
