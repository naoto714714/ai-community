"""Discord Webhook送信ユーティリティ"""

import logging
import os
import time

import httpx

logger = logging.getLogger(__name__)


class DiscordWebhookSender:
    """Discord Webhook送信クラス"""

    # Discord API制約
    MAX_MESSAGE_LENGTH = 2000
    RATE_LIMIT_MESSAGES = 30
    RATE_LIMIT_WINDOW = 60  # 60秒

    def __init__(self) -> None:
        """初期化"""
        self.webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        self.message_timestamps: list[float] = []
        if not self.webhook_url:
            logger.warning("DISCORD_WEBHOOK_URL環境変数が設定されていません。Discord送信機能は無効です。")

    def _escape_discord_markdown(self, text: str) -> str:
        """Discord Markdownの特殊文字をエスケープ"""
        special_chars = ["*", "_", "`", "~", "|", "\\", ">"]
        for char in special_chars:
            text = text.replace(char, f"\\{char}")
        return text

    def _truncate_message(self, message: str, max_length: int = MAX_MESSAGE_LENGTH) -> str:
        """メッセージを指定長さに切り詰める"""
        if len(message) <= max_length:
            return message

        # 区切り線とマージンを考慮して切り詰める
        margin = 20  # "...(省略)" + マージン
        truncated = message[: max_length - margin] + "...(省略)"
        logger.warning(f"Discord メッセージが長すぎるため切り詰めました: {len(message)} -> {len(truncated)} 文字")
        return truncated

    def _check_rate_limit(self) -> bool:
        """レート制限チェック（30件/分）"""
        current_time = time.time()

        # 60秒以内のタイムスタンプのみを保持
        self.message_timestamps = [
            timestamp for timestamp in self.message_timestamps if current_time - timestamp < self.RATE_LIMIT_WINDOW
        ]

        # レート制限チェック
        if len(self.message_timestamps) >= self.RATE_LIMIT_MESSAGES:
            logger.warning(
                f"Discord API レート制限に達しました: {len(self.message_timestamps)}件/{self.RATE_LIMIT_WINDOW}秒"
            )
            return False

        # 現在のタイムスタンプを追加
        self.message_timestamps.append(current_time)
        return True

    async def send_ai_message(self, ai_name: str, message_content: str) -> bool:
        """AIメッセージをDiscordに送信

        Args:
            ai_name: AI人格名（例: "レン", "ミナ"）
            message_content: メッセージ本文

        Returns:
            送信成功: True, 失敗: False

        """
        if not self.webhook_url:
            logger.debug("Discord Webhook URLが未設定のため送信をスキップ")
            return False

        # レート制限チェック
        if not self._check_rate_limit():
            logger.warning("Discord レート制限のため送信をスキップ")
            return False

        # Markdown特殊文字をエスケープ
        escaped_ai_name = self._escape_discord_markdown(ai_name)
        escaped_message_content = self._escape_discord_markdown(message_content)

        # Discord送信内容: 1行目にAI名、2行目にメッセージ本文、最下部に区切り線
        discord_message = f"{escaped_ai_name}\n{escaped_message_content}\n{'-' * 20}"

        # メッセージ長制限チェック
        discord_message = self._truncate_message(discord_message)

        payload = {"content": discord_message}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0,
                )

                if response.status_code == 204:
                    logger.info(f"Discord Webhook送信成功: {escaped_ai_name}")
                    return True

                logger.error(f"Discord Webhook送信失敗: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Discord Webhook送信エラー: {e!s}")
            return False


# グローバルインスタンス
discord_sender = DiscordWebhookSender()
