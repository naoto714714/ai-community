"""Discord Webhook送信ユーティリティ"""

import logging
import os

import httpx

logger = logging.getLogger(__name__)


class DiscordWebhookSender:
    """Discord Webhook送信クラス"""

    def __init__(self) -> None:
        """初期化"""
        self.webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        if not self.webhook_url:
            logger.warning("DISCORD_WEBHOOK_URL環境変数が設定されていません。Discord送信機能は無効です。")

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

        # Discord送信内容: 1行目にAI名、2行目にメッセージ本文、最下部に区切り線
        discord_message = f"{ai_name}\n{message_content}\n----------"

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
                    logger.info(f"Discord Webhook送信成功: {ai_name}")
                    return True
                else:
                    logger.error(f"Discord Webhook送信失敗: {response.status_code} - {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Discord Webhook送信エラー: {str(e)}")
            return False


# グローバルインスタンス
discord_sender = DiscordWebhookSender()
